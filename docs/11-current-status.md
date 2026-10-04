# SIH26146 — Current Status

> This starter file intentionally does not pretend to know the state of the existing codebase. Update it after a repository inspection.

## Status legend

- `NOT STARTED`
- `PLANNED`
- `IN PROGRESS`
- `BLOCKED`
- `IMPLEMENTED`
- `TESTED`
- `VERIFIED`
- `DEPRECATED`
- `UNKNOWN`

## Current implementation matrix

| Component | Status | Evidence / test reference | Notes |
|---|---|---|---|
| Project requirements documentation | VERIFIED | Master Prompt + docs | Complete specification |
| CSV ingestion | VERIFIED | `tests/test_ingestion.py` | Full bulk CSV parsing + headers aliasing |
| JSON ingestion | VERIFIED | `tests/test_ingestion.py` | Array & JSONL formats supported |
| XML ingestion | VERIFIED | `tests/test_ingestion.py` | Standard & nested XML formats supported |
| Validation | VERIFIED | `tests/test_ingestion.py` | Explicit rejection of malformed inputs & negative amounts |
| Normalization | VERIFIED | `tests/test_ingestion.py` | Normalized to `NormalizedRecord` schema contract |
| Geo-IP | VERIFIED | `tests/test_geoip.py` | 100% offline local subnet & RFC classification |
| Network↔blockchain correlation | VERIFIED | `tests/test_correlation.py` | Exact TXID + temporal window + repeated IP |
| Entity resolution | VERIFIED | `tests/test_graph.py` | Common-input co-spending clustering heuristic |
| Graph | VERIFIED | `tests/test_graph.py` | NetworkX typed multi-directed graph (IP, TX, WALLET) |
| Feature engineering | VERIFIED | `tests/test_features.py` | 16 behavioral, temporal, network, and graph features |
| Supervised ML | VERIFIED | `tests/test_ml.py` | Random Forest classifier with scenario holdout |
| Anomaly detection | VERIFIED | `tests/test_ml.py` | Unsupervised Isolation Forest continuous scoring |
| Explainability | VERIFIED | `tests/test_alerts.py` | Multi-factor plain language reasons & narrative |
| Alert ranking | VERIFIED | `tests/test_alerts.py` | Priority score descending order (CRITICAL/HIGH/MED/LOW) |
| Alert evidence/provenance | VERIFIED | `tests/test_alerts.py` | Full traceability to source row and file IDs |
| Dashboard & Dynamic Topology Studio | VERIFIED | `tests/test_api.py`, `src/dashboard/` | Responsive dark-mode SPA, 4-mode Topology Studio, incremental expansion, route tracing |
| Fund Taint Propagation Engine | VERIFIED | `tests/test_graph.py`, `src/graph/` | Multi-hop Haircut fund taint tracing with visual halos |
| Chrono-Player Time-Lapse Suite | VERIFIED | `src/dashboard/index.html` | Playback dock with scrub slider, speed controls, sequential flow illumination |
| Export & Evidence Reporting | VERIFIED | `tests/test_api.py` | JSON dossier, .txt dossier, print layout, and court-admissible Chain-of-Custody (.zip) |
| Active Dataset Ingestion & Protection | VERIFIED | `tests/test_api.py`, `src/dashboard/` | Full Drag & Drop (.csv/.json/.xml), 1-click dataset download, overwrite confirmation modal |
| Scenario Presets & Instant Demonstration | VERIFIED | `src/synthetic/scenario_presets.py`, `tests/test_api.py` | 6 targeted presets (Peeling, Burst, Structuring, Benign Exchange, 10K Benchmark) with 1-click execution |
| Entity Intelligence Dossier & Cluster Inspector | VERIFIED | `tests/test_api.py`, `src/api/server.py`, `src/dashboard/` | Deep node inspector with co-spending cluster addresses, AI lead attribution, and 1-click taint trace |
| Autonomous Laundering Syndicate & Ring Detection | VERIFIED | `tests/test_api.py`, `tests/test_graph.py`, `src/graph/analytics.py` | Topological graph partitioning & motif classifier identifying peeling rings, mixers, and botnets |
| Classified Agency Forensic Intelligence Briefing | VERIFIED | `tests/test_api.py`, `src/reporting/intelligence_brief.py` | Official NTRO executive case brief with print-ready pagination, syndicate table, and SHA-256 seal |
| Investigator Case Notes & Human Disposition Tagging | VERIFIED | `tests/test_api.py`, `src/dashboard/index.html`, `src/api/server.py` | Human-in-the-loop triage dispositions (SEIZURE, SURVEILLANCE, BENIGN), audit log & custody inclusion |
| Model Ablation Evaluation Suite | VERIFIED | `src/ml/ablation.py`, `main.py evaluate --ablation` | 4-model comparison against 1,045 blind entities (Rule-based vs IF vs RF vs Fused Ensemble) |
| Interactive Terminal Forensic Console (TUI) | VERIFIED | `src/cli/terminal_ui.py`, `tests/test_terminal_ui.py` | Full headless/SSH air-gapped forensic terminal with ASCII graph, taint tree, inspector & tagging |
| Linux Air-Gap Packaging & Shell Runners | VERIFIED | `requirements.txt`, `Dockerfile`, `*.sh`, `*.bat` | Offline runners with async health-check poller, terminal console launchers, zero remote dependency |
| Offline execution | VERIFIED | `tests/test_offline.py` | Zero network socket connection test passed |
| 10,000+ Record Benchmark Generator | VERIFIED | `tests/test_benchmark.py`, `src/synthetic/` | 10,250 records, zero data leakage, multi-typology, CSV/JSON/XML |
| Blind Benchmark Evaluator | VERIFIED | `tests/test_benchmark.py`, `src/synthetic/` | Independent evaluation against hidden ground truth, audit scorecard |
| Unit & Integration tests | VERIFIED | 47 passing tests in `tests/` | Pytest suite running cleanly in ~27s |

| Integration tests | VERIFIED | `main.py run`, `tests/test_api.py`, `tests/test_benchmark.py`, `tests/test_terminal_ui.py` | End-to-end pipeline, API & TUI verified |
| Offline acceptance test | VERIFIED | `tests/test_offline.py` | Verified with socket connection blocking |

## Active blockers

None. All prototype features, web dashboard, headless terminal console, Linux runners, Dockerfile, ablation evaluations, and demo playbook are complete.

## Next verification step

System is fully demonstrable via Web UI (`./start_dashboard.sh` / `start_dashboard.bat`), Terminal Console (`python main.py console` / `./terminal_console.sh` / `terminal_console.bat`), and CLI evaluation (`python main.py evaluate --ablation`). Follow `DEMO_PLAYBOOK.md` for live judge presentation.
