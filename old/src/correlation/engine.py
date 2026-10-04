"""
SIH26146 — Network ↔ Blockchain Correlation Engine
Fulfills REQ-007, Section 7, 8, 9, and docs/05-correlation-spec.md.
Explicitly links network telemetry to blockchain activity with measured confidence and provenance.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from src.models.schema import NormalizedRecord, CorrelationRecord


class CorrelationEngine:
    """
    Correlates network observations with blockchain observations.
    Implements multi-factor evidence linking:
    - Exact TXID matching
    - Temporal proximity within configurable window
    - Repeated IP / infrastructure corroboration
    """

    def __init__(self, temporal_window_seconds: float = 60.0):
        self.temporal_window_seconds = temporal_window_seconds

    def correlate(self, records: List[NormalizedRecord]) -> List[CorrelationRecord]:
        """
        Executes correlation over a collection of normalized records.
        Records can contain pure network telemetry, pure blockchain records, or combined observations.
        """
        correlation_records: List[CorrelationRecord] = []
        
        # Index records by TXID and by IP
        txid_to_records: Dict[str, List[NormalizedRecord]] = defaultdict(list)
        ip_to_records: Dict[str, List[NormalizedRecord]] = defaultdict(list)
        
        for r in records:
            if r.txid:
                txid_to_records[r.txid].append(r)
            if r.src_ip and r.src_ip != "0.0.0.0":
                ip_to_records[r.src_ip].append(r)

        # Track IP observation frequencies across all records for corroboration boost
        ip_observation_counts = {ip: len(recs) for ip, recs in ip_to_records.items()}

        seen_correlations: set[Tuple[str, str]] = set()

        for rec in records:
            # 1. Exact TXID Correlation
            # If the record has a TXID, associate its network observation with its blockchain metadata
            if rec.txid:
                linked_wallets = list(set(rec.input_addresses + rec.output_addresses))
                ip_count = ip_observation_counts.get(rec.src_ip, 1)

                reasons: List[str] = ["Direct transaction identifier (TXID) presence in telemetry"]
                match_methods = ["EXACT_TXID"]
                matched_fields = ["txid"]
                
                # Dynamic evidence-weighted confidence for exact TXID match
                base_confidence = 0.86
                if rec.src_ip and rec.src_ip not in ("0.0.0.0", "127.0.0.1"):
                    base_confidence += 0.02
                if rec.dst_port == 8333 or rec.src_port == 8333:
                    base_confidence += 0.02
                if rec.geo_country and rec.geo_country not in ("UNKNOWN", "MALFORMED"):
                    base_confidence += 0.03
                    reasons.append(f"Enriched with localized ASN/Geo origin ({rec.geo_country} / {rec.asn})")
                if ip_count > 3:
                    base_confidence = min(0.98, base_confidence + 0.05)
                    reasons.append(f"Corroborated by repeated observations ({ip_count} events from IP {rec.src_ip})")
                    match_methods.append("REPEATED_OBSERVATION")
                base_confidence = min(0.98, base_confidence)

                corr_key = (str(rec.source_row_id), rec.txid)
                if corr_key not in seen_correlations:
                    seen_correlations.add(corr_key)
                    corr_rec = CorrelationRecord(
                        correlation_id=f"CORR-{uuid.uuid4().hex[:10].upper()}",
                        network_observation_id=f"{rec.source_file_id}#row{rec.source_row_id}",
                        txid=rec.txid,
                        wallet_references=linked_wallets,
                        match_methods=match_methods,
                        matched_fields=matched_fields,
                        time_delta_seconds=0.0,
                        correlation_confidence=round(base_confidence, 4),
                        confidence_reasons=reasons,
                        source_record_ids=[f"{rec.source_file_id}#row{rec.source_row_id}"],
                    )
                    correlation_records.append(corr_rec)

            # 2. Cross-Record Temporal Proximity Matching
            # If this record has an IP but NO TXID (pure network telemetry), or we check proximity to other transactions from same IP
            if not rec.txid and rec.src_ip and rec.src_ip != "0.0.0.0":
                # Find candidate blockchain transactions from the same IP or related IPs within time window
                same_ip_tx_records = [other for other in ip_to_records[rec.src_ip] if other.txid and other != rec]
                
                for other in same_ip_tx_records:
                    time_delta = abs((rec.timestamp - other.timestamp).total_seconds())
                    if time_delta <= self.temporal_window_seconds and other.txid:
                        corr_key = (str(rec.source_row_id), other.txid)
                        if corr_key in seen_correlations:
                            continue
                        seen_correlations.add(corr_key)

                        # Compute decayed confidence based on time delta
                        # (0 seconds delta -> 0.70 confidence, window_seconds delta -> 0.35 confidence)
                        decay = max(0.0, (1.0 - (time_delta / self.temporal_window_seconds)))
                        proximity_confidence = round(0.35 + (0.35 * decay), 4)

                        reasons = [
                            f"Temporal proximity: Network telemetry observed {time_delta:.1f}s from transaction event",
                            f"Shared network address {rec.src_ip}",
                        ]
                        match_methods = ["TEMPORAL_PROXIMITY"]
                        matched_fields = ["src_ip", "timestamp"]

                        if ip_observation_counts.get(rec.src_ip, 0) > 2:
                            match_methods.append("REPEATED_OBSERVATION")
                            reasons.append(f"Corroborating traffic activity from source subnet")
                            proximity_confidence = min(0.85, proximity_confidence + 0.1)

                        corr_rec = CorrelationRecord(
                            correlation_id=f"CORR-{uuid.uuid4().hex[:10].upper()}",
                            network_observation_id=f"{rec.source_file_id}#row{rec.source_row_id}",
                            txid=other.txid,
                            wallet_references=list(set(other.input_addresses + other.output_addresses)),
                            match_methods=match_methods,
                            matched_fields=matched_fields,
                            time_delta_seconds=round(time_delta, 2),
                            correlation_confidence=proximity_confidence,
                            confidence_reasons=reasons,
                            source_record_ids=[
                                f"{rec.source_file_id}#row{rec.source_row_id}",
                                f"{other.source_file_id}#row{other.source_row_id}",
                            ],
                        )
                        correlation_records.append(corr_rec)

        return correlation_records
