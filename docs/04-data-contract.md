# SIH26146 — Data Contract

## Purpose

Define the normalized schema that all ingestion formats map into.

## Required input fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| timestamp | datetime/string→normalized datetime | Yes | Normalize consistently; preserve original source value |
| src_ip | string/IP | Yes | Validate syntax; distinguish public/private/reserved |
| dst_ip | string/IP | Yes | Validate syntax |
| src_port | integer | Yes | Validate valid port range |
| dst_port | integer | Yes | Validate valid port range |
| txid | string | Yes where transaction record exists | Normalize identifier format |
| input_addresses | array[string] | Yes where applicable | Preserve order if source semantics require it |
| output_addresses | array[string] | Yes where applicable | Preserve order if source semantics require it |
| input_amounts | array[number] | Yes where applicable | Must align with source semantics |
| output_amounts | array[number] | Yes where applicable | Must align with source semantics |
| geo_country | string | Yes/derived where available | May be unknown |
| ASN | string/integer | Yes/derived where available | May be unknown |
| fee | number | Expected when supplied | Keep nullable |
| script_type | string | Expected when supplied | Keep nullable |

## Recommended internal metadata

These are project fields rather than sponsor fields:

- `source_file_id`
- `source_row_id`
- `schema_version`
- `validation_status`
- `ingestion_run_id`
- `raw_timestamp`
- `timestamp_normalization_status`

## Missing values

Never silently replace unknown values with semantically meaningful defaults.

Recommended markers:

- `null` / `unknown` for genuinely missing information;
- explicit validation status for invalid values;
- explicit `not_applicable` where the field does not apply.

## Array consistency

Where a source format implies a one-to-one relationship between `input_addresses` and `input_amounts`, or `output_addresses` and `output_amounts`, mismatches must be surfaced and not silently truncated.

## Timestamp policy

Define one internal canonical representation before analytical processing. Preserve the original source value for auditability.

## Schema versioning

Every normalized record should be traceable to the schema version used to interpret it.

## Data-quality categories

- `VALID`
- `INVALID`
- `INCOMPLETE`
- `AMBIGUOUS`
- `DUPLICATE`
- `QUARANTINED`

## Provenance

Every record used to produce an alert should remain traceable to its source record(s).
