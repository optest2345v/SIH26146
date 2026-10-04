# SIH26146 — Architecture

## Current architecture status

`TO ASSESS AGAINST REPOSITORY`

This document is a living design record. The Master Prompt contains the project-wide requirements; this file should describe the architecture that is actually agreed for the current implementation.

## Target logical architecture

```text
Data Sources
    ↓
Ingestion
    ↓
Validation / Normalization
    ↓
Correlation Engine
    ↓
Entity / Transaction Graph
    ↓
Feature Engineering
    ↓
AI/ML Detection
    ↓
Evidence Fusion / Explainability
    ↓
Alert Ranking
    ↓
Investigation API / Local Service
    ↓
Dashboard / Link Analysis
```

## Recommended prototype decomposition

### 1. Ingestion layer

Responsibilities:
- read CSV/JSON/XML;
- validate syntax;
- normalize fields;
- attach source record IDs;
- produce ingestion statistics.

### 2. Data layer

Recommended local options: SQLite, DuckDB, Parquet, or another embedded/local store depending on measured workload.

### 3. Correlation layer

Responsibilities:
- exact TXID matching;
- temporal association;
- repeated-observation correlation;
- correlation confidence;
- evidence provenance.

### 4. Graph layer

Responsibilities:
- IP nodes;
- transaction nodes;
- wallet/address nodes;
- explicit relationship semantics;
- graph queries and neighborhoods.

### 5. Feature layer

Responsibilities:
- behavioral features;
- temporal features;
- graph features;
- network features;
- reproducible feature versioning.

### 6. ML layer

Recommended baseline: a practical supervised model plus anomaly detection, provided the data supports it. Exact algorithms must be recorded in `10-decisions.md` after evaluation.

### 7. Explanation layer

Responsibilities:
- model feature contribution;
- graph evidence;
- temporal evidence;
- network/correlation evidence.

### 8. Alert layer

Responsibilities:
- ranking;
- confidence separation;
- evidence summary;
- alert IDs;
- provenance.

### 9. UI layer

Responsibilities:
- overview;
- alerts;
- investigation view;
- graph exploration;
- timeline;
- evidence view;
- export.

## Offline architecture principles

- no runtime-required cloud service;
- no required remote AI inference;
- no required online Geo-IP lookup;
- package local model and database assets;
- provide an explicit offline test procedure.

## Architecture decision rule

Do not introduce a graph database, microservice architecture, GNN, real-time streaming stack, or other heavyweight technology unless it demonstrably improves a required capability and can be validated within the project scope.
