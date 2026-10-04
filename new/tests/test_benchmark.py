"""
Tests for 10,000+ Forensic Benchmark Generator and Blind Evaluator.
Fulfills REQ-009, REQ-013, and docs/09-testing-validation.md.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
import pytest

from src.synthetic.benchmark_generator import Benchmark10KGenerator
from src.synthetic.benchmark_evaluator import BenchmarkEvaluator
from src.pipeline import MasterPipeline


class TestBenchmarkGenerator:
    """Validates benchmark generator correctness and zero-leakage guarantee."""

    def test_benchmark_generation_structure_and_no_leakage(self, tmp_path):
        """Verify generator creates valid records, manifest, and hidden ground truth without leakage."""
        gen = Benchmark10KGenerator(seed=123)
        records, ground_truth, manifest = gen.generate()

        assert len(records) >= 10000
        assert "entities" in ground_truth
        assert "transactions" in ground_truth
        assert "records" in ground_truth
        assert "benchmark_manifest" in manifest

        # Strict check for zero hint leakage in raw records
        forbidden_leakage_keys = {"scenario_label", "ground_truth", "is_anomalous", "typology"}
        sample = records[:50]
        for r in sample:
            assert "source_row_id" in r
            assert "timestamp" in r
            assert "txid" in r
            assert "input_addresses" in r
            assert "output_addresses" in r
            assert "src_ip" in r
            assert "dst_ip" in r
            for forbidden in forbidden_leakage_keys:
                assert forbidden not in r, f"Leakage detected: raw record contains '{forbidden}'"

        # Check export to files
        export_res = gen.export_all(tmp_path)
        assert Path(export_res["json_data"]).exists()
        assert Path(export_res["csv_data"]).exists()
        assert Path(export_res["xml_data"]).exists()
        assert Path(export_res["ground_truth"]).exists()
        assert Path(export_res["manifest"]).exists()

        # Validate that JSON file parses properly
        with open(export_res["json_data"], "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["schema_version"] == "1.0.0"
            assert len(data["records"]) == len(records)


class TestBenchmarkEvaluator:
    """Validates blind benchmark evaluation against ground truth."""

    def test_evaluator_scoring(self, tmp_path):
        """Test evaluator scoring pipeline results against ground truth."""
        # Use existing pre-generated benchmark or test files
        gt_path = Path("data/benchmark_10k/ground_truth.json")
        manifest_path = Path("data/benchmark_10k/benchmark_manifest.json")
        json_data_path = Path("data/benchmark_10k/benchmark_data.json")

        if not gt_path.exists() or not json_data_path.exists():
            pytest.skip("Benchmark 10k dataset not yet generated in data/benchmark_10k")

        evaluator = BenchmarkEvaluator(gt_path, manifest_path)
        assert evaluator.gt is not None
        assert "entities" in evaluator.gt

        # Run pipeline on a small subset or full dataset if fast enough
        # We test running evaluator with a pipeline result
        pipeline = MasterPipeline()
        # Ingest directly from data file
        pipeline_result = pipeline.run(str(json_data_path))
        eval_result = evaluator.evaluate(pipeline_result)

        assert "classification_metrics" in eval_result
        metrics = eval_result["classification_metrics"]
        assert "precision" in metrics
        assert "recall" in metrics
        assert "roc_auc" in metrics
        assert metrics["roc_auc"] >= 0.85

        assert "top_k_yield" in eval_result
        top_k = eval_result["top_k_yield"]
        assert "precision@3" in top_k
        assert top_k["precision@3"] >= 0.90

        # Test markdown report generation
        report_path = tmp_path / "test_report.md"
        evaluator.generate_markdown_report(eval_result, report_path)
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        assert "Independent Benchmark Evaluation Scorecard" in content
