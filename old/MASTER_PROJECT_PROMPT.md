# SIH26146 — MASTER PROJECT PROMPT

## 0. PROJECT IDENTITY

You are working on:

**Problem Statement:** SIH26146  
**Title:** AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic  
**Sponsoring Organization:** National Technical Research Organisation (NTRO)  
**Category:** Software  
**Platform Requirement:** Linux  
**Execution Requirement:** Fully offline  
**Primary Domain:** Bitcoin transaction analytics, network telemetry correlation, graph analytics, AI/ML, cybersecurity/forensic intelligence

Treat this document as the project's foundational specification.

The objective is to build a complete, demonstrable, offline prototype that transforms bulk Bitcoin transaction/network metadata into **ranked, explainable investigative leads**.

The system is an **investigative intelligence and analysis tool**. It is not intended to autonomously determine criminal guilt, prove identity, or replace human investigators.

---

# 1. PROBLEM STATEMENT CONTEXT

Bitcoin's pseudonymous peer-to-peer architecture can make traditional financial monitoring difficult when illicit funds are moved, layered, fragmented, or eventually cashed out.

Potentially relevant scenarios include:

- ransomware-related payments,
- darknet-market proceeds,
- extortion-related transfers,
- laundering-related transaction patterns,
- other suspicious movement of cryptocurrency.

The project must address the difficulty of analyzing large volumes of heterogeneous data and identifying relationships that are difficult to discover through manual inspection.

The system must bring together two major evidence layers:

### Blockchain layer

Examples include:

- transaction ID (TXID),
- input wallet/address data,
- output wallet/address data,
- transaction amounts,
- fees,
- script type,
- timestamp.

### Network layer

Examples include:

- source IP,
- destination IP,
- source port,
- destination port,
- timestamp,
- TXID where available.

The central problem is therefore:

> How can bulk Bitcoin transaction and network metadata be correlated, represented, analyzed, and prioritized so that investigators can quickly identify unusual or suspicious behavioral patterns and understand the evidence behind each resulting lead?

The system must solve this as an integrated workflow rather than as an isolated machine-learning classifier.

---

# 2. PRIMARY OBJECTIVE

Build a **complete offline Bitcoin transaction/network intelligence prototype** that:

1. ingests bulk structured data;
2. validates and normalizes the data;
3. correlates network observations with blockchain observations;
4. builds an entity/transaction graph;
5. derives behavioral, temporal, network and graph features;
6. applies a genuine AI/ML detection method;
7. optionally combines multiple analytical signals;
8. generates ranked investigative leads;
9. explains why each lead was generated;
10. exposes supporting evidence and correlation context;
11. visualizes the relevant entities and relationships;
12. operates completely offline on Linux;
13. remains reproducible, auditable, testable and understandable.

The system should optimize for **investigative usefulness**, not merely ML accuracy.

---

# 3. CORE SUCCESS DEFINITION

A successful prototype must allow an evaluator to perform a workflow similar to:

```text
Load Data
    ↓
Validate / Normalize
    ↓
Correlate Network + Blockchain Evidence
    ↓
Build Entity / Transaction Graph
    ↓
Extract Behavioral / Temporal / Graph Features
    ↓
Run AI/ML Analysis
    ↓
Generate Ranked Alerts
    ↓
Explain Why Each Alert Exists
    ↓
Inspect Graph / Timeline / Supporting Evidence
    ↓
Export or Record Investigation Findings
```

The final result must not stop at:

```text
Data → ML → Suspicious
```

It must instead provide:

```text
Data
→ Correlation
→ Relationships
→ Behavior
→ Detection
→ Evidence
→ Explanation
→ Investigative Priority
```

---

# 4. AUTHORITATIVE REQUIREMENTS

The following are mandatory because they are directly derived from the SIH26146 problem statement.

## R-001 — Bulk ingestion

The system must ingest bulk Bitcoin transaction/network metadata.

Supported source formats must include:

- CSV
- JSON
- XML

The parser may support additional formats, but those three must remain supported unless the sponsor specification is changed.

---

## R-002 — Required metadata fields

The input data must support, at minimum:

- timestamp
- src_ip
- dst_ip
- src_port
- dst_port
- txid
- input_addresses[]
- output_addresses[]
- input_amounts[]
- output_amounts[]
- geo_country
- ASN

The problem statement also references:

- fee
- script_type

Treat these as expected transaction metadata and include them in the normalized model when present.

The exact original field naming used by an input file may vary. The ingestion layer must normalize equivalent external representations into one internal schema.

---

## R-003 — Data validation

The system must validate incoming records before they enter the analytical pipeline.

Validation should cover:

- missing mandatory fields,
- malformed timestamps,
- malformed IP addresses,
- invalid ports,
- malformed TXIDs,
- invalid or missing wallet/address arrays,
- mismatched array lengths where applicable,
- non-numeric transaction amounts,
- impossible negative amounts where the schema does not allow them,
- duplicate or conflicting records,
- malformed JSON/XML,
- empty datasets,
- unsupported schema versions.

Invalid records must not silently disappear.

The system should either:

1. reject them with an explicit error;
2. quarantine them;
3. or mark them with a validation status.

