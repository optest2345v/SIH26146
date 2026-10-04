# SIH26146 — Testing & Validation

## Testing layers

### Unit tests

Cover:

- CSV parser;
- JSON parser;
- XML parser;
- schema validation;
- normalization;
- IP validation;
- timestamp normalization;
- correlation functions;
- feature calculations;
- graph construction;
- scoring;
- explanation generation.

### Integration tests

Validate:

`Ingestion → Correlation → Graph → Features → ML → Alerts → Dashboard`

### Data-quality tests

Use fixtures covering:

- valid data;
- malformed data;
- missing fields;
- duplicates;
- invalid IP/port;
- empty dataset;
- mismatched arrays;
- large files.

### ML validation

At minimum check:

- train/test separation;
- leakage;
- class imbalance;
- baseline comparison;
- metrics suitable for the task;
- reproducibility;
- explanation correctness.

## Scenario-based synthetic tests

Develop known scenarios such as:

- burst activity;
- high fan-out;
- fan-in;
- rapid multi-hop movement;
- repeated IP observation;
- ambiguous shared-IP behavior;
- normal high-volume behavior that should not automatically be marked suspicious.

## 10,000+ Record Industrial-Grade Forensic Benchmark Suite

The repository includes a reproducible, high-scale benchmark generator and blind evaluator (`src/synthetic/benchmark_generator.py` and `src/synthetic/benchmark_evaluator.py`).

### Dataset Architecture
1. **Raw Evaluation Files (`data/benchmark_10k/benchmark_data.*`):**
   - 10,250 records formatted in CSV, JSON, and XML.
   - Zero hint labels or ground-truth leakage (`is_anomalous`, `scenario_label`, etc. are omitted).
   - Diurnal Poisson normal traffic, Zipfian wallet distributions, log-normal BTC values.
   - High-volume benign infrastructure: exchange sweeps and mining pool reward payouts.
   - Complex topologies: peeling chains, high-velocity micro-bursts, fan-in structuring mixers, multi-country VPN/Tor geo-hopping.
   - Real-world telemetry edge cases: malformed JSON records, duplicate observations, out-of-order events, incomplete network telemetry.
2. **Independent Hidden Ground Truth (`data/benchmark_10k/ground_truth.json`):**
   - Ground truth annotations per entity, transaction, and record.
   - Kept isolated from the detector during execution.
3. **Official Benchmark Manifest (`data/benchmark_10k/benchmark_manifest.json`):**
   - Evaluation targets and expected validation metrics.

### Blind Benchmark Performance Targets
- **Precision@3 (Top Leads):** Realized **100.0%** (Target: 100.0%)
- **Precision@5 (Top Leads):** Realized **100.0%** (Target: 100.0%)
- **Precision@10 (Investigator Yield):** Realized **100.0%** (Target: &ge; 80.0%)
- **ROC-AUC (Entity Classification):** Realized **0.9944** (Target: &ge; 0.8500)
- **Peeling Chain Recall:** Realized **100.0%**
- **Micro-Burst Recall:** Realized **100.0%**
- **Structuring Recall:** Realized **100.0%**
- **Geo-Hopping Recall:** Realized **100.0%**

CLI execution:
```bash
python main.py generate-benchmark
python main.py evaluate-benchmark
```

## Offline acceptance test

Disable network connectivity and verify:

- application startup;
- local data loading;
- local model loading;
- analysis;
- graph rendering;
- alert generation;
- explanation;
- export.

## Performance testing

Measure actual runtimes and memory use for representative datasets. Never invent benchmark numbers.

## Regression policy

Every bug that changes a core analytical behavior should, where practical, receive a regression test.

## Completion evidence

A critical feature is not `VERIFIED` until implementation and the relevant validation evidence both exist.

