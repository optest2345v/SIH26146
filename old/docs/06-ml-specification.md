# SIH26146 — ML Specification

## Status

`TO ASSESS AGAINST CURRENT IMPLEMENTATION`

## Objective

Use a genuine AI/ML method to identify unusual or suspicious behavioral patterns in the available data while keeping the result explainable and locally executable.

## Recommended baseline

A practical prototype can consider:

- supervised tree-based model such as XGBoost or Random Forest where reliable labels exist;
- Isolation Forest or another anomaly method for unlabeled/unusual behavior;
- graph-derived and temporal features;
- explainability with SHAP or a model-appropriate alternative.

These are recommendations, not sponsor-mandated algorithms.

## Feature groups

### Transaction behavior

- transaction count;
- total amount;
- average/median amount;
- amount dispersion;
- frequency/velocity;
- repeated counterparties.

### Network behavior

- unique IP count;
- IP reuse;
- country count;
- ASN count;
- observation frequency.

### Temporal behavior

- inter-arrival time;
- burstiness;
- activity change;
- rapid sequential transfers;
- observation-to-transaction time delta.

### Graph behavior

- degree;
- in/out degree;
- fan-in/fan-out;
- neighborhood size;
- centrality;
- component size;
- local density;
- path depth;
- community/motif features where justified.

## Feature contract

Every production feature should document:

- feature name;
- exact definition;
- input fields;
- calculation;
- unit;
- expected range;
- interpretation;
- likely false-positive conditions;
- version.

## Label strategy

If the official dataset is synthetic, document how labels/scenarios were produced. Do not present synthetic test performance as guaranteed real-world performance.

## Leakage prevention

Prefer:

- temporal splits;
- entity-disjoint evaluation;
- scenario holdouts;
- different random seeds;
- untouched final test data.

Avoid using future information to predict past behavior.

## Evaluation

Where labels are available, consider:

- precision;
- recall;
- F1;
- PR-AUC;
- ROC-AUC;
- confusion matrix;
- Precision@K;
- Recall@K.

For ranked investigations, top-K utility is especially relevant.

## Explainability

An explanation should identify concrete contributing signals rather than merely outputting the model label.

## Model artifact metadata

Record:

- model ID/version;
- feature version;
- training dataset version;
- training timestamp;
- random seed where relevant;
- evaluation summary;
- known limitations.

## Failure behavior

If the model is unavailable or incompatible, report the failure. Never fabricate a score.
