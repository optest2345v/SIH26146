# SIH26146 — AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic

[![Sponsor: NTRO](https://img.shields.io/badge/Sponsor-NTRO-blue.svg)](https://ntro.gov.in)
[![Team: COGNOVAX](https://img.shields.io/badge/Team-COGNOVAX-green.svg)](#)
[![Team ID: 162623](https://img.shields.io/badge/Team%20ID-162623-orange.svg)](#)
[![Security: 100% Offline Air-Gap](https://img.shields.io/badge/Security-100%25%20Offline%20Air--Gap-red.svg)](#)
[![Tests: 39 Passed](https://img.shields.io/badge/Tests-39%20Passed-brightgreen.svg)](#)

> **Autonomous Bitcoin Forensic Intelligence & Network Traffic Correlation Platform**  
> Developed for the **National Technical Research Organisation (NTRO)** under **Smart India Hackathon (Problem Statement: SIH26146)**.

---

## 1. Executive Summary

Law enforcement and national intelligence agencies face immense challenges in attributing illicit cryptocurrency flows due to the decoupling of **network-layer telemetry** (IP addresses, peer gossip, timestamps) from **on-chain blockchain ledger events** (TXIDs, wallet clusters, outputs).

**COGNOVAX** delivers a 100% sovereign, air-gapped forensic intelligence platform that ingests bulk heterogeneous telemetry, correlates network traffic with blockchain transactions, builds a dynamic entity graph, executes dual-engine AI/ML anomaly detection, and surfaces explainable, prioritized investigative leads.

---

## 2. Key Architecture & Features

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│ Bulk Ingestion  │ ──► │ Validation &     │ ──► │ Evidence           │
│ (CSV, JSON, XML)│     │ Normalization    │     │ Correlation Engine │
└─────────────────┘     └──────────────────┘     └────────────────────┘
                                                            │
┌─────────────────┐     ┌──────────────────┐     ┌──────────▼─────────┐
│ Investigation   │ ◄── │ Ranked Leads &   │ ◄── │ Entity Graph &     │
│ Web Dashboard   │     │ Explainability   │     │ Dual AI/ML Engine  │
└─────────────────┘     └──────────────────┘     └────────────────────┘
```

1. **Multi-Format Ingestion & Validation (`src/ingestion/`):**
   * High-throughput parsers for **CSV**, **JSON / JSONL**, and **XML** formats.
   * Schema contract validation with quarantine isolation for malformed data.
2. **Network ↔ Blockchain Evidence Correlation (`src/correlation/`):**
   * Multi-factor correlation linking network broadcast observations to on-chain transactions via **Exact TXID**, **Sliding Temporal Proximity Windows (±60s)**, and **Repeated IP Infrastructure Corroboration**.
3. **Graph Intelligence & Topology Studio (`src/graph/`):**
   * Directed multi-relational graph connecting `IP`, `TX`, and `WALLET` entities.
   * **Common-Input Co-Spending Heuristic** for automated wallet clustering.
   * 60 FPS force-directed physics layout with slide-over node inspector drawer.
4. **Dual-Model AI/ML Engine (`src/ml/`):**
   * **Unsupervised Isolation Forest:** Detects novel structural outliers and zero-day laundering patterns.
   * **Supervised Random Forest:** Classifies known threat typologies (peeling chains, high-velocity bursts, fan-out mixing).
5. **Investigative Explainability & Lead Ranking (`src/alerts/`):**
   * Multi-factor priority score ($Score = 0.40 \cdot Anomaly + 0.35 \cdot Correlation + 0.25 \cdot Centrality$).
   * Explicit separation of Anomaly Score, Correlation Confidence, and Investigative Priority.
   * Plain-language forensic narratives with traceable evidence provenance.
6. **Advanced Forensic Toolkit (`src/analytics/`):**
   * **Multi-Hop Fund Taint Propagation:** Proportional haircut algorithm tracing tainted funds across peeling chains.
   * **Chrono-Player Time-Lapse:** Interactive timeline playback with scrubbing controls.
   * **Autonomous Syndicate Detection:** Graph community detection uncovering laundering rings and mixing pools.
   * **Section 65B Chain-of-Custody Export:** Court-admissible ZIP packages with SHA-256 integrity digests.
7. **Strict Air-Gap Sovereign Execution:**
   * **Zero external runtime network dependencies** (no cloud APIs, zero socket leaks).
   * Local Geo-IP subnet resolution without external DNS queries.

---

## 3. Quick Start Guide

### Prerequisites
* **Operating System:** Linux (Ubuntu 20.04+, Debian, RHEL) or Windows 10/11
* **Python:** Python 3.10, 3.11, or 3.12
* **Package Manager:** `pip`

### 1. Install Dependencies
In your terminal or command prompt:
```bash
pip install -r requirements.txt
```

---

### 2. Launching the Platform

#### **Option A: 1-Click Web Dashboard (Recommended)**
* **On Windows:** Double-click [`start_dashboard.bat`](file:///start_dashboard.bat)
* **On Linux:** Run `./start_dashboard.sh`

*(The script starts the local service, waits for health readiness, and automatically opens `http://127.0.0.1:8000` in your default browser).*

#### **Option B: Master Interactive Operations Menu**
* **On Windows:** Run [`run.bat`](file:///run.bat)
* **On Linux:** Run `./run.sh`

Provides an interactive numbered menu for all platform functions:
```text
============================================================
  SIH26146: Bitcoin Transaction & Network Intelligence
  Team: COGNOVAX (Team ID: 162623) | Sponsor: NTRO
============================================================
  [1] Launch Investigation Web Dashboard (Opens Browser)
  [2] Run Forensic Pipeline CLI (Ingest, Correlate, ML, Rank)
  [3] Run Automated Test Suite (39 Pytest Verification Tests)
  [4] Regenerate Baseline Test Datasets (34 records)
  [5] Generate 10,000+ Record Benchmark Dataset (JSON, CSV, XML)
  [6] Run 10k Blind Benchmark Evaluation & Scorecard
  [7] Run Model Ablation Benchmark Study
  [8] Exit
============================================================
```

#### **Option C: 1-Click Verification Test Suite**
* **On Windows:** Double-click [`run_tests.bat`](file:///run_tests.bat)
* **On Linux:** Run `./run_tests.sh`

---

## 4. CLI Command Reference

All core capabilities can also be executed directly via Python:

| Command | Description |
| :--- | :--- |
| `python main.py serve` | Starts the investigation web server at `http://127.0.0.1:8000`. |
| `python main.py serve --port 8080` | Starts the service on a custom port. |
| `python main.py run` | Executes end-to-end analytical pipeline on synthetic sample data. |
| `python main.py run --data <file_path>` | Ingests and analyzes a custom CSV, JSON, or XML file. |
| `python main.py run --data <file> --export dossier.json` | Ingests data and exports a structured JSON case dossier. |
| `python main.py generate-benchmark` | Generates 10,250-record forensic benchmark with separate hidden ground truth. |
| `python main.py evaluate-benchmark` | Evaluates detection pipeline against hidden ground truth and prints scorecard. |
| `python main.py evaluate --ablation` | Executes comparative model ablation study across 1,045 holdout entities. |
| `python main.py generate-data` | Regenerates standard baseline scenario files in `data/synthetic/`. |
| `pytest tests/ -v` | Executes the complete 39-test automated test suite. |

---

## 5. Web Investigation Dashboard Walkthrough

Access the dashboard at `http://127.0.0.1:8000`:

* **Dynamic Topology Studio:** Full-screen graph canvas with interactive pan, zoom, drag, and node highlighting.
* **Lead Triage Table:** Prioritized threats ranked by investigative score with badges (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and real-time search.
* **Node Inspector Drawer:** Slide-over panel displaying entity type, BTC transaction volume, fees, counterparty addresses, and Geo-IP telemetry.
* **Multi-Hop Fund Taint Tool:** Select any suspicious node and trigger multi-hop taint tracing to reveal downstream peeling chains and exit points.
* **Chrono-Player Playback Dock:** Play, pause, or scrub through transactions chronologically to visualize the propagation of transactions over time.
* **Forensic Dossier Export:** 1-click download of:
  * **Plain-Text Dossier (`.txt`)** for investigator notes.
  * **Machine JSON Dossier (`.json`)** for inter-agency data sharing.
  * **Section 65B Chain-of-Custody Bundle (`.zip`)** containing raw data, audit logs, and SHA-256 cryptographic hashes.

---

## 6. 10,000+ Record Benchmark & Model Ablation

To demonstrate enterprise scalability and defense-grade accuracy, COGNOVAX includes an independent **10,250-record benchmark suite** (`data/benchmark_10k/`):

### Benchmark Performance Metrics (Blind Hold-Out)
- **Top Leads Precision (Precision@3):** `100.0%`
- **Investigator Yield (Precision@10):** `100.0%`
- **Entity Classification ROC-AUC:** `0.9944`
- **Peeling Chain Typology Recall:** `100.0%`
- **High-Velocity Burst Recall:** `100.0%`
- **Structuring / Smurfing Recall:** `100.0%`
- **Total Ingestion & Pipeline Runtime:** `< 8 seconds` for 10,250 records

Run the benchmark evaluation:
```bash
python main.py evaluate-benchmark
```

Run the model ablation study:
```bash
python main.py evaluate --ablation
```

---

## 7. Automated Testing & Air-Gap Verification

The repository includes **39 automated tests** covering unit, integration, benchmark, and security requirements:

```bash
pytest tests/ -v
```

### Air-Gap Verification Test
To prove that COGNOVAX operates 100% offline without leaking any data:
```bash
pytest tests/test_offline.py -v
```
*(This test monkeypatches the operating system socket layer to disallow any outbound network connections. The pipeline runs end-to-end to verify zero network socket attempts).*

---

## 8. Repository Layout

```text
.
├── main.py                     # Master CLI and service launcher
├── requirements.txt            # Python dependencies (pure offline-capable)
├── start_dashboard.bat         # 1-Click Web Dashboard launcher (Windows)
├── start_dashboard.sh          # 1-Click Web Dashboard launcher (Linux)
├── run_tests.bat               # 1-Click Pytest test runner (Windows)
├── run_tests.sh                # 1-Click Pytest test runner (Linux)
├── run.bat                     # Master Interactive Operations Menu (Windows)
├── run.sh                      # Master Interactive Operations Menu (Linux)
├── DEMO_PLAYBOOK.md            # Step-by-step judge presentation walkthrough
│
├── src/                        # Core Application Source Code
│   ├── api/                    # FastAPI local offline REST server & endpoints
│   ├── alerts/                 # Priority scoring, ranking & explainability
│   ├── correlation/            # Network ↔ blockchain evidence correlation
│   ├── dashboard/              # Standalone dark-mode HTML/CSS/JS interface
│   ├── features/               # 16-dimensional behavioral feature pipeline
│   ├── geoip/                  # Local offline subnet & RFC 1918 resolution
│   ├── graph/                  # NetworkX multigraph builder & analytics
│   ├── ingestion/              # CSV, JSON, and XML parsers & validators
│   ├── ml/                     # Isolation Forest & Random Forest models
│   ├── models/                 # Pydantic data schemas & contracts
│   ├── reporting/              # Section 65B dossier & intelligence brief
│   └── synthetic/              # Scenario generators & benchmark evaluators
│
├── data/                       # Offline Forensic Datasets
│   ├── benchmark_10k/          # 10,250-record blind hold-out benchmark
│   ├── scenarios/              # Targeted forensic typology scenarios
│   └── synthetic/              # Baseline sample transaction datasets
│
├── models/saved/               # Pre-trained offline model artifacts
│   └── ml_detector.joblib      # Serialized ML ensemble
│
├── tests/                      # Automated Verification & Acceptance Suite
│   ├── test_alerts.py          # Alert ranking & priority separation
│   ├── test_api.py             # API endpoints & export verification
│   ├── test_benchmark.py       # 10k benchmark generator & evaluator
│   ├── test_correlation.py    # Temporal & TXID correlation
│   ├── test_features.py       # Feature extraction contract
│   ├── test_geoip.py          # Offline Geo-IP subnet resolution
│   ├── test_graph.py          # Graph construction & taint propagation
│   ├── test_ingestion.py      # Schema validation & format parsers
│   ├── test_ml.py             # Anomaly detection & classifier metrics
│   └── test_offline.py        # Strict socket-blocking air-gap test
│
├── docs/                       # Engineering Specifications & Architecture ADRs
│   └── dev_context/           # Archived developer context & prompt specifications
│
└── project_materials/          # Presentation & Submission Assets
    └── presentation/           # PowerPoint presentations, diagrams & slides
```

---

## 9. Team & Institutional Credentials

* **Team Name:** COGNOVAX  
* **Team ID:** 162623  
* **Problem Statement:** SIH26146  
* **Sponsoring Agency:** National Technical Research Organisation (NTRO)  
* **Category:** Software / Cyber Security & Digital Forensics
