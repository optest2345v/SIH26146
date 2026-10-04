# SIH26146 — Requirements

## Status vocabulary

- `MANDATORY` — required by the PS or an accepted project constraint
- `RECOMMENDED` — project engineering recommendation
- `OPTIONAL` — useful but not part of the critical path
- `EXPERIMENTAL` — research/advanced extension
- `UNKNOWN` — not yet verified
- `DEPRECATED` — no longer active

## Mandatory functional requirements

| ID | Requirement | Priority | Acceptance evidence |
|---|---|---|---|
| REQ-001 | Bulk data ingestion | MANDATORY | Valid bulk dataset loads successfully |
| REQ-002 | CSV support | MANDATORY | CSV fixture passes ingestion |
| REQ-003 | JSON support | MANDATORY | JSON fixture passes ingestion |
| REQ-004 | XML support | MANDATORY | XML fixture passes ingestion |
| REQ-005 | Data validation | MANDATORY | Invalid inputs are surfaced explicitly |
| REQ-006 | Data normalization | MANDATORY | Equivalent input formats map to one internal model |
| REQ-007 | Network ↔ blockchain correlation | MANDATORY | Correlation records are produced with evidence |
| REQ-008 | Entity/transaction graph | MANDATORY | Graph can be built and inspected |
| REQ-009 | Genuine AI/ML component | MANDATORY | Local model executes on project data |
| REQ-010 | Ranked investigative alerts | MANDATORY | Alerts appear in deterministic/documented priority order |
| REQ-011 | Alert explainability | MANDATORY | Each alert contains meaningful supporting reasons |
| REQ-012 | Visualization / link analysis | MANDATORY | Investigator can inspect relevant relationships |
| REQ-013 | Offline Linux execution | MANDATORY | Core workflow succeeds with network disabled |
| REQ-014 | Local Geo-IP support | MANDATORY | Geo-IP enrichment can use a downloaded local database |
| REQ-015 | Evidence/provenance | RECOMMENDED→CORE | Important findings trace toward source records |
| REQ-016 | Human-in-the-loop interpretation | MANDATORY PRINCIPLE | UI/documentation avoids automatic guilt/identity claims |

## Non-functional requirements

### NFR-001 — Offline reliability

Core operation must not depend on runtime internet connectivity.

### NFR-002 — Reproducibility

Important analysis runs should be reproducible from the same input/configuration/model when deterministic operation is intended.

### NFR-003 — Auditability

Important findings should retain enough provenance to trace them back toward input records.

### NFR-004 — Performance

Use bulk-friendly processing and avoid unnecessary O(N²) operations. Exact performance targets must be measured rather than invented.

### NFR-005 — Explainability

A score without an understandable reason is insufficient for an investigator-facing alert.

### NFR-006 — Safety of interpretation

The system must not convert network correlation into unsupported identity claims.

## Change-control rule

Any new requirement must be tagged with source and authority before being treated as part of the specification.
