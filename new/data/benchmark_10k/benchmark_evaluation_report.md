# SIH26146 — Independent Benchmark Evaluation Scorecard

**Benchmark ID:** `SIH26146-BENCHMARK-10K-42`  
**Evaluation Mode:** `STRICT AIR-GAPPED INDEPENDENT HOLD-OUT`  
**Execution Timestamp:** `2026-10-04T06:06:27.360092+00:00`  

---

## 1. Executive Summary & Forensic KPIs

| Metric | Realized Score | Benchmark Target | Status |
| :--- | :--- | :--- | :--- |
| **Precision@3 (Top Leads)** | **100.0%** | 100.0% | ✅ TARGET MET |
| **Precision@5 (Top Leads)** | **100.0%** | 100.0% | ✅ TARGET MET |
| **Precision@10 (Investigator Yield)** | **100.0%** | &ge; 80.0% | ✅ TARGET MET |
| **Overall Classification ROC-AUC** | **0.9944** | &ge; 0.8500 | ✅ TARGET MET |
| **Overall Precision** | **0.4685** | &ge; 0.8000 | ⚠️ MARGINAL |
| **Overall Recall** | **1.0000** | &ge; 0.7500 | ✅ TARGET MET |
| **Benign Sweep False Alarm Protection** | **1 FP** | 0 FP | ⚠️ WARNING |

---

## 2. Ingestion & Validation Telemetry

- **Total Records Ingested:** 10250
- **Valid Canonical Records:** 10180
- **Intentionally Rejected Invalid Records:** 15 (Malformed IPs, negative amounts, bad ports)
- **Quarantined Records:** 55 (Non-standard TXID hex syntax)
- **Pure Telemetry Incomplete Records:** 0 (Network observations correlated via temporal window)

---

## 3. Typology-Specific Detection Rates

| Forensic Typology | Detection Recall | Assessment |
| :--- | :--- | :--- |
| Benign Retail | 0.0% | Moderate Sensitivity |
| Benign Mining Pool | 0.0% | Moderate Sensitivity |
| Benign Exchange Sweep | 0.0% | Moderate Sensitivity |
| Peeling Chain | 100.0% | High Sensitivity |
| High Velocity Burst | 100.0% | High Sensitivity |
| Structuring Fanout | 100.0% | High Sensitivity |
| Rapid Geo Hopping | 100.0% | High Sensitivity |

---

## 4. Confusion Matrix (Entity Level)

- **True Positives (TP):** 52 (Anomalies correctly flagged)
- **True Negatives (TN):** 843 (Benign entities correctly filtered)
- **False Positives (FP):** 59 (Benign entities flagged)
- **False Negatives (FN):** 0 (Anomalies missed)

---
*Report generated deterministically using blind hold-out evaluation contract.*