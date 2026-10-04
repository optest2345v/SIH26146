"""
SIH26146 — Unified Ingestion Pipeline
Coordinates CSV, JSON, and XML loaders, runs validation, aggregates metrics.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter
from src.models.schema import NormalizedRecord, ValidationStatus, ValidationSummary
from src.ingestion.csv_loader import load_csv
from src.ingestion.json_loader import load_json
from src.ingestion.xml_loader import load_xml


def ingest_file(file_path: str | Path, format_hint: Optional[str] = None) -> Tuple[List[NormalizedRecord], ValidationSummary]:
    """
    Ingests a single file (CSV, JSON, or XML), auto-detecting extension if format_hint is omitted.
    Returns parsed NormalizedRecords and a ValidationSummary.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = (format_hint or path.suffix).lower().lstrip(".")

    if ext in ("csv", "tsv", "txt"):
        records = load_csv(path)
    elif ext in ("json", "jsonl", "ndjson"):
        records = load_json(path)
    elif ext in ("xml",):
        records = load_xml(path)
    else:
        raise ValueError(f"Unsupported file format: '.{ext}'. Supported formats: CSV, JSON, XML.")

    # Calculate summary
    summary = generate_validation_summary(records, [path.name])
    return records, summary


def ingest_records_from_multiple_sources(file_paths: List[str | Path]) -> Tuple[List[NormalizedRecord], ValidationSummary]:
    """Ingests multiple files across heterogeneous formats into one unified normalized dataset."""
    all_records: List[NormalizedRecord] = []
    source_names: List[str] = []

    for fp in file_paths:
        path = Path(fp)
        if path.exists():
            records, _ = ingest_file(path)
            all_records.extend(records)
            source_names.append(path.name)

    summary = generate_validation_summary(all_records, source_names)
    return all_records, summary


def generate_validation_summary(records: List[NormalizedRecord], source_files: List[str]) -> ValidationSummary:
    """Computes an audit summary for validation reporting."""
    total = len(records)
    valid = sum(1 for r in records if r.validation_status == ValidationStatus.VALID)
    invalid = sum(1 for r in records if r.validation_status == ValidationStatus.INVALID)
    incomplete = sum(1 for r in records if r.validation_status == ValidationStatus.INCOMPLETE)
    quarantined = sum(1 for r in records if r.validation_status == ValidationStatus.QUARANTINED)

    error_counter: Counter[str] = Counter()
    for r in records:
        for err in r.validation_errors:
            # Group errors by category prefix
            category = err.split(":")[0].strip()
            error_counter[category] += 1

    return ValidationSummary(
        total_records=total,
        valid_records=valid,
        invalid_records=invalid,
        incomplete_records=incomplete,
        quarantined_records=quarantined,
        error_counts_by_type=dict(error_counter),
        source_files=source_files,
    )
