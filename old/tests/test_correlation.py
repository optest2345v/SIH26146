"""
SIH26146 — Network ↔ Blockchain Correlation Test Suite
Fulfills REQ-007, docs/05-correlation-spec.md.
"""

from datetime import datetime, timezone, timedelta
from src.correlation.engine import CorrelationEngine
from src.models.schema import NormalizedRecord, ValidationStatus


def test_exact_txid_correlation():
    engine = CorrelationEngine()
    txid = "c" * 64
    rec = NormalizedRecord(
        source_file_id="test.csv",
        source_row_id="1",
        timestamp=datetime.now(timezone.utc),
        src_ip="142.250.190.46",
        dst_ip="198.51.100.1",
        src_port=45000,
        dst_port=8333,
        txid=txid,
        input_addresses=["1AddrIn"],
        output_addresses=["1AddrOut"],
        input_amounts=[1.0],
        output_amounts=[0.99],
        geo_country="US",
        asn="AS15169",
        validation_status=ValidationStatus.VALID,
    )
    correlations = engine.correlate([rec])
    assert len(correlations) == 1
    corr = correlations[0]
    assert corr.txid == txid
    assert "EXACT_TXID" in corr.match_methods
    assert corr.correlation_confidence >= 0.85
    assert len(corr.confidence_reasons) > 0


def test_temporal_proximity_correlation():
    engine = CorrelationEngine(temporal_window_seconds=30.0)
    base_time = datetime(2026, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
    shared_ip = "193.106.30.88"
    txid = "d" * 64

    # Record 1: Pure network telemetry observation from shared IP (no TXID)
    net_obs = NormalizedRecord(
        source_file_id="net.csv",
        source_row_id="1",
        timestamp=base_time,
        src_ip=shared_ip,
        dst_ip="198.51.100.10",
        src_port=52000,
        dst_port=8333,
        txid=None,
        input_addresses=[],
        output_addresses=[],
        input_amounts=[],
        output_amounts=[],
        validation_status=ValidationStatus.VALID,
    )

    # Record 2: Blockchain transaction 10 seconds later from same IP
    bc_tx = NormalizedRecord(
        source_file_id="blockchain.csv",
        source_row_id="2",
        timestamp=base_time + timedelta(seconds=10),
        src_ip=shared_ip,
        dst_ip="198.51.100.10",
        src_port=52000,
        dst_port=8333,
        txid=txid,
        input_addresses=["1AddrX"],
        output_addresses=["1AddrY"],
        input_amounts=[2.0],
        output_amounts=[1.99],
        validation_status=ValidationStatus.VALID,
    )

    correlations = engine.correlate([net_obs, bc_tx])
    # Expect temporal match
    temporal_matches = [c for c in correlations if "TEMPORAL_PROXIMITY" in c.match_methods]
    assert len(temporal_matches) >= 1
    tm = temporal_matches[0]
    assert tm.time_delta_seconds == 10.0
    assert 0.3 <= tm.correlation_confidence <= 0.8