The ingestion process must produce a validation summary.

---

# 5. OFFICIAL DATA CONSTRAINT

The SIH problem statement specifies that participants will work with a **synthetic dataset modeled on real Bitcoin P2P/transaction fields**, and that real seized/live-intercept data will not be supplied.

Therefore:

- synthetic data is an accepted development/evaluation basis;
- the system must not pretend synthetic data is real investigative evidence;
- model performance on synthetic data must not be presented as guaranteed production performance;
- dataset generation methodology must be documented;
- known synthetic scenarios should be distinguishable from naturally occurring records when appropriate for evaluation.

If a public dataset is used for additional benchmarking, clearly distinguish:

```text
Official/SIH synthetic data
vs
Public external benchmark data
vs
Project-generated synthetic data
```

Do not merge them without documenting provenance and semantic differences.

---

# 6. GEO-IP REQUIREMENT

The project must support enrichment using an **open-source downloadable Geo-IP database**.

The solution must be designed to work without a live external lookup service at runtime.

Recommended workflow:

```text
Offline Geo-IP database
        ↓
Local lookup
        ↓
Country / ASN enrichment
        ↓
Evidence / feature generation
```

Do not make runtime execution dependent on an internet API.

The Geo-IP module must account for:

- unknown IPs,
- private/reserved IP ranges,
- malformed IPs,
- database misses,
- IPv4 and IPv6 where supported,
- approximate or stale geolocation,
- Geo-IP database version/provenance.

Geo-IP information is contextual evidence and must not automatically be interpreted as identity evidence.

---

# 7. NETWORK ↔ BLOCKCHAIN CORRELATION

This is a core requirement.

The system must correlate:

### Network observations

- source IP,
- destination IP,
- source/destination ports,
- timestamps,
- TXID where present.

with:

### Blockchain observations

- TXID,
- transaction timestamp,
- wallet/address inputs,
- wallet/address outputs,
- transaction amounts,
- fees,
- script information.

---

# 8. CORRELATION PRINCIPLES

Correlation must be explicit and reproducible.

Possible correlation evidence may include:

### Strong correlation

- exact TXID match,
- explicit observation linking a network event to a TXID,
- repeated corroborating observations.

### Moderate correlation

- close timestamp relationship,
- compatible transaction/network sequence,
- repeated network observations around the same transaction/entity,
- consistent IP/ASN patterns.

### Weak/contextual correlation

- geographic coincidence,
- shared IP,
- shared infrastructure,
- temporal proximity without a direct transaction identifier.

The system must not convert weak evidence into a definitive ownership claim.

Avoid logic equivalent to:

```text
IP = Wallet Owner
```

Instead use concepts such as:

```text
Observed association
Correlation confidence
Supporting evidence
Temporal association
Probable/common entity
```

Any entity-resolution heuristic must explicitly document its assumptions.

---

# 9. CORRELATION CONFIDENCE

The system should maintain a separate concept called **correlation confidence**.

This measures how strongly available data supports a relationship such as:

```text
IP ↔ Transaction
Transaction ↔ Wallet
Wallet ↔ Entity Cluster
```

Correlation confidence must not be presented as:

- probability of guilt,
- proof of identity,
- certainty of ownership.

If a numerical score is used, its meaning must be documented.

A preferred conceptual distinction is:

```text
Anomaly Score
    =
How unusual is this behavior?

Correlation Confidence
    =
How strongly is the evidence linked?

Investigative Priority
    =
How deserving of human review is this lead?
```

These three concepts must not be conflated.

---

# 10. ENTITY / TRANSACTION GRAPH

The system must build an entity/transaction graph linking:

- IP entities,
- wallet/address entities,
- transaction entities.

A graph representation should support relationships such as:

```text
IP ──OBSERVED──> Transaction
Transaction ──INPUT──> Wallet
Transaction ──OUTPUT──> Wallet
Wallet ──RELATED_TO──> Wallet
Transaction ──TEMPORALLY_RELATED──> Transaction
```

Additional edge types may be introduced when justified.

Each graph relationship must have a defined semantic meaning.

The graph must support investigative inspection.

---

# 11. ENTITY RESOLUTION

The system may provisionally cluster addresses into entities where justified.

Possible heuristics can include:

- common-input relationships,
- repeated transaction behavior,
- graph structure,
- shared network observations,
- temporal associations.

However:

> Entity resolution is probabilistic/heuristic and must never be presented as unquestionable identity.

For example:

```text
A + B + C
    ↓
Probable common entity
```

is acceptable.

```text
A + B + C
    ↓
Confirmed person/organization
```

is not acceptable unless independently supported by authoritative evidence that is actually available to the system.

---

# 12. GRAPH ANALYTICS

The graph layer should support useful investigative measurements where computationally practical.

Potential features include:

- degree,
- in-degree,
- out-degree,
- fan-in,
- fan-out,
- neighborhood size,
- centrality,
- PageRank,
- clustering coefficient,
- connected component size,
- path length,
- local density,
- community membership,
- graph motifs,
- repeated counterparty relationships,
- upstream/downstream exposure.

Do not add graph metrics purely to make the project appear technically complex.

