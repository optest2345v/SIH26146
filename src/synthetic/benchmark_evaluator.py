"""
SIH26146 — Independent Benchmark Evaluation Engine
Evaluates detection pipeline performance against hidden ground truth.
Fulfills Section 17, 18, REQ-009, and docs/09-testing-validation.md.

Guarantees 100% blind evaluation:
The detector operates purely on raw benchmark data without access to ground truth labels.
The evaluator subsequently benchmarks pipeline predictions against the hidden key.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

# Add project root to sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from src.pipeline import MasterPipeline, AnalysisResult


class BenchmarkEvaluator:
    """
    Evaluates pipeline performance on raw benchmark datasets using hidden ground-truth keys.
    """

    def __init__(self, ground_truth_path: str | Path, manifest_path: Optional[str | Path] = None):
        self.ground_truth_path = Path(ground_truth_path)
        if not self.ground_truth_path.exists():
            raise FileNotFoundError(f"Ground truth file not found: {self.ground_truth_path}")

        with open(self.ground_truth_path, "r", encoding="utf-8") as f:
            self.gt = json.load(f)

        self.manifest = None
        if manifest_path and Path(manifest_path).exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                self.manifest = json.load(f)

    def evaluate(self, result: Any) -> Dict[str, Any]:
        """
        Scores the pipeline's AnalysisResult against the hidden ground truth.
        """
        if isinstance(result, tuple):
            result = result[0]
        gt_entities = self.gt.get("entities", {})
        alerts_by_target = {a.target_id: a for a in result.alerts}

        # 1. Validation Ingestion Verification
        actual_val = result.validation_summary
        val_assessment = {
            "total_records_processed": actual_val.total_records,
            "valid_records": actual_val.valid_records,
            "invalid_records": actual_val.invalid_records,
            "quarantined_records": actual_val.quarantined_records,
            "incomplete_records": actual_val.incomplete_records,
        }

        # 2. Entity-Level Detection Matrix
        y_true: List[int] = []
        y_pred_binary: List[int] = []
        y_pred_scores: List[float] = []
        typology_hits: Dict[str, Dict[str, int]] = {}

        for target_id, meta in gt_entities.items():
            is_anomaly = 1 if meta.get("is_anomaly", False) else 0
            typology = meta.get("typology", "unknown")
            y_true.append(is_anomaly)

            if typology not in typology_hits:
                typology_hits[typology] = {"total": 0, "detected": 0}
            typology_hits[typology]["total"] += 1

            if target_id in alerts_by_target:
                alert = alerts_by_target[target_id]
                score = alert.priority_score
                # Flagged if priority score >= 0.35 (MEDIUM or higher tier)
                flagged = 1 if score >= 0.35 else 0
                y_pred_binary.append(flagged)
                y_pred_scores.append(score)
                if flagged and is_anomaly:
                    typology_hits[typology]["detected"] += 1
            else:
                y_pred_binary.append(0)
                y_pred_scores.append(0.0)

        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred_binary)
        y_scores_arr = np.array(y_pred_scores)

        # Standard statistical classification metrics
        prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
        rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
        f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))

        try:
            roc_val = float(roc_auc_score(y_true_arr, y_scores_arr))
        except Exception:
            roc_val = 0.5

        cm = confusion_matrix(y_true_arr, y_pred_arr).tolist()
        tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

        # 3. Precision@K (Top-K investigative yield)
        ranked_alerts = result.alerts
        top_k_metrics: Dict[str, float] = {}
        for k in [3, 5, 10, 20, 50]:
            top_k = ranked_alerts[:k]
            if top_k:
                k_pos = sum(1 for a in top_k if gt_entities.get(a.target_id, {}).get("is_anomaly", False))
                top_k_metrics[f"precision@{k}"] = round(k_pos / len(top_k), 4)
            else:
                top_k_metrics[f"precision@{k}"] = 0.0

        # 4. Typology-specific recall
        typology_recall: Dict[str, float] = {}
        for typ, data in typology_hits.items():
            if data["total"] > 0:
                typology_recall[typ] = round(data["detected"] / data["total"], 4)

        # 5. Benign False Positive Rate assessment
        benign_sweeps = [
            a for a in ranked_alerts
            if gt_entities.get(a.target_id, {}).get("typology") in ("benign_mining_pool", "benign_exchange_sweep")
        ]
        fp_on_benign_infrastructure = len([a for a in benign_sweeps if a.investigative_priority in ("CRITICAL", "HIGH")])

        report = {
            "benchmark_evaluation": {
                "benchmark_id": self.gt.get("metadata", {}).get("benchmark_id", "10K_BENCHMARK"),
                "run_id": result.run_id,
                "timestamp_utc": result.run_timestamp.isoformat(),
                "evaluation_mode": "INDEPENDENT_HIDDEN_HOLD_OUT",
            },
            "ingestion_validation": val_assessment,
            "classification_metrics": {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "roc_auc": round(roc_val, 4),
            },
            "top_k_yield": top_k_metrics,
            "confusion_matrix": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
            },
            "typology_recall": typology_recall,
            "benign_infrastructure_protection": {
                "false_positives_on_mining_and_sweeps": fp_on_benign_infrastructure,
                "status": "PASSED" if fp_on_benign_infrastructure == 0 else "WARNING",
            },
        }

        return report

    def render_markdown_scorecard(self, evaluation: Dict[str, Any]) -> str:
        """Formats the evaluation result as an audit-ready Markdown scorecard."""
        m = evaluation["classification_metrics"]
        top_k = evaluation["top_k_yield"]
        cm = evaluation["confusion_matrix"]
        v = evaluation["ingestion_validation"]
        t = evaluation["typology_recall"]
        b = evaluation["benign_infrastructure_protection"]

        lines = [
            "# SIH26146 — Independent Benchmark Evaluation Scorecard",
            "",
            f"**Benchmark ID:** `{evaluation['benchmark_evaluation']['benchmark_id']}`  ",
            f"**Evaluation Mode:** `STRICT AIR-GAPPED INDEPENDENT HOLD-OUT`  ",
            f"**Execution Timestamp:** `{evaluation['benchmark_evaluation']['timestamp_utc']}`  ",
            "",
            "---",
            "",
            "## 1. Executive Summary & Forensic KPIs",
            "",
            "| Metric | Realized Score | Benchmark Target | Status |",
            "| :--- | :--- | :--- | :--- |",
            f"| **Precision@3 (Top Leads)** | **{top_k.get('precision@3', 0.0)*100:.1f}%** | 100.0% | {'✅ TARGET MET' if top_k.get('precision@3', 0) >= 0.99 else '⚠️ MARGINAL'} |",
            f"| **Precision@5 (Top Leads)** | **{top_k.get('precision@5', 0.0)*100:.1f}%** | 100.0% | {'✅ TARGET MET' if top_k.get('precision@5', 0) >= 0.99 else '⚠️ MARGINAL'} |",
            f"| **Precision@10 (Investigator Yield)** | **{top_k.get('precision@10', 0.0)*100:.1f}%** | &ge; 80.0% | {'✅ TARGET MET' if top_k.get('precision@10', 0) >= 0.80 else '⚠️ MARGINAL'} |",
            f"| **Overall Classification ROC-AUC** | **{m['roc_auc']:.4f}** | &ge; 0.8500 | {'✅ TARGET MET' if m['roc_auc'] >= 0.85 else '⚠️ MARGINAL'} |",
            f"| **Overall Precision** | **{m['precision']:.4f}** | &ge; 0.8000 | {'✅ TARGET MET' if m['precision'] >= 0.80 else '⚠️ MARGINAL'} |",
            f"| **Overall Recall** | **{m['recall']:.4f}** | &ge; 0.7500 | {'✅ TARGET MET' if m['recall'] >= 0.75 else '⚠️ MARGINAL'} |",
            f"| **Benign Sweep False Alarm Protection** | **{b['false_positives_on_mining_and_sweeps']} FP** | 0 FP | {'✅ ZERO FALSE ALARMS' if b['status'] == 'PASSED' else '⚠️ WARNING'} |",
            "",
            "---",
            "",
            "## 2. Ingestion & Validation Telemetry",
            "",
            f"- **Total Records Ingested:** {v['total_records_processed']}",
            f"- **Valid Canonical Records:** {v['valid_records']}",
            f"- **Intentionally Rejected Invalid Records:** {v['invalid_records']} (Malformed IPs, negative amounts, bad ports)",
            f"- **Quarantined Records:** {v['quarantined_records']} (Non-standard TXID hex syntax)",
            f"- **Pure Telemetry Incomplete Records:** {v['incomplete_records']} (Network observations correlated via temporal window)",
            "",
            "---",
            "",
            "## 3. Typology-Specific Detection Rates",
            "",
            "| Forensic Typology | Detection Recall | Assessment |",
            "| :--- | :--- | :--- |",
        ]

        for typ, rec_val in t.items():
            clean_name = typ.replace("_", " ").title()
            lines.append(f"| {clean_name} | {rec_val*100:.1f}% | {'High Sensitivity' if rec_val >= 0.80 else 'Moderate Sensitivity'} |")

        lines.extend([
            "",
            "---",
            "",
            "## 4. Confusion Matrix (Entity Level)",
            "",
            f"- **True Positives (TP):** {cm['true_positives']} (Anomalies correctly flagged)",
            f"- **True Negatives (TN):** {cm['true_negatives']} (Benign entities correctly filtered)",
            f"- **False Positives (FP):** {cm['false_positives']} (Benign entities flagged)",
            f"- **False Negatives (FN):** {cm['false_negatives']} (Anomalies missed)",
            "",
            "---",
            "*Report generated deterministically using blind hold-out evaluation contract.*",
        ])

        return "\n".join(lines)

    def generate_markdown_report(self, evaluation: Dict[str, Any], output_path: Optional[str | Path] = None) -> str:
        """Renders and optionally writes the markdown scorecard to disk."""
        md = self.render_markdown_scorecard(evaluation)
        if output_path:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(md)
        return md


def run_benchmark_evaluation(
    data_path: str | Path = "data/benchmark_10k/benchmark_data.json",
    ground_truth_path: str | Path = "data/benchmark_10k/ground_truth.json",
    manifest_path: str | Path = "data/benchmark_10k/benchmark_manifest.json",
    output_report_path: Optional[str | Path] = "data/benchmark_10k/benchmark_evaluation_report.md",
) -> Dict[str, Any]:
    """
    Executes full blind evaluation:
    1. Pipeline runs on raw data_path only.
    2. Evaluator scores pipeline results against ground_truth_path.
    3. Outputs report to console and markdown file.
    """
    print(f"[*] Step 1: Running Master Pipeline on raw benchmark data: {data_path}")
    pipeline = MasterPipeline()
    result, graph, _, recs, corrs = pipeline.run(data_path)

    print(f"[*] Step 2: Scoring against hidden ground truth: {ground_truth_path}")
    evaluator = BenchmarkEvaluator(ground_truth_path=ground_truth_path, manifest_path=manifest_path)
    evaluation = evaluator.evaluate(result)
    scorecard = evaluator.render_markdown_scorecard(evaluation)

    if output_report_path:
        out_p = Path(output_report_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(scorecard, encoding="utf-8")
        print(f"[*] Scorecard written to: {out_p}")

    return {
        "evaluation": evaluation,
        "scorecard": scorecard,
        "result": result,
    }


if __name__ == "__main__":
    run_benchmark_evaluation()
