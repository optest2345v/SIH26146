"""
SIH26146 — JSON / JSONL Ingestion Loader
Fulfills R-001 (Bulk data ingestion) and R-003 (JSON support).
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List
from src.models.schema import NormalizedRecord
from src.ingestion.validator import validate_and_normalize_raw_record


def load_json(file_path: str | Path) -> List[NormalizedRecord]:
    """
    Loads JSON formatted data (either standard JSON array or newline-delimited JSONL).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    records: List[NormalizedRecord] = []
    file_id = path.name

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read().strip()

    if not content:
        return []

    # Attempt parsing as standard JSON document
    try:
        data = json.loads(content)
        if isinstance(data, list):
            for idx, item in enumerate(data, start=1):
                if isinstance(item, dict):
                    records.append(
                        validate_and_normalize_raw_record(
                            raw=item,
                            source_file_id=file_id,
                            source_row_id=idx,
                        )
                    )
            return records
        elif isinstance(data, dict):
            # Single object or container dict (e.g. {"records": [...]})
            items = data.get("records") or data.get("transactions") or data.get("data")
            if isinstance(items, list):
                for idx, item in enumerate(items, start=1):
                    if isinstance(item, dict):
                        records.append(
                            validate_and_normalize_raw_record(
                                raw=item,
                                source_file_id=file_id,
                                source_row_id=idx,
                            )
                        )
                return records
            else:
                # Single record dict
                records.append(
                    validate_and_normalize_raw_record(
                        raw=data,
                        source_file_id=file_id,
                        source_row_id=1,
                    )
                )
                return records
    except json.JSONDecodeError:
        pass

    # Attempt parsing line by line (JSON Lines / JSONL)
    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                records.append(
                    validate_and_normalize_raw_record(
                        raw=item,
                        source_file_id=file_id,
                        source_row_id=idx,
                    )
                )
        except json.JSONDecodeError as e:
            # Mark malformed line explicitly
            err_dict: Dict[str, Any] = {
                "raw_timestamp": None,
                "src_ip": "0.0.0.0",
                "dst_ip": "0.0.0.0",
                "src_port": 0,
                "dst_port": 0,
            }
            rec = validate_and_normalize_raw_record(err_dict, file_id, idx)
            rec.validation_errors.append(f"JSON_SYNTAX_ERROR: {str(e)}")
            rec.validation_status = rec.validation_status.INVALID
            records.append(rec)

    return records