Every graph metric used for detection must have a documented reason.

---

# 13. TEMPORAL ANALYSIS

Time is a first-class analytical dimension.

The system should analyze:

- transaction frequency,
- transaction velocity,
- inter-arrival time,
- burstiness,
- sudden activity increases,
- repeated activity windows,
- rapid sequential transfers,
- time gaps between related transactions,
- time between network observation and blockchain event,
- changes in behavior over time.

The dashboard should ideally allow an investigator to understand:

```text
What happened?
When did it happen?
What changed?
What happened immediately before?
What happened immediately after?
```

A time sequence should be available for significant alerts.

---

# 14. BEHAVIORAL FEATURES

Potential behavioral features include:

- number of transactions,
- total amount,
- average amount,
- median amount,
- amount variance,
- transaction frequency,
- unique counterparties,
- unique wallets,
- unique IPs,
- unique countries,
- number of ASNs,
- fan-in ratio,
- fan-out ratio,
- burstiness,
- repeated transfers,
- transaction chain length,
- graph degree,
- centrality,
- cluster size,
- local graph density,
- network observation frequency.

Feature definitions must be precise.

For every production feature, document:

```text
Feature name
Definition
Data source
Calculation
Unit
Expected range
Why it matters
Potential false-positive conditions
```

---

# 15. AI/ML REQUIREMENT

The project must contain a **real working AI/ML detection component**.

Rules alone are insufficient.

The ML layer must operate on actual input data and produce actual analytical output.

An implementation may use:

- supervised learning,
- unsupervised anomaly detection,
- semi-supervised learning,
- clustering,
- graph ML,
- temporal ML,
- or a justified hybrid.

The algorithm choice must be based on:

- available labels,
- dataset characteristics,
- interpretability,
- offline execution,
- computational feasibility,
- evaluation quality.

Do not choose a model merely because its name sounds more advanced.

---

# 16. RECOMMENDED BASELINE ML ARCHITECTURE

A practical baseline may consist of:

### Primary supervised model

Example:

- XGBoost
- Random Forest
- another interpretable tree-based model

### Secondary anomaly detector

Example:

- Isolation Forest

### Supporting analysis

Example:

- DBSCAN/HDBSCAN
- community detection
- graph-based anomaly signals

These are recommendations, not sponsor-mandated algorithms.

The project must remain logically correct if a different model is chosen.

---

# 17. MODEL EVALUATION

The project must not rely on a single accuracy number.

Where labels are available, consider:

- precision,
- recall,
- F1 score,
- PR-AUC,
- ROC-AUC,
- confusion matrix,
- Precision@K,
- Recall@K.

For anomaly detection, use appropriate ranking metrics and validate against known scenarios where ground truth is available.

Where labels are synthetic or injected, clearly state that the benchmark represents controlled prototype validation.

---

# 18. DATA LEAKAGE PREVENTION

This is mandatory for trustworthy evaluation.

Avoid:

- training and testing on the same records,
- leaking labels into features,
- generating suspicious patterns and then evaluating on the exact same generated pattern instances,
- allowing future information to leak into past predictions,
- random transaction splits that cause graph/entity leakage where inappropriate.

Prefer evaluation strategies such as:

- temporal splits,
- entity-disjoint splits,
- scenario-holdout testing,
- separate synthetic seeds,
- untouched final test sets.

The precise strategy depends on the dataset.

The AI must explicitly check for leakage before reporting model performance.

---

# 19. SYNTHETIC DATA GENERATION

If synthetic data must be generated, do not create purely random rows.

The generator should model:

### Normal behavior

Examples:

- ordinary transaction frequency,
- repeated legitimate counterparties,
- normal amounts,
- typical network observations.

### Suspicious scenarios

Examples may include:

- unusually high transaction velocity,
- burst activity,
- fan-in/fan-out structures,
- rapid multi-hop movement,
- peeling/layering-style structures,
- highly connected clusters,
- unusual IP reuse,
- multi-country observations,
- unusual temporal relationships.

The exact scenario set should be documented.

Synthetic data must contain enough noise and variation to avoid making the classification problem trivial.

The generator must support deterministic seeds for reproducibility.

---

# 20. MODEL EXPLAINABILITY

The system must generate explanations for flagged entities/transactions.

A useful explanation should answer:

> Why was this alert generated?

Possible explanation components:

### Model evidence

For example:

- high transaction velocity,
- high fan-out,
- unusual number of counterparties,
- unusual burstiness,
- unusual graph degree.

### Graph evidence

For example:

- connected to a high-risk cluster,
- unusual multi-hop path,
- strong fan-in/fan-out structure,
- shared network observations.

### Temporal evidence

For example:

- sudden activity burst,
- rapid sequential transfers,
- repeated transactions within a short time interval.

### Network evidence

For example:

- repeated observation from an IP,
- unusual IP reuse,
- geographic spread,
- repeated ASN transitions.

If a model such as a tree-based model is used, techniques such as SHAP may be used for feature-level explanation.

Explainability should combine:

```text
Model contribution
+
Graph evidence
+
Temporal evidence
+
Correlation evidence
```

