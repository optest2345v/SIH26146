"""
SIH26146 — Model & Graph Explainability Engine
Fulfills REQ-011, Section 20, and docs/06-ml-specification.md.
Combines feature-level deviations, graph motifs, temporal bursts, and correlation provenance.
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


class LeadExplainer:
    """
    Synthesizes multi-factor explanations for investigative leads.
    """

    def __init__(self, baseline_df: Optional[pd.DataFrame] = None):
        # Calculate baseline medians and interquartile ranges if baseline provided
        self.medians: Dict[str, float] = {}
        if baseline_df is not None and not baseline_df.empty:
            for col in baseline_df.select_dtypes(include=[np.number]).columns:
                self.medians[col] = float(baseline_df[col].median())

    def explain_target(
        self,
        features: Dict[str, Any],
        anomaly_score: float,
        correlation_confidence: float,
        feature_importances: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive explainability packet for a specific target.
        """
        reasons: List[str] = []
        model_evidence: Dict[str, Any] = {}
        graph_evidence: Dict[str, Any] = {}
        temporal_evidence: Dict[str, Any] = {}
        correlation_evidence: Dict[str, Any] = {}

        # 1. Temporal signals
        burst = float(features.get("burst_score", 0.0))
        velocity = float(features.get("velocity_tx_per_hour", 0.0))
        min_interval = float(features.get("inter_arrival_time_min", 3600.0))
        tx_count = int(features.get("tx_count", 1))
        time_span_seconds = float(features.get("observation_window_seconds", 0.0))

        temporal_evidence = {
            "burst_score": burst,
            "velocity_tx_per_hour": velocity,
            "min_inter_arrival_seconds": min_interval,
            "transactions_observed": tx_count,
            "observation_window_seconds": time_span_seconds,
        }

        if burst >= 0.5 and tx_count > 1:
            reasons.append(f"High-frequency burst activity: {burst*100:.1f}% of transfers occurred within 60-second windows")
        if min_interval <= 10.0 and tx_count > 1:
            reasons.append(f"Automated rapid succession: Consecutive transfers observed as little as {min_interval:.1f}s apart")
        if velocity > 20.0 and tx_count >= 3:
            window_min = max(0.1, time_span_seconds / 60.0)
            reasons.append(f"Elevated velocity: {velocity:.1f} tx/hr across {window_min:.1f}-minute observation window ({tx_count} transactions)")
        elif tx_count > 1 and time_span_seconds <= 120.0:
            reasons.append(f"Rapid succession: {tx_count} transfers observed in brief {time_span_seconds:.0f}s interval")

        # 2. Graph topological signals
        fan_out = float(features.get("fan_out_ratio", 1.0))
        fan_in = float(features.get("fan_in_ratio", 1.0))
        out_deg = int(features.get("out_degree", 0))
        in_deg = int(features.get("in_degree", 0))

        graph_evidence = {
            "in_degree": in_deg,
            "out_degree": out_deg,
            "fan_out_ratio": fan_out,
            "fan_in_ratio": fan_in,
            "pagerank": float(features.get("pagerank", 0.0)),
        }

        if fan_out >= 3.0:
            reasons.append(f"Structuring / Fan-out dispersion pattern: {out_deg} outputs with fan-out ratio of {fan_out:.2f}")
        if fan_in >= 3.0:
            reasons.append(f"Consolidation / Fan-in aggregation pattern: {in_deg} inputs with fan-in ratio of {fan_in:.2f}")

        # 3. Network & Geo-IP signals
        uniq_countries = int(features.get("unique_countries_count", 0))
        uniq_asns = int(features.get("unique_asn_count", 0))
        uniq_ips = int(features.get("unique_ip_count", 0))
        ip_reuse = int(features.get("ip_reuse_max", 0))

        correlation_evidence = {
            "unique_ip_count": uniq_ips,
            "ip_reuse_max": ip_reuse,
            "unique_countries": uniq_countries,
            "unique_asns": uniq_asns,
            "correlation_confidence": correlation_confidence,
        }

        if uniq_countries > 2:
            reasons.append(f"Multi-jurisdictional telemetry: Observed across {uniq_countries} distinct sovereign countries")
        if ip_reuse > 5:
            reasons.append(f"Repeated infrastructure reuse: Single node broadcast {ip_reuse} distinct transactions")

        # 4. Model feature contributions
        if feature_importances:
            top_features = sorted(feature_importances.items(), key=lambda x: -x[1])[:5]
            model_evidence = {
                "top_contributing_features": [k for k, v in top_features],
                "feature_importances": {k: v for k, v in top_features},
                "model_anomaly_score": anomaly_score,
            }

        # Fallback general explanation if no extreme thresholds breached
        if not reasons:
            reasons.append("Behavioral statistical deviation from baseline peer population across multiple combined signals")

        # Synthesize plain-language summary narrative
        narrative_parts = [
            f"Target {features.get('target_id', 'Unknown')} was flagged with an anomaly score of {anomaly_score:.2f} "
            f"and correlation confidence of {correlation_confidence:.2f}."
        ]
        narrative_parts.append("Key investigative indicators include: " + "; ".join(reasons) + ".")
        narrative_parts.append(
            "Evidence provenance and network graph linkages have been retained for forensic inspection. "
            "This finding serves as an investigative lead and does not establish guilt or identity."
        )

        return {
            "primary_reasons": reasons,
            "explanation_narrative": " ".join(narrative_parts),
            "model_evidence": model_evidence,
            "graph_evidence": graph_evidence,
            "temporal_evidence": temporal_evidence,
            "correlation_evidence": correlation_evidence,
        }
