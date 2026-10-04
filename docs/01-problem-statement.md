# SIH26146 — Problem Statement

## Authority

**Source type:** SIH problem statement / sponsor specification  
**Problem ID:** SIH26146  
**Title:** AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic  
**Sponsor:** National Technical Research Organisation (NTRO)  
**Category:** Software

## Sponsor-derived problem summary

The project is expected to process bulk Bitcoin P2P/transaction metadata and correlate network-layer observations with blockchain-layer transaction information so that suspicious or unusual behavior can be identified and presented as ranked, explainable investigative leads.

## Required data concepts

### Network layer

- timestamp
- source IP
- destination IP
- source port
- destination port
- TXID where available

### Blockchain layer

- TXID
- transaction timestamp
- input addresses
- output addresses
- input amounts
- output amounts
- fees where present
- script type where present

### Enrichment

- geo country
- ASN
- local downloadable Geo-IP database support

## Required solution concepts

- bulk ingestion
- CSV / JSON / XML support
- validation and normalization
- network ↔ blockchain correlation
- entity/transaction graph
- AI/ML-based detection
- ranked investigative alerts
- explanation of why an alert was produced
- dashboard/link-analysis visualization
- offline Linux execution

## Data constraint

The SIH specification describes a synthetic dataset modeled on real Bitcoin P2P/transaction fields and states that real seized/live-intercept data will not be supplied.

## Important interpretation boundary

This file intentionally does not add architecture choices such as a specific ML algorithm or database. Those belong in the project recommendation/decision documents.

## Source note

For the exact sponsor wording, use `MASTER_PROJECT_PROMPT.md` plus the original SIH source supplied/verified for the project. Do not silently substitute general blockchain knowledge for sponsor requirements.