Do not present a model explanation as proof of criminal activity.

---

# 21. ALERT GENERATION

The system must generate a ranked alert list.

Every alert should include, as appropriate:

- alert ID,
- entity/transaction ID,
- priority,
- confidence,
- anomaly score,
- relevant model output,
- important features,
- evidence summary,
- graph relationships,
- correlation information,
- timestamps,
- source record references,
- explanation,
- provenance.

Example conceptual structure:

```text
ALERT-00017
Priority: HIGH
Confidence: 0.84

Observed entity:
ENTITY-1042

Primary reasons:
- unusual transaction burst
- high fan-out
- repeated network observation
- strong temporal correlation

Graph evidence:
IP-17 → TX-4821 → WAL-91 → TX-4890 → WAL-107

Model evidence:
- burstiness: high
- fan_out_ratio: high
- unique_ip_count: elevated

Interpretation:
Investigative lead requiring human review.

Important:
This does not establish criminality or identity.
```

---

# 22. RISK / PRIORITY MODEL

The system may combine multiple signals into an **investigative priority score**.

Possible inputs:

- ML prediction,
- anomaly score,
- graph evidence,
- temporal evidence,
- correlation confidence,
- evidence quality.

If weighted fusion is used:

- document all weights,
- make them configurable,
- avoid arbitrary hidden constants,
- evaluate whether the fusion actually improves ranking,
- do not call the resulting number "probability of crime" unless properly calibrated and scientifically justified.

Prefer terms such as:

- investigative priority,
- alert priority,
- anomaly severity,
- evidence confidence.

---

# 23. DASHBOARD / USER INTERFACE

The system must provide a simple dashboard or link-analysis visualization.

The dashboard should prioritize investigative workflows rather than decorative visuals.

Recommended major views:

## A. Overview

Show:

- records processed,
- entities discovered,
- transactions analyzed,
- network observations,
- alerts generated,
- severity/priority distribution.

## B. Alert list

Provide:

- ranking,
- filtering,
- sorting,
- search,
- severity/priority,
- entity/transaction identifiers,
- confidence.

## C. Investigation view

When an alert is selected:

- graph,
- transaction details,
- wallet/address details,
- IP details,
- timeline,
- model explanation,
- evidence.

## D. Graph exploration

Allow:

- node selection,
- relationship inspection,
- neighborhood expansion,
- path inspection,
- filters by node type,
- filters by time.

## E. Evidence view

Show:

- source records,
- derived features,
- correlation details,
- model contribution,
- graph context.

---

# 24. INVESTIGATIVE WORKFLOW

The preferred user flow is:

```text
1. Launch application
2. Load dataset
3. Validate dataset
4. Review ingestion report
5. Configure or select analysis run
6. Run correlation
7. Build/update graph
8. Extract features
9. Run ML
10. Generate alerts
11. Rank alerts
12. Inspect top alert
13. View evidence
14. Explore graph
15. Inspect timeline
16. Review explanation
17. Export/save findings
```

The system should allow an investigator to move from a high-level alert to low-level evidence without manually reconstructing the relationship.

---

# 25. OFFLINE-FIRST ARCHITECTURE

This is a core system constraint.

At judging/runtime:

- no cloud inference,
- no required external APIs,
- no required web requests,
- no remote model calls,
- no runtime data upload,
- no required external database,
- no required online map provider.

All critical functionality must operate locally.

External resources may be downloaded and packaged before deployment where their licenses permit.

The system must have an explicit offline verification procedure.

A proper demonstration should work with network connectivity disabled.

---

# 26. EXTERNAL DEPENDENCIES

External dependencies are allowed only where they do not violate offline execution.

Examples:

- Python packages,
- locally packaged model files,
- local Geo-IP database,
- local frontend libraries,
- local graph visualization assets.

All required dependencies must be identified and packaged.

Do not make the core system dependent on a service that may be unavailable during judging.

---

# 27. STORAGE

The storage layer should be selected based on the expected prototype data volume and offline requirement.

Suitable options may include:

- SQLite,
- DuckDB,
- Parquet,
- local files,
- another embedded/local analytical store.

Use a graph database only when the graph complexity genuinely justifies it.

Do not introduce infrastructure purely for architectural appearance.

For larger datasets, prefer:

- columnar storage,
- streaming ingestion,
- batch processing,
- indexes,
- bounded-memory operations.

---

# 28. PERFORMANCE EXPECTATIONS

The prototype should be practical for bulk data rather than assuming only a few dozen records.

The system should:

- avoid loading unnecessarily large raw datasets entirely into memory;
- use batching or streaming where appropriate;
- avoid repeatedly recomputing expensive graph features;
- cache reusable derived datasets where useful;
- avoid unnecessary O(N²) operations;
- show processing status for long operations;
- maintain acceptable interactive response for dashboard exploration.

Exact performance targets must be determined empirically based on the actual development dataset.

Do not invent benchmark numbers.

Benchmark the actual implementation.

---

# 29. RELIABILITY

The application should fail gracefully.

Requirements include:

- clear validation errors,
- structured logs,
- deterministic runs where possible,
- reproducible random seeds,
- model/version identification,
- data provenance,
- retry or recovery where useful,
- corruption detection,
- safe handling of incomplete files.

