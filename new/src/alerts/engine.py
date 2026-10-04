"""
SIH26146 — Alert Ranking & Evidence Fusion Engine
Fulfills REQ-010, REQ-011, Section 21, 22, and docs/10-decisions.md (ADR-002).
Explicitly separates anomaly score, correlation confidence, and investigative priority.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.models.schema import Alert, InvestigativePriority, TargetType, CorrelationRecord
from src.ml.explainer import LeadExplainer


class AlertRanker:
    """
    Combines machine learning anomaly scores, classifier probabilities,
    correlation confidence, and graph topological signals into ranked investigative leads.
    """

    def __init__(
        self,
        weight_anomaly: float = 0.35,
        weight_classifier: float = 0.30,
        weight_correlation: float = 0.20,
        weight_graph: float = 0.15,
    ):
        # Validate weights sum to 1.0
        total = weight_anomaly + weight_classifier + weight_correlation + weight_graph
        self.w_anomaly = weight_anomaly / total
        self.w_classifier = weight_classifier / total
        self.w_correlation = weight_correlation / total
        self.w_graph = weight_graph / total

    def compute_priority_score(
        self,
        anomaly_score: float,
        classifier_prob: float,
        correlation_confidence: float,
        graph_structural_risk: float,
    ) -> float:
        """
        Fused investigative priority formula:
        Priority = w1*Anomaly + w2*Classifier + w3*Confidence + w4*GraphRisk
        """
        score = (
            self.w_anomaly * anomaly_score
            + self.w_classifier * classifier_prob
            + self.w_correlation * correlation_confidence
            + self.w_graph * graph_structural_risk
        )
        return round(float(np.clip(score, 0.0, 1.0)), 4)

    def classify_priority_tier(self, score: float) -> InvestigativePriority:
        """Categorizes raw priority score into operational actionability tiers."""
        if score >= 0.75:
            return InvestigativePriority.CRITICAL
        elif score >= 0.55:
            return InvestigativePriority.HIGH
        elif score >= 0.35:
            return InvestigativePriority.MEDIUM
        else:
            return InvestigativePriority.LOW


class AlertEngine:
    """
    Coordinates feature matrix evaluation, explainability synthesis, priority ranking,
    and structured Alert generation.
    """

    def __init__(self, ranker: Optional[AlertRanker] = None):
        self.ranker = ranker or AlertRanker()

    def generate_alerts(
        self,
        feature_df: pd.DataFrame,
        anomaly_scores: np.ndarray,
        classifier_probs: np.ndarray,
        correlations: List[CorrelationRecord],
        feature_importances: Optional[Dict[str, float]] = None,
        min_priority_threshold: float = 0.25,
    ) -> List[Alert]:
        """
        Produces ranked, explainable Alert objects for entities breaching investigative thresholds.
        """
        if feature_df.empty:
            return []

        # Index correlations by wallet / txid references
        target_to_confidence: Dict[str, float] = {}
        target_to_corrs: Dict[str, List[CorrelationRecord]] = {}
        for c in correlations:
            for w in c.wallet_references:
                target_to_confidence[w] = max(target_to_confidence.get(w, 0.0), c.correlation_confidence)
                target_to_corrs.setdefault(w, []).append(c)
            target_to_confidence[c.txid] = max(target_to_confidence.get(c.txid, 0.0), c.correlation_confidence)
            target_to_corrs.setdefault(c.txid, []).append(c)

        explainer = LeadExplainer(baseline_df=feature_df)
        alerts: List[Alert] = []

        for idx, row in feature_df.iterrows():
            target_id = str(row["target_id"])
            anomaly_score = float(anomaly_scores[idx])
            classifier_prob = float(classifier_probs[idx])
            
            # --- 1. Multi-Signal Evidence Fusion Confidence ---
            # Component A: Network Correlation Confidence (Derived directly from telemetry linkage)
            corr_conf = round(float(target_to_confidence.get(target_id, 0.65)), 2)

            # Component B: Behavioral Confidence (Strength of statistical/behavioral deviations)
            burst = float(row.get("burst_score", 0.0))
            amt = float(row.get("total_amount_btc", 0.0))
            fan_out = float(row.get("fan_out_ratio", 1.0))
            fan_in = float(row.get("fan_in_ratio", 1.0))
            tx_cnt = int(row.get("tx_count", 1))

            behav_conf = round(float(np.clip(
                0.55 + 0.20 * burst + 0.15 * min(1.0, amt / 5.0) + (0.10 if tx_cnt > 1 else 0.0),
                0.50, 0.95
            )), 2)

            # Component C: Graph Structural Confidence (Centrality & flow certainty)
            in_deg = int(row.get("in_degree", 0))
            out_deg = int(row.get("out_degree", 0))
            pr_val = float(row.get("pagerank", 0.0))
            graph_conf = round(float(np.clip(
                0.52 + 0.20 * min(1.0, (in_deg + out_deg) / 6.0) + 0.15 * min(1.0, max(fan_out, fan_in) / 4.0) + 0.10 * min(1.0, pr_val * 10.0),
                0.50, 0.96
            )), 2)

            # Component D: Temporal Consistency Confidence
            inter_arrival = float(row.get("inter_arrival_time_min", 3600.0))
            temp_conf = round(float(np.clip(
                0.55 + 0.25 * burst + (0.15 if inter_arrival <= 60.0 else 0.0) + (0.05 if tx_cnt > 1 else 0.0),
                0.50, 0.95
            )), 2)

            # Component E: Fused Multi-Signal Confidence
            fused_conf = round(float(0.35 * corr_conf + 0.25 * behav_conf + 0.20 * graph_conf + 0.20 * temp_conf), 2)

            confidence_breakdown = {
                "network_correlation_confidence": corr_conf,
                "behavioral_deviation_confidence": behav_conf,
                "graph_structural_confidence": graph_conf,
                "temporal_consistency_confidence": temp_conf,
                "fused_multi_signal_confidence": fused_conf,
            }

            # Compute graph structural risk signal (elevated for extreme fan-in or fan-out)
            graph_risk = min(1.0, max(0.0, (max(fan_out, fan_in) - 1.0) / 4.0))

            priority_score = self.ranker.compute_priority_score(
                anomaly_score=anomaly_score,
                classifier_prob=classifier_prob,
                correlation_confidence=fused_conf,
                graph_structural_risk=graph_risk,
            )

            # Filter out purely benign normal baselines below threshold
            if priority_score < min_priority_threshold:
                continue

            priority_tier = self.ranker.classify_priority_tier(priority_score)
            
            # Synthesize explanations
            explanation_pack = explainer.explain_target(
                features=row.to_dict(),
                anomaly_score=anomaly_score,
                correlation_confidence=fused_conf,
                feature_importances=feature_importances,
            )

            target_type = TargetType.TRANSACTION if target_id.startswith("TX:") or len(target_id) == 64 else TargetType.WALLET

            # Build rich structured provenance details
            target_corrs = target_to_corrs.get(target_id, [])
            associated_txids = list(set(c.txid for c in target_corrs if c.txid))
            raw_rec_ids = row.get("source_record_ids", [])
            source_files = sorted(list(set(s.split("#")[0] for s in raw_rec_ids if "#" in s)))
            source_rows = [s.split("#")[-1] if "#" in s else s for s in raw_rec_ids]

            provenance_details = {
                "source_files": source_files or ["unknown"],
                "source_records": source_rows,
                "observation_count": tx_cnt,
                "associated_txids": associated_txids[:5],
                "correlation_methods": sorted(list(set(m for c in target_corrs for m in c.match_methods))),
            }

            alert = Alert(
                alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                target_id=target_id,
                target_type=target_type,
                investigative_priority=priority_tier,
                priority_score=priority_score,
                anomaly_score=anomaly_score,
                correlation_confidence=corr_conf,
                fused_confidence=fused_conf,
                confidence_breakdown=confidence_breakdown,
                provenance_details=provenance_details,
                primary_reasons=explanation_pack["primary_reasons"],
                model_evidence=explanation_pack["model_evidence"],
                graph_evidence=explanation_pack["graph_evidence"],
                temporal_evidence=explanation_pack["temporal_evidence"],
                correlation_evidence=explanation_pack["correlation_evidence"],
                source_record_ids=raw_rec_ids,
                explanation_narrative=explanation_pack["explanation_narrative"],
            )
            alerts.append(alert)

        # Sort strictly in descending order of investigative priority score
        alerts.sort(key=lambda a: -a.priority_score)
        return alerts
