# SIH26146 — Dashboard / Investigation UI Specification

## UX goal

The interface should help an investigator move from a high-level alert to supporting evidence with minimal manual reconstruction.

## Required/target views

### 1. Overview

Display useful system-level counts such as:

- records processed;
- entities;
- transactions;
- network observations;
- alerts;
- priority distribution.

### 2. Alert list

Support:

- ranking;
- search;
- filters;
- sort;
- entity/transaction IDs;
- priority;
- confidence.

### 3. Investigation view

Show:

- alert summary;
- anomaly score;
- correlation confidence;
- investigative priority;
- graph;
- transaction data;
- wallet/address data;
- IP/network context;
- timeline;
- explanation;
- provenance.

### 4. Graph exploration

Support where practical:

- node selection;
- relationship inspection;
- neighborhood expansion;
- path inspection;
- node-type filtering;
- time filtering.

### 5. Evidence panel

Show:

- source record IDs;
- derived feature values;
- correlation details;
- model contributions;
- graph evidence.

## UX rules

- Do not make color the only indicator of priority.
- Make uncertainty visible.
- Avoid wording that implies automatic guilt or identity.
- Avoid rendering the entire graph when a filtered neighborhood is sufficient.
- Provide a table alternative if graph rendering becomes too large.

## Target demo flow

`Load data → Validate → Analyze → Ranked alerts → Open alert → Explanation → Graph → Timeline → Evidence → Export`