A partially invalid dataset must not cause unexplained silent corruption.

---

# 30. AUDITABILITY / PROVENANCE

Every important analytical result should be traceable back toward its source.

A useful chain is:

```text
Alert
 ↓
Entity / Transaction
 ↓
Features
 ↓
Graph evidence
 ↓
Correlation evidence
 ↓
Source record(s)
 ↓
Input dataset
```

Where feasible, store:

- dataset ID,
- dataset version,
- ingestion run ID,
- analysis run ID,
- model version,
- feature version,
- configuration,
- timestamp,
- source record IDs.

A result should be reproducible using the same inputs and configuration.

---

# 31. SECURITY REQUIREMENTS

Although this is a prototype, treat investigative data as sensitive.

Do not:

- transmit datasets externally,
- send raw data to external AI services without explicit authorization,
- expose sensitive data through public endpoints,
- log unnecessary sensitive content,
- hard-code credentials,
- commit secrets,
- depend on external services at runtime.

Use:

- local processing,
- least-privilege file access,
- environment-based configuration,
- safe logging,
- input validation,
- dependency pinning where practical.

The system must never create a hidden telemetry channel.

---

# 32. PRIVACY

The system must be conservative about attribution.

Do not make claims such as:

```text
IP X = Person Y
Wallet Z = Criminal
```

unless an independently authoritative source actually establishes that fact.

The system should describe:

- observed relationships,
- correlations,
- anomalies,
- confidence,
- evidence.

It should clearly communicate uncertainty.

---

# 33. RESPONSIBLE INTERPRETATION

The system's purpose is:

```text
Detect
Correlate
Prioritize
Explain
Investigate
```

It is not:

```text
Convict
Identify a suspect automatically
Declare guilt
Automatically take punitive action
```

All suspicious outputs are **investigative leads** requiring human interpretation.

---

# 34. FALSE POSITIVES

The system must anticipate legitimate activity that may appear unusual.

Examples may include:

- exchanges,
- mining infrastructure,
- high-volume services,
- payment processors,
- legitimate multi-address behavior,
- wallets with many counterparties,
- shared infrastructure,
- institutional activity,
- IP reuse caused by NAT/shared networks.

Do not classify a single feature as proof of suspicious activity.

Avoid:

```text
High volume = criminal
Many countries = criminal
Many wallets = criminal
High fan-out = criminal
High degree = criminal
```

These are signals, not conclusions.

---

# 35. FALSE NEGATIVES

The system should also acknowledge that sophisticated suspicious activity may evade simple behavioral patterns.

Do not claim:

> "Anything not flagged is legitimate."

The correct interpretation is:

> "Entities not prioritized by this model were not prioritized under the current data, model and configuration."

---

# 36. EDGE CASES

The system must consider at least the following:

### Data edge cases

- empty file,
- very large file,
- duplicate record,
- duplicate TXID,
- missing TXID,
- missing wallet,
- missing IP,
- invalid IP,
- invalid port,
- malformed timestamp,
- invalid amount,
- empty array,
- mismatched input/output arrays,
- null geo information.

### Network edge cases

- private IP,
- loopback IP,
- reserved IP,
- IPv4,
- IPv6,
- same IP observed for many wallets,
- many IPs associated with one transaction,
- many countries for a shared infrastructure source,
- missing Geo-IP match.

### Blockchain edge cases

- multiple inputs,
- multiple outputs,
- change addresses,
- self-transfer-like patterns,
- repeated wallet reuse,
- zero-fee or unusual-fee records,
- very small transactions,
- unusually large transactions,
- long transaction chains,
- cycles in derived graphs caused by relationships rather than actual spend ordering.

### Temporal edge cases

- timezone differences,
- timestamps with different formats,
- missing timezone,
- clock skew,
- identical timestamps,
- out-of-order records,
- future timestamps,
- extremely old timestamps.

### ML edge cases

- no labels,
- very few positive examples,
- class imbalance,
- constant feature,
- missing feature,
- distribution shift,
- unseen entity,
- unseen scenario,
- model unavailable,
- incompatible model artifact.

---

# 37. ERROR HANDLING PRINCIPLE

Errors must be explicit.

Never silently convert:

```text
unknown
missing
invalid
ambiguous
unavailable
```

into:

```text
normal
safe
zero
false
confirmed
```

Unknown information should remain unknown.

---

# 38. MODEL FAILURE HANDLING

If the ML model cannot run:

- report the failure clearly;
- do not fabricate scores;
- allow safe diagnostic output if practical;
- never silently fall back to fake AI output.

A rules-based fallback may exist only if clearly labeled as a fallback and must not be presented as equivalent to the required ML component.

---

# 39. DASHBOARD FAILURE HANDLING

If graph rendering fails because of data size:

- allow tabular exploration,
- allow filtered graph rendering,
- show the relevant evidence in a non-graph form.

Never allow an oversized graph to crash the entire application unnecessarily.

---

# 40. SEARCH AND FILTERING

The investigation interface should support practical search/filter operations such as:

