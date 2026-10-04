"""
SIH26146 — AI/ML Detection Engine Test Suite
Fulfills REQ-009, Section 15, 16, 17, 18, and docs/06-ml-specification.md.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from src.ingestion.pipeline import ingest_file
from src.graph.builder import GraphBuilder
from src.features.extractor import FeatureExtractor
from src.ml.model import AnomalyDetectionEngine, FEATURE_COLUMNS
from src.ml.evaluator import evaluate_detector, compute_top_k_metrics


def test_ml_anomaly_detector_fit_and_predict():
    records, _ = ingest_file("data/synthetic/transactions_sample.csv")
    graph = GraphBuilder().build_graph(records)
    df = FeatureExtractor(graph=graph).extract_features(records)

    engine = AnomalyDetectionEngine(contamination=0.15, random_state=42)
    engine.fit_anomaly_detector(df)

    scores = engine.predict_anomaly_scores(df)
    assert len(scores) == len(df)
    assert (scores >= 0.0).all() and (scores <= 1.0).all()


def test_ml_supervised_classifier_and_metrics():
    records, _ = ingest_file("data/synthetic/transactions_sample.csv")
    graph = GraphBuilder().build_graph(records)
    df = FeatureExtractor(graph=graph).extract_features(records)

    # Synthetic labels
    y = np.zeros(len(df))
    y[:5] = 1.0  # Mark first 5 as suspicious

    engine = AnomalyDetectionEngine(random_state=42)
    engine.fit_classifier(df, y)

    probs = engine.predict_suspicious_probabilities(df)
    assert len(probs) == len(df)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    # Evaluator metrics
    report = evaluate_detector(y, probs, threshold=0.5)
    assert "metrics" in report
    assert "precision" in report["metrics"]
    assert "recall" in report["metrics"]
    assert "roc_auc" in report["metrics"]
    assert "top_k_metrics" in report
    assert "precision@3" in report["top_k_metrics"]


def test_ml_model_offline_serialization(tmp_path: Path):
    records, _ = ingest_file("data/synthetic/transactions_sample.csv")
    df = FeatureExtractor().extract_features(records)

    engine = AnomalyDetectionEngine(random_state=42)
    engine.fit_anomaly_detector(df)

    save_path = tmp_path / "model_test.joblib"
    engine.save_model(save_path)
    assert save_path.exists()

    loaded = AnomalyDetectionEngine.load_model(save_path)
    scores = loaded.predict_anomaly_scores(df)
    assert len(scores) == len(df)
