"""
SIH26146 — Feature Extraction Test Suite
Fulfills REQ-008, Section 13, 14, and docs/06-ml-specification.md.
"""

from src.ingestion.pipeline import ingest_file
from src.graph.builder import GraphBuilder
from src.features.extractor import FeatureExtractor, FEATURE_CONTRACT


def test_feature_extraction_contract():
    # Load sample CSV
    records, _ = ingest_file("data/synthetic/transactions_sample.csv")
    graph = GraphBuilder().build_graph(records)
    extractor = FeatureExtractor(graph=graph)

    df = extractor.extract_features(records)
    assert not df.empty
    assert "target_id" in df.columns

    # Verify every contracted feature is generated
    for feat_name in FEATURE_CONTRACT.keys():
        assert feat_name in df.columns, f"Missing feature from contract: {feat_name}"

    # Verify quantitative boundaries
    assert (df["burst_score"] >= 0.0).all() and (df["burst_score"] <= 1.0).all()
    assert (df["fan_out_ratio"] >= 0.0).all()
    assert (df["unique_ip_count"] >= 0).all()
