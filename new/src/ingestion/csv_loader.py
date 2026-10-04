"""
SIH26146 — CSV Ingestion Loader
Fulfills R-001 (Bulk data ingestion) and R-002 (CSV support).
"""

from __future__ import annotations
import csv
from pathlib import Path
from typing import List
from src.models.schema import NormalizedRecord
from src.ingestion.validator import validate_and_normalize_raw_record


def load_csv(file_path: str | Path) -> List[NormalizedRecord]:
    """
    Reads a CSV file in bulk and normalizes records into canonical NormalizedRecord objects.
    Preserves row line indices for provenance auditability.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    records: List[NormalizedRecord] = []
    file_id = path.name

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row_idx, row in enumerate(reader, start=1):
            norm_rec = validate_and_normalize_raw_record(
                raw=row,
                source_file_id=file_id,
                source_row_id=row_idx,
            )
            records.append(norm_rec)

    return records
