"""
SIH26146 — Model Evaluation & Benchmark Metrics
Fulfills REQ-009, Section 17, 18, and docs/09-testing-validation.md.
Evaluates Precision, Recall, F1, ROC-AUC, PR-AUC, and Top-K ranking utility.
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    confusion_matrix,
)


def compute_top_k_metrics(
    y_true: np.ndarray,
    scores: np.ndarray,
    k_values: List[int] = [3, 5, 10],
) -> Dict[str, float]:
    """
    Computes Precision@K and Recall@K for prioritized alert assessment.
    """
    metrics: Dict[str, float] = {}
    ranked_indices = np.argsort(-scores)
    total_positives = max(1, int(np.sum(y_true)))

    for k in k_values:
        actual_k = min(k, len(y_true))
        top_k_indices = ranked_indices[:actual_k]
        top_k_true = y_true[top_k_indices]
        prec_k = np.sum(top_k_true) / actual_k
        rec_k = np.sum(top_k_true) / total_positives
        metrics[f"precision@{k}"] = round(float(prec_k), 4)
        metrics[f"recall@{k}"] = round(float(rec_k), 4)

    return metrics


def evaluate_detector(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Generates a full empirical benchmark report for the model.
    """
    y_true_binary = (y_true > 0).astype(int)
    y_pred_binary = (y_pred_proba >= threshold).astype(int)

    # Standard classification metrics
    prec = precision_score(y_true_binary, y_pred_binary, zero_division=0)
    rec = recall_score(y_true_binary, y_pred_binary, zero_division=0)
    f1 = f1_score(y_true_binary, y_pred_binary, zero_division=0)

    # Area under curves
    try:
        roc_val = roc_auc_score(y_true_binary, y_pred_proba)
    except Exception:
        roc_val = 0.5

    try:
        p_curve, r_curve, _ = precision_recall_curve(y_true_binary, y_pred_proba)
        pr_auc_val = auc(r_curve, p_curve)
    except Exception:
        pr_auc_val = 0.0

    cm = confusion_matrix(y_true_binary, y_pred_binary).tolist()

    # Top-K ranking metrics
    top_k = compute_top_k_metrics(y_true_binary, y_pred_proba, k_values=[3, 5, 10])
    n_samples = len(y_true)

    if n_samples < 30:
        status_label = f"Preliminary synthetic evaluation (Sample size: N={n_samples})"
        note = (
            f"Dataset size (N={n_samples}) is insufficient for reliable statistical generalization. "
            "Standard classification metrics measure synthetic anomaly discrimination across observed entities, "
            "while Precision@K measures top-ranked investigative yield."
        )
    else:
        status_label = "Hold-out partition benchmark evaluation"
        note = "Model evaluated on independent synthetic hold-out partition."

    report = {
        "status": status_label,
        "evaluation_note": note,
        "evaluation_summary": {
            "total_samples": len(y_true),
            "positive_samples": int(np.sum(y_true_binary)),
            "negative_samples": int(len(y_true_binary) - np.sum(y_true_binary)),
            "threshold": threshold,
        },
        "metrics": {
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc_val), 4),
            "pr_auc": round(float(pr_auc_val), 4),
        },
        "top_k_metrics": top_k,
        "metric_definitions": {
            "precision": "Proportion of flagged entities matching synthetic anomaly criteria",
            "recall": "Proportion of all synthetic anomaly entities correctly identified",
            "f1_score": "Harmonic mean of precision and recall",
            "roc_auc": "Area Under Receiver Operating Characteristic Curve",
            "precision@3": "Proportion of ground-truth positive cases appearing in top-3 ranked leads",
        },
        "confusion_matrix": cm,
    }
    return report
