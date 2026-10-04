# SIH26146 — Project Context

> This is the small AI entry point. Keep it concise. Detailed requirements belong in `MASTER_PROJECT_PROMPT.md` and the specialist documents under `docs/`.

## Project

**Problem Statement:** SIH26146  
**Title:** AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic  
**Sponsor:** National Technical Research Organisation (NTRO)  
**Category:** Software  
**Runtime target:** Linux  
**Core execution constraint:** Fully offline

## Mission

Build an offline Bitcoin transaction/network intelligence prototype that ingests bulk structured metadata, validates and normalizes it, correlates network observations with blockchain observations, constructs an entity/transaction graph, performs AI/ML-based analysis, generates ranked and explainable investigative leads, and provides an investigator-oriented visualization and evidence workflow.

## Critical pipeline

`Ingestion → Validation → Correlation → Graph → Features → AI/ML → Explainability → Ranked Alerts → Investigation UI → Offline Execution`

## Non-negotiable constraints

- Linux execution
- Offline core functionality
- CSV / JSON / XML ingestion
- Network ↔ blockchain correlation
- Entity/transaction graph
- Genuine AI/ML component
- Ranked investigative alerts
- Explainable alerts
- Local/downloadable Geo-IP support rather than runtime online lookup
- Human-in-the-loop interpretation
- No unsupported identity or criminality claims
- No fabricated performance or accuracy claims

## Current state
- Requirements: VERIFIED & DOCUMENTED
- Architecture: IMPLEMENTED (Modular Python pipeline)
- Data pipeline: VERIFIED (CSV / JSON / XML ingestion + offline Geo-IP)
- Correlation engine: VERIFIED (Exact TXID + temporal proximity + repeated IP)
- Graph engine: VERIFIED (NetworkX multi-directed graph + ego-subgraphs)
- ML pipeline: VERIFIED (Isolation Forest + Supervised Random Forest)
- Explainability: VERIFIED (Multi-factor evidence + plain language narratives)
- Alert ranking: VERIFIED (Investigative priority score & CRITICAL/HIGH/MED tiers)
- Dashboard: VERIFIED (Local dark-mode SPA with Dynamic Topology Studio & tri-gauges)
- Offline packaging: VERIFIED (100% offline, zero external runtime internet calls)
- Testing: VERIFIED (36 unit, integration, benchmark, and offline acceptance tests passing)
- Export & Custody: VERIFIED (Dual .txt & .json downloads, multi-page print, and cryptographic Chain-of-Custody .zip bundle)
- Forensic Analytics: VERIFIED (Multi-hop fund taint propagation engine & interactive Chrono-Player time-lapse)
- Benchmark Suite: VERIFIED (10,250 records, blind hold-out scoring, 100% Top-K Precision, 0.9944 ROC-AUC)


## Key design principle

Treat anomaly score, correlation confidence, and investigative priority as separate concepts. The system produces investigative leads, not proof of identity or guilt.

## Differentiation direction

Recommended strategic emphasis: **evidence-backed network ↔ blockchain correlation**, temporal investigation, explicit uncertainty, and traceable evidence provenance. These are project recommendations, not sponsor-mandated algorithms.

## Read next

- Overall requirements → `docs/02-requirements.md`
- Architecture → `docs/03-architecture.md`
- Data/schema → `docs/04-data-contract.md`
- Correlation → `docs/05-correlation-spec.md`
- ML → `docs/06-ml-specification.md`
- UI → `docs/07-dashboard-spec.md`
- Security/privacy → `docs/08-security-privacy.md`
- Testing → `docs/09-testing-validation.md`
- Decisions → `docs/10-decisions.md`
- Current implementation status → `docs/11-current-status.md`
- Backlog → `docs/12-backlog.md`
- Research/references → `docs/13-references.md`
- AI work log → `docs/14-what-the-ai-has-done.md`