- TXID,
- wallet/address,
- IP,
- entity ID,
- alert ID,
- country,
- ASN,
- time range,
- priority,
- confidence range.

Filters should narrow the graph and alert list consistently.

---

# 41. EXPORT / REPORTING

The prototype should support exporting investigation findings where practical.

Possible formats:

- JSON,
- CSV,
- HTML,
- PDF,
- structured case report.

An exported finding should preserve:

- alert identifier,
- entity/transaction identifier,
- priority,
- confidence,
- key evidence,
- timestamps,
- graph/path summary,
- model information,
- source/provenance references.

Do not export claims stronger than the underlying evidence.

---

# 42. EXPECTED PROJECT DELIVERABLES

A complete solution should contain:

## D-001 — Working offline application

Runs on Linux without runtime internet dependency.

## D-002 — Ingestion module

CSV/JSON/XML support.

## D-003 — Correlation module

Network ↔ blockchain relationship generation.

## D-004 — Entity/transaction graph

Queryable and visually inspectable.

## D-005 — Working AI/ML model

Actual trained/inference-capable model.

## D-006 — Ranked alert engine

Prioritized investigative leads.

## D-007 — Explainability system

Reason for each flagged entity/transaction.

## D-008 — Dashboard/link analysis view

Interactive inspection of results.

## D-009 — Validation/testing

Demonstrable correctness checks.

## D-010 — Technical write-up

Should document:

- problem understanding,
- architecture,
- data,
- model selection,
- features,
- correlation logic,
- explainability,
- evaluation,
- limitations,
- offline deployment.

---

# 43. TECHNICAL WRITE-UP REQUIREMENTS

The documentation should answer:

### Problem

What problem is being solved?

### Why

Why is existing manual analysis insufficient?

### Data

What data is available?

### Correlation

How are network and blockchain layers connected?

### Graph

How is the graph constructed?

### Features

What signals are used?

### ML

Which model is used and why?

### Evaluation

How is success measured?

### Explainability

How do investigators understand alerts?

### Limitations

What cannot the prototype safely conclude?

### Deployment

How does it work offline?

---

# 44. ACCEPTANCE CRITERIA

The prototype can be considered functionally complete only when all critical conditions below are true.

### AC-001

A valid dataset can be imported.

### AC-002

Invalid records are handled explicitly.

### AC-003

Network and blockchain data can be correlated.

### AC-004

An entity/transaction graph can be generated.

### AC-005

Behavioral/graph/temporal features can be calculated.

### AC-006

A genuine ML model can execute locally.

### AC-007

Ranked alerts are generated.

### AC-008

Each alert has an explanation.

### AC-009

The dashboard can inspect the alert and evidence.

### AC-010

The complete application works offline.

### AC-011

The results are reproducible enough to support debugging and demonstration.

### AC-012

The system does not claim unsupported identity or criminal attribution.

### AC-013

The implementation can explain how the model was evaluated.

---

# 45. TESTING REQUIREMENTS

Testing must cover four levels.

## Unit testing

Test:

- parsers,
- validators,
- feature functions,
- correlation functions,
- graph construction,
- scoring,
- explanation generation.

## Integration testing

Test:

```text
Ingestion → Correlation
Correlation → Graph
Graph → Features
Features → ML
ML → Alerts
Alerts → Dashboard
```

## Dataset testing

Include:

- valid dataset,
- malformed dataset,
- missing fields,
- duplicate records,
- unusual values,
- empty dataset,
- large dataset.

## Offline testing

Disable network connectivity and verify:

- startup,
- data loading,
- model loading,
- analysis,
- graph rendering,
- alert generation,
- explanations,
- export.

---

# 46. DEMONSTRATION REQUIREMENTS

The most useful live demonstration should be scenario-driven.

Recommended flow:

```text
1. Load a bulk dataset.
2. Show that the system operates locally.
3. Run the analysis.
4. Display ranked alerts.
5. Open one high-priority alert.
6. Show why it was flagged.
7. Show the transaction/wallet/IP graph.
8. Show temporal behavior.
9. Show correlation confidence.
10. Trace evidence back to the source records.
11. Export or save the investigation result.
12. Demonstrate offline execution.
```

A good demonstration should prove the system's core value without requiring a long explanation.

---

# 47. PROJECT BOUNDARY

The critical path is:

```text
INGESTION
    ↓
VALIDATION
    ↓
CORRELATION
    ↓
GRAPH
    ↓
FEATURES
    ↓
AI/ML
    ↓
EXPLANATION
    ↓
RANKING
    ↓
DASHBOARD
    ↓
OFFLINE EXECUTION
```

Anything that does not materially improve this chain should be treated as secondary.

---

# 48. NON-CRITICAL OPTIONAL FEATURES

These may be considered only after the critical pipeline is stable:

- advanced graph neural networks,
- graph embeddings,
- temporal graph neural networks,
- sophisticated community detection,
- automated case management,
- advanced report generation,
- local natural-language explanation assistant,
- richer geographical visualization,
- multi-chain analytics,
- real-time streaming,
- advanced forensic workflow automation.

Optional features must never destabilize the core MVP.

---

