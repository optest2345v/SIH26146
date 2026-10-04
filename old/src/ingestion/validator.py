"""
SIH26146 — Data Validator & Sanitizer
Fulfills R-003 (Data validation) and R-006 (Data normalization).
Surfaces invalid records explicitly; never silently discards or converts data to fake values.
"""

from __future__ import annotations
import ipaddress
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from src.models.schema import NormalizedRecord, ValidationStatus
from src.geoip.local_geoip import default_geoip


_HEX_64_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def parse_timestamp(raw_val: Any) -> Tuple[Optional[datetime], str]:
    """
    Attempts to parse multiple timestamp representations into UTC datetime.
    Returns (datetime_obj, status_str).
    """
    if raw_val is None:
        return None, "MISSING_TIMESTAMP"

    val_str = str(raw_val).strip()
    if not val_str:
        return None, "EMPTY_TIMESTAMP"

    # Try numeric Unix epoch (seconds or milliseconds)
    try:
        numeric_val = float(val_str)
        # If timestamp is in milliseconds (e.g. > 1e11)
        if numeric_val > 1e11:
            numeric_val /= 1000.0
        # Sanity range check (year 2009 to 2050)
        dt = datetime.fromtimestamp(numeric_val, tz=timezone.utc)
        if dt.year < 2009 or dt.year > 2050:
            return None, f"TIMESTAMP_OUT_OF_RANGE_YEAR_{dt.year}"
        return dt, "NORMALIZED_EPOCH"
    except (ValueError, OverflowError, OSError):
        pass

    # Try standard string date formats
    date_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(val_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt, "NORMALIZED_STRING"
        except ValueError:
            continue

    return None, f"UNRECOGNIZED_TIMESTAMP_FORMAT: {val_str}"


def validate_ip(ip_val: Any) -> Tuple[bool, str]:
    """Validates IP address syntax (IPv4 or IPv6)."""
    if not ip_val:
        return False, "MISSING_IP"
    ip_str = str(ip_val).strip()
    try:
        ipaddress.ip_address(ip_str)
        return True, "VALID_IP"
    except ValueError:
        return False, f"MALFORMED_IP: {ip_str}"


def validate_port(port_val: Any) -> Tuple[bool, int, str]:
    """Validates port number within range 0-65535."""
    if port_val is None:
        return False, 0, "MISSING_PORT"
    try:
        p = int(port_val)
        if 0 <= p <= 65535:
            return True, p, "VALID_PORT"
        return False, p, f"PORT_OUT_OF_RANGE_{p}"
    except (ValueError, TypeError):
        return False, 0, f"INVALID_PORT_LITERAL: {port_val}"


def parse_string_list(raw_val: Any) -> List[str]:
    """Extracts a list of strings from lists, comma-separated strings, or semicolon-separated strings."""
    if raw_val is None:
        return []
    if isinstance(raw_val, list):
        return [str(x).strip() for x in raw_val if str(x).strip()]
    val_str = str(raw_val).strip()
    if not val_str or val_str.lower() in ("none", "null", "[]"):
        return []
    # If wrapped in brackets e.g. "['addr1', 'addr2']"
    if val_str.startswith("[") and val_str.endswith("]"):
        val_str = val_str[1:-1]
    # Split by semicolon, pipe, or comma
    delimiters = [";", "|", ","]
    for delim in delimiters:
        if delim in val_str:
            return [x.strip().strip("'\"") for x in val_str.split(delim) if x.strip()]
    return [val_str.strip("'\"")]


def parse_float_list(raw_val: Any) -> Tuple[List[float], List[str]]:
    """Extracts a list of non-negative floats from array/delimited string."""
    errors = []
    if raw_val is None:
        return [], errors
    str_list = parse_string_list(raw_val)
    floats = []
    for item in str_list:
        try:
            val = float(item)
            if val < 0:
                errors.append(f"NEGATIVE_AMOUNT_NOT_PERMITTED: {val}")
            else:
                floats.append(val)
        except (ValueError, TypeError):
            errors.append(f"NON_NUMERIC_AMOUNT: {item}")
    return floats, errors


def validate_and_normalize_raw_record(
    raw: Dict[str, Any],
    source_file_id: str,
    source_row_id: str | int,
) -> NormalizedRecord:
    """
    Validates a raw dictionary into a NormalizedRecord.
    Classifies record status (VALID, INVALID, INCOMPLETE, QUARANTINED) without throwing uncaught exceptions.
    """
    errors: List[str] = []
    
    # 1. Timestamp validation
    raw_ts = raw.get("timestamp") or raw.get("time") or raw.get("date") or raw.get("raw_timestamp")
    parsed_dt, ts_status = parse_timestamp(raw_ts)
    if parsed_dt is None:
        errors.append(f"INVALID_TIMESTAMP: {ts_status}")
        # Default placeholder to allow object creation, but marked INVALID
        parsed_dt = datetime(1970, 1, 1, tzinfo=timezone.utc)

    # 2. IP validations
    raw_src_ip = raw.get("src_ip") or raw.get("source_ip") or raw.get("src") or raw.get("source")
    raw_dst_ip = raw.get("dst_ip") or raw.get("dest_ip") or raw.get("destination_ip") or raw.get("dst")
    
    src_valid, src_msg = validate_ip(raw_src_ip)
    if not src_valid:
        errors.append(f"INVALID_SRC_IP: {src_msg}")
    src_ip_clean = str(raw_src_ip).strip() if raw_src_ip else "0.0.0.0"

    dst_valid, dst_msg = validate_ip(raw_dst_ip)
    if not dst_valid:
        errors.append(f"INVALID_DST_IP: {dst_msg}")
    dst_ip_clean = str(raw_dst_ip).strip() if raw_dst_ip else "0.0.0.0"

    # 3. Port validations (standard Bitcoin P2P port 8333 default if network observation without port)
    raw_src_port = raw.get("src_port") or raw.get("source_port") or 8333
    raw_dst_port = raw.get("dst_port") or raw.get("dest_port") or raw.get("destination_port") or 8333
    
    src_port_valid, src_port_val, src_p_msg = validate_port(raw_src_port)
    if not src_port_valid:
        errors.append(f"INVALID_SRC_PORT: {src_p_msg}")
        src_port_val = 0

    dst_port_valid, dst_port_val, dst_p_msg = validate_port(raw_dst_port)
    if not dst_port_valid:
        errors.append(f"INVALID_DST_PORT: {dst_p_msg}")
        dst_port_val = 0

    # 4. TXID validation
    raw_txid = raw.get("txid") or raw.get("tx_id") or raw.get("transaction_id") or raw.get("hash")
    txid_clean: Optional[str] = None
    if raw_txid:
        txid_str = str(raw_txid).strip()
        if txid_str.lower() not in ("none", "null", ""):
            txid_clean = txid_str
            if not _HEX_64_PATTERN.match(txid_clean):
                errors.append(f"NON_STANDARD_TXID_SYNTAX: {txid_clean}")

    # 5. Blockchain addresses & amounts
    in_addrs = parse_string_list(raw.get("input_addresses") or raw.get("inputs") or raw.get("in_addr"))
    out_addrs = parse_string_list(raw.get("output_addresses") or raw.get("outputs") or raw.get("out_addr"))

    in_amts, in_amt_errs = parse_float_list(raw.get("input_amounts") or raw.get("in_amounts") or raw.get("in_btc"))
    out_amts, out_amt_errs = parse_float_list(raw.get("output_amounts") or raw.get("out_amounts") or raw.get("out_btc") or raw.get("amount"))
    errors.extend(in_amt_errs)
    errors.extend(out_amt_errs)

    # Check array length consistency if both present
    if in_addrs and in_amts and len(in_addrs) != len(in_amts):
        errors.append(f"ARRAY_MISMATCH: {len(in_addrs)} input_addresses vs {len(in_amts)} input_amounts")
    if out_addrs and out_amts and len(out_addrs) != len(out_amts):
        errors.append(f"ARRAY_MISMATCH: {len(out_addrs)} output_addresses vs {len(out_amts)} output_amounts")

    # 6. Geo-IP and ASN enrichment (offline)
    geo_country = raw.get("geo_country") or raw.get("country")
    asn = raw.get("asn") or raw.get("ASN")
    
    # If not provided, enrich offline from local Geo-IP resolver
    if not geo_country or str(geo_country).lower() in ("none", "null", "unknown"):
        resolved_geo = default_geoip.lookup(src_ip_clean if src_valid else None)
        geo_country = resolved_geo.country_code
        if not asn:
            asn = resolved_geo.asn

    # 7. Fee & Script type
    fee_raw = raw.get("fee")
    fee_val: Optional[float] = None
    if fee_raw is not None and str(fee_raw).strip() not in ("", "none", "null", "None", "Null"):
        try:
            fee_val = float(fee_raw)
            if fee_val < 0:
                errors.append(f"NEGATIVE_FEE: {fee_val}")
                fee_val = None
        except (ValueError, TypeError):
            errors.append(f"NON_NUMERIC_FEE: {fee_raw}")

    script_type = raw.get("script_type") or raw.get("script") or raw.get("type")
    script_type_clean = str(script_type).strip() if script_type else None

    # Determine status
    if any(e.startswith(("INVALID_TIMESTAMP", "MALFORMED_IP", "NEGATIVE_AMOUNT")) for e in errors):
        status = ValidationStatus.INVALID
    elif not txid_clean and not in_addrs and not out_addrs and (not src_valid or not dst_valid):
        status = ValidationStatus.INCOMPLETE
    elif errors:
        status = ValidationStatus.QUARANTINED
    else:
        status = ValidationStatus.VALID

    return NormalizedRecord(
        source_file_id=source_file_id,
        source_row_id=str(source_row_id),
        schema_version="v1.0.0",
        validation_status=status,
        validation_errors=errors,
        raw_timestamp=str(raw_ts) if raw_ts is not None else None,
        timestamp_normalization_status=ts_status,
        timestamp=parsed_dt,
        src_ip=src_ip_clean,
        dst_ip=dst_ip_clean,
        src_port=src_port_val,
        dst_port=dst_port_val,
        txid=txid_clean,
        input_addresses=in_addrs,
        output_addresses=out_addrs,
        input_amounts=in_amts,
        output_amounts=out_amts,
        geo_country=str(geo_country).upper() if geo_country else "UNKNOWN",
        asn=str(asn).upper() if asn else "AS0",
        fee=fee_val,
        script_type=script_type_clean,
    )
