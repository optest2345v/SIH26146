"""
SIH26146 — Alert Generation & Ranking Test Suite
Fulfills REQ-010, REQ-011, Section 20, 21, 22.
"""

from src.ingestion.pipeline import ingest_file
from src.correlation.engine import CorrelationEngine
from src.graph.builder import GraphBuilder
from src.features.extractor import FeatureExtractor
from src.ml.model import AnomalyDetectionEngine
from src.alerts.engine import AlertEngine, AlertRanker


def test_alert_ranking_and_separation():
    records, _ = ingest_file("data/synthetic/transactions_sample.csv")
    corrs = CorrelationEngine().correlate(records)
    graph = GraphBuilder().build_graph(records, corrs)
    df = FeatureExtractor(graph=graph).extract_features(records)

    ml = AnomalyDetectionEngine()
    anomaly_scores = ml.predict_anomaly_scores(df)
    probs = anomaly_scores  # Unsupervised fallback

    engine = AlertEngine()
    alerts = engine.generate_alerts(
        feature_df=df,
        anomaly_scores=anomaly_scores,
        classifier_probs=probs,
        correlations=corrs,
        min_priority_threshold=0.1,
    )

    assert len(alerts) > 0

    # Test 1: Priority score descending order
    for i in range(len(alerts) - 1):
        assert alerts[i].priority_score >= alerts[i+1].priority_score

    # Test 2: Separation of concepts
    # Anomaly score, correlation confidence, and priority score must be independently populated
    for a in alerts:
        assert 0.0 <= a.anomaly_score <= 1.0
        assert 0.0 <= a.correlation_confidence <= 1.0
        assert 0.0 <= a.priority_score <= 1.0
        assert len(a.primary_reasons) > 0
        assert a.explanation_narrative is not None
        assert "investigative lead" in a.disclaimer.lower()