# 49. FEATURES THAT MUST NOT BECOME CORE DEPENDENCIES

Do not make the critical path dependent on:

- live blockchain APIs,
- cloud services,
- external AI inference,
- LLM APIs,
- online Geo-IP services,
- paid intelligence providers,
- complex distributed infrastructure,
- Kubernetes,
- unnecessary microservices,
- mobile applications.

The core product must stand alone offline.

---

# 50. IMPLEMENTATION PRINCIPLES

## Principle P-001 — Correctness over complexity

A smaller validated system is preferable to a large collection of unreliable features.

## Principle P-002 — Evidence over appearance

Every important alert should be supported by interpretable evidence.

## Principle P-003 — Explainability over black-box claims

The project must be able to explain why a result was produced.

## Principle P-004 — Reproducibility

Same input + same configuration + same model should produce reproducible results when deterministic operation is intended.

## Principle P-005 — Explicit uncertainty

Unknown and ambiguous evidence must remain visible.

## Principle P-006 — Human-in-the-loop

The system produces leads for human investigation.

## Principle P-007 — Offline by design

Offline is an architectural requirement, not an emergency fallback.

## Principle P-008 — Modular architecture

Data ingestion, correlation, graph, ML, scoring, UI and deployment should remain separable.

## Principle P-009 — Measured claims

Never invent accuracy, speed, scale, or improvement numbers.

## Principle P-010 — No unnecessary technology

Use a technology because it solves a problem, not because it sounds advanced.

---

# 51. TERMINOLOGY

### Transaction

A Bitcoin transaction represented by a TXID and associated input/output information.

### TXID

Transaction identifier.

### Wallet/address

Blockchain address-level entity used in the dataset. Do not automatically equate an address with a real-world person.

### IP

Network-layer Internet Protocol address observed in telemetry.

### Network observation

A recorded network-layer event containing fields such as source/destination IP, ports and timestamp.

### Entity

A logical grouping of related addresses or other identifiers.

### Entity graph

Graph containing relationships among entities such as IPs, wallets and transactions.

### Correlation

The process of linking observations across data sources based on explicit evidence.

### Anomaly

Behavior that deviates from a learned or expected pattern.

### Alert

A generated investigation lead.

### Investigative priority

A ranking indicating which alerts should receive attention first.

### Confidence

A measure defined by the system for how strongly the evidence/model supports the alert. It must not automatically mean probability of criminality.

### Explainability

The ability to communicate why the system generated a particular output.

### Ground truth

Known labels or deliberately constructed scenarios used to evaluate the model.

### Synthetic data

Artificially generated data designed to approximate relevant structural/behavioral properties for controlled testing.

---

# 52. IMPORTANT FORENSIC RULES

The system must never assume:

```text
One IP = One person
One wallet = One person
One anomalous feature = Criminality
One model score = Proof
One correlation = Attribution
One cluster = Criminal organization
```

The system should instead represent:

```text
Observation
+
Correlation
+
Uncertainty
+
Evidence
+
Investigative Priority
```

---

# 53. COMMERCIAL / EXISTING-SOLUTION POSITIONING

Commercial blockchain intelligence platforms already provide capabilities such as transaction tracing, graph investigation, risk intelligence and transaction monitoring.

Therefore, the project must not claim to replace the full capabilities of commercial platforms.

Differentiation should instead be framed around the specific SIH problem and prototype architecture, especially:

- offline execution,
- network-layer + blockchain-layer correlation,
- transparent evidence,
- explainable analytics,
- local deployment,
- reproducible analysis,
- configurable investigative workflows.

Existing products and public prototypes are reference material, not requirements.

---

# 54. RESEARCH REFERENCE POLICY

Research papers may be used to guide:

- feature engineering,
- transaction graph analysis,
- illicit-transaction detection,
- network deanonymization,
- temporal modeling,
- graph ML,
- anomaly detection.

When research is adopted:

1. document the source;
2. describe what was actually adopted;
3. do not claim replication unless it was genuinely replicated;
4. distinguish literature results from project results.

---

# 55. TECHNOLOGY DECISION POLICY

When choosing between technologies:

1. start with the PS requirement;
2. identify the actual problem;
3. choose the simplest sufficient technology;
4. verify offline compatibility;
5. verify explainability;
6. measure performance;
7. document the decision.

Example:

Do not choose a GNN simply because:

> "GNN sounds more advanced."

Choose it only if:

- graph structure is central,
- data supports it,
- evaluation supports it,
- computation is feasible,
- the added complexity is justified.

---

# 56. CHANGE MANAGEMENT

When a requirement changes:

1. identify the original requirement;
2. record the change;
3. identify affected components;
4. update specifications;
5. update architecture if necessary;
6. update tests;
7. update current status;
8. document unresolved implications.

Never silently change an important system behavior.

---

# 57. CONFLICT RESOLUTION

If project documents disagree:

Priority order is:

```text
1. Latest authoritative sponsor requirement
2. Explicit project decision recorded in decisions.md
3. Current architecture/specification
4. Current implementation
5. Temporary notes
6. AI assumptions
```

If two authoritative sources conflict and the conflict cannot be resolved:

