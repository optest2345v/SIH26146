"""
SIH26146 — XML Ingestion Loader
Fulfills R-001 (Bulk data ingestion) and R-004 (XML support).
"""

from __future__ import annotations
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List
from src.models.schema import NormalizedRecord, ValidationStatus
from src.ingestion.validator import validate_and_normalize_raw_record


def _xml_elem_to_dict(elem: ET.Element) -> Dict[str, Any]:
    """Helper to convert an XML record element to a flat dictionary."""
    data: Dict[str, Any] = {}
    for child in elem:
        tag = child.tag
        # If element has sub-children (like <input_addresses><address>...</address></input_addresses>)
        if len(child) > 0:
            sub_items = [sub.text.strip() for sub in child if sub.text and sub.text.strip()]
            data[tag] = sub_items
        else:
            text = child.text.strip() if child.text else ""
            data[tag] = text
    return data


def load_xml(file_path: str | Path) -> List[NormalizedRecord]:
    """
    Parses XML data files containing Bitcoin transactions/telemetry records.
    Handles <records><record>...</record></records> or <transactions><transaction>...</transaction></transactions>.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"XML file not found: {path}")

    records: List[NormalizedRecord] = []
    file_id = path.name

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as e:
        # Explicit error reporting without silently swallowing
        err_dict: Dict[str, Any] = {
            "raw_timestamp": None,
            "src_ip": "0.0.0.0",
            "dst_ip": "0.0.0.0",
            "src_port": 0,
            "dst_port": 0,
        }
        rec = validate_and_normalize_raw_record(err_dict, file_id, 1)
        rec.validation_errors.append(f"XML_SYNTAX_ERROR: {str(e)}")
        rec.validation_status = ValidationStatus.INVALID
        return [rec]

    # Find candidate repeating record elements
    candidate_elements = []
    for tag_name in ("record", "transaction", "entry", "item", "row"):
        candidate_elements = root.findall(f".//{tag_name}")
        if candidate_elements:
            break

    # If root itself has immediate children and no known tag matched
    if not candidate_elements:
        candidate_elements = list(root)

    for idx, elem in enumerate(candidate_elements, start=1):
        raw_dict = _xml_elem_to_dict(elem)
        records.append(
            validate_and_normalize_raw_record(
                raw=raw_dict,
                source_file_id=file_id,
                source_row_id=idx,
            )
        )

    return records
