"""
SIH26146 — Ingestion & Validation Test Suite
Fulfills REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, and REQ-006.
"""

import pytest
from datetime import datetime, timezone
from src.ingestion.validator import (
    validate_and_normalize_raw_record,
    parse_timestamp,
    validate_ip,
    validate_port,
    parse_string_list,
    parse_float_list,
)
from src.ingestion.pipeline import ingest_file
from src.models.schema import ValidationStatus


def test_timestamp_parsing_epoch():
    dt, status = parse_timestamp(1786701600)  # Epoch in 2026
    assert dt is not None
    assert dt.year == 2026
    assert "EPOCH" in status


def test_timestamp_parsing_iso():
    dt, status = parse_timestamp("2026-08-15T12:30:45Z")
    assert dt is not None
    assert dt.hour == 12
    assert dt.tzinfo == timezone.utc


def test_timestamp_parsing_invalid():
    dt, status = parse_timestamp("not-a-date")
    assert dt is None
    assert "UNRECOGNIZED" in status


def test_validate_ip():
    ok, _ = validate_ip("192.168.1.1")
    assert ok is True
    ok, _ = validate_ip("2001:db8::1")
    assert ok is True
    ok, msg = validate_ip("999.999.999.999")
    assert ok is False
    assert "MALFORMED_IP" in msg


def test_validate_port():
    ok, p, _ = validate_port("8333")
    assert ok is True
    assert p == 8333
    ok, _, msg = validate_port("70000")
    assert ok is False
    assert "OUT_OF_RANGE" in msg


def test_array_parsing_and_mismatch():
    raw = {
        "timestamp": "2026-08-15T10:00:00Z",
        "src_ip": "8.8.8.8",
        "dst_ip": "1.1.1.1",
        "src_port": 50000,
        "dst_port": 8333,
        "txid": "a" * 64,
        "input_addresses": "addr1;addr2",
        "input_amounts": "1.5",  # Mismatch: 2 addresses vs 1 amount
    }
    rec = validate_and_normalize_raw_record(raw, "test.csv", 1)
    assert any("ARRAY_MISMATCH" in err for err in rec.validation_errors)
    assert rec.validation_status == ValidationStatus.QUARANTINED


def test_negative_amount_rejection():
    raw = {
        "timestamp": "2026-08-15T10:00:00Z",
        "src_ip": "8.8.8.8",
        "dst_ip": "1.1.1.1",
        "src_port": 50000,
        "dst_port": 8333,
        "txid": "b" * 64,
        "output_addresses": "addr1",
        "output_amounts": "-5.0",  # Impossible negative amount
    }
    rec = validate_and_normalize_raw_record(raw, "test.csv", 2)
    assert rec.validation_status == ValidationStatus.INVALID
    assert any("NEGATIVE_AMOUNT" in err for err in rec.validation_errors)


def test_ingest_sample_files():
    # Ingest CSV
    recs_csv, sum_csv = ingest_file("data/synthetic/transactions_sample.csv")
    assert len(recs_csv) > 0
    assert sum_csv.total_records == len(recs_csv)

    # Ingest JSON
    recs_json, sum_json = ingest_file("data/synthetic/transactions_sample.json")
    assert len(recs_json) == len(recs_csv)

    # Ingest XML
    recs_xml, sum_xml = ingest_file("data/synthetic/transactions_sample.xml")
    assert len(recs_xml) == len(recs_csv)