- mark the requirement as CONFLICTING;
- do not silently pick one;
- identify the exact conflict;
- choose the safest implementation only when necessary;
- document the assumption.

---

# 58. SOURCE OF TRUTH RULE

The Master Prompt defines:

- project identity,
- sponsor requirements,
- system purpose,
- hard constraints,
- non-negotiable behavior,
- terminology,
- acceptance principles.

Project documentation files define:

- current implementation,
- architecture decisions,
- schema versions,
- current status,
- implementation details,
- test results,
- decisions,
- changes.

Code defines:

- actual implementation.

If the code differs from documentation, the discrepancy must be surfaced rather than hidden.

---

# 59. FINAL PROJECT OUTCOME

The intended final system is:

> An offline, Linux-compatible, AI-assisted Bitcoin transaction and network intelligence prototype that ingests bulk structured metadata, correlates network and blockchain observations, builds an entity/transaction graph, detects unusual behavior using real ML, ranks investigative leads, explains the evidence behind those leads, and provides an investigator-oriented visualization and analysis workflow.

The system must prioritize:

```text
Accuracy of interpretation
+
Evidence
+
Explainability
+
Reproducibility
+
Offline operation
+
Practicality
+
Clear investigation workflow
```

over:

```text
Feature count
+
Buzzwords
+
Unnecessary architecture
+
Unverified claims
```

---

# 60. NON-NEGOTIABLE RULES

Never violate these rules:

1. The core system must function offline.
2. The core system must run on Linux.
3. CSV/JSON/XML ingestion must remain supported.
4. Network and blockchain layers must be correlated.
5. An entity/transaction graph must exist.
6. A real AI/ML model must be part of the detection pipeline.
7. Alerts must be ranked.
8. Alerts must be explainable.
9. Geo-IP integration must be possible through a downloadable local database.
10. Synthetic data must not be presented as real-world criminal ground truth.
11. IP/wallet correlation must not automatically be presented as identity proof.
12. Model scores must not be presented as criminal guilt.
13. Unknown or ambiguous information must not be silently converted into certainty.
14. Performance or accuracy numbers must be measured, not invented.
15. Optional features must not destabilize the critical path.
16. External services must not be required for core offline operation.
17. Every important design assumption must be documented.
18. Changes to core requirements must be recorded.
19. The implementation must remain testable and reproducible.
20. The project must remain an investigative decision-support system, not an autonomous enforcement system.

---

# 61. DEFAULT ENGINEERING DIRECTION

Unless another documented decision supersedes it, a pragmatic prototype architecture may use:

```text
Python
    ↓
CSV / JSON / XML ingestion
    ↓
Validation + normalization
    ↓
Local analytical storage
    ↓
Correlation engine
    ↓
NetworkX or equivalent graph layer
    ↓
Behavioral + temporal + graph features
    ↓
Tree-based supervised model
+
Isolation Forest / anomaly detector
    ↓
Evidence fusion
    ↓
Explainability
    ↓
Ranked alerts
    ↓
Local dashboard
```

This is a recommended implementation path, not a hard sponsor requirement.

---

# 62. AI AGENT BEHAVIOR WHEN WORKING ON THIS PROJECT

When an AI agent is asked to modify or extend the project:

1. Preserve all mandatory requirements.
2. Do not invent sponsor requirements.
3. Check project documentation before changing architecture.
4. Prefer the smallest change that solves the requested problem.
5. Do not introduce external runtime dependencies that violate offline operation.
6. Do not remove explainability or provenance to simplify implementation.
7. Do not replace a real ML component with deterministic rules and still describe the result as ML.
8. Do not fabricate datasets, evaluation metrics, or performance claims.
9. Clearly state assumptions when requirements are ambiguous.
10. Maintain backward compatibility with existing data contracts where possible.
11. Add/update tests for important behavioral changes.
12. Update project documentation after significant changes.
13. Keep temporary implementation notes separate from permanent project knowledge.
14. If the existing implementation conflicts with this specification, identify the conflict before silently changing behavior.
15. Do not assume that a feature is complete merely because code exists; verify it through tests or execution.

---

# 63. DEFINITION OF "DONE"

A feature is DONE only when:

```text
Implemented
+
Integrated
+
Tested
+
Documented
+
Works offline
+
Does not violate the PS
```

Code existing in a file is not sufficient evidence that a feature is complete.

---

# 64. FINAL INSTRUCTION TO ANY AI WORKING ON SIH26146

Understand the entire project as an integrated investigative system.

Do not optimize one subsystem in isolation.

Always ask:

```text
Does this help ingest?
Does this improve correlation?
Does this improve the graph?
Does this improve detection?
Does this improve evidence?
Does this improve explainability?
Does this improve investigator usability?
Does this preserve offline operation?
Does this remain scientifically and forensically defensible?
```

When proposing a change, distinguish clearly between:

- REQUIRED BY PS
- REQUIRED BY EXISTING PROJECT DESIGN
- RECOMMENDED
- OPTIONAL
- EXPERIMENTAL
- UNKNOWN / NEEDS VERIFICATION

The project must remain understandable, defensible and demonstrable from end to end.

END OF MASTER PROJECT PROMPT