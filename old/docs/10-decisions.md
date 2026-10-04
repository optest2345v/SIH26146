# SIH26146 — Architecture & Engineering Decisions

Use lightweight ADR-style records. Do not record every minor coding choice.

## ADR template

```text
ADR-ID: ADR-XXX
Title: <short decision>
Status: PROPOSED | ACCEPTED | SUPERSEDED | REJECTED
Date: YYYY-MM-DD
Authority: PROJECT | SPONSOR | RESEARCH

Context:
Why is this decision needed?

Decision:
What was chosen?

Alternatives considered:
What else was considered?

Reason:
Why was this selected?

Consequences:
What becomes easier/harder?

Affected components:
Which modules/docs/tests change?

Related requirements:
REQ-XXX, ...
```

## Initial decision records

### ADR-000 — Treat this file as the design-decision history

**Status:** ACCEPTED  
**Authority:** PROJECT

Architectural decisions that meaningfully affect the implementation should be preserved here so future AI agents do not repeatedly reconsider the same choice without context.

### ADR-001 — Offline is a first-class architecture constraint

**Status:** ACCEPTED  
**Authority:** SPONSOR → PROJECT

The critical runtime path must not require cloud APIs, remote inference, or online Geo-IP lookup.

### ADR-002 — Separate anomaly, correlation confidence, and investigative priority

**Status:** ACCEPTED  
**Authority:** PROJECT

These concepts answer different questions and should remain separately represented in the data model and UI.

### ADR-003 — Prefer the simplest sufficient model

**Status:** ACCEPTED  
**Authority:** PROJECT

A complex model must justify its added value through evaluation, explainability, offline feasibility and computational practicality.

### ADR-004 — Evidence provenance is part of the investigation result

**Status:** ACCEPTED  
**Authority:** PROJECT

Important alerts should retain enough source linkage and analysis metadata to support reproduction and inspection.

### ADR-005 — Hybrid ML Detection Pipeline (Isolation Forest + Supervised Classifier)

**Status:** ACCEPTED  
**Authority:** PROJECT

**Context:** The system must detect both unknown anomalies (unsupervised) and known forensic crime typologies like peeling chains, velocity bursts, and structuring (supervised) completely offline.  
**Decision:** Implemented an ensemble combining an unsupervised `IsolationForest` (for behavioral outlier scoring) with a supervised `RandomForestClassifier` (for forensic scenario categorization) executed via `scikit-learn`.  
**Consequences:** Enables robust scoring on unlabelled bulk data while prioritizing known illicit transaction patterns.

### ADR-006 — Standalone Zero-Dependency Offline Investigation Dashboard

**Status:** ACCEPTED  
**Authority:** PROJECT

**Context:** The UI must function in an air-gapped Linux or Windows offline setting without external CDN assets or online map dependencies.  
**Decision:** Developed a single-page dark-mode investigation workbench with pure embedded HTML5, CSS3, and dynamic SVG graph rendering served locally via FastAPI.  
**Consequences:** Zero external HTTP/CDN requests required; instantaneous load times and full interactive neighborhood exploration.

### ADR-007 — Tri-Factor Evidence Ranking (Separation of Anomaly, Confidence, Priority)

**Status:** ACCEPTED  
**Authority:** PROJECT

**Context:** Conflating anomaly with guilt or correlation confidence produces misleading forensic claims.  
**Decision:** Separated the output into three explicit metrics: Anomaly Score (how unusual is the behavior), Correlation Confidence (how strongly linked is network telemetry to blockchain records), and Investigative Priority (fused actionable score for investigator triage).  
**Consequences:** Upholds forensic safety principles and protects against false attribution.

### ADR-008 — Incremental Dynamic Topology Studio Architecture & Interactive Suite

**Status:** ACCEPTED  
**Authority:** PROJECT

**Context:** Static or full-reload graph views disrupt forensic investigation workflows when expanding counterparties or tracing transactions. The topology visualization must support smooth navigation, tactile exploration, dynamic multi-hop expansion without resetting the canvas, and actionable shortest-path fund flow tracing in strict offline environments.  
**Decision:** Implemented an interactive HTML5 Canvas engine with high-DPI retina scaling, 4 topological layouts (Physics, Fund Flow DAG, Radial Radar, and Chronological Time), dynamic incremental neighborhood expansion via `/api/graph/{id}/expand`, shortest-path fund routing via `/api/graph/path`, minimum volume threshold filtering, interactive mini-map navigation, and high-resolution evidentiary snapshot export.  
**Consequences:** Enables investigators to dynamically peel through suspect transaction hops without losing their contextual mental model, while strictly preserving zero-CDN offline air-gap guarantees.

## Future decision rule

When a major technical decision is proposed, add a new ADR rather than rewriting an old accepted decision without history.


