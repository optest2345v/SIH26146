"""
SIH26146 — AI/ML Detection Engine
Fulfills REQ-009, Section 15, 16, and docs/06-ml-specification.md.
Combines unsupervised Isolation Forest anomaly scoring with a supervised Random Forest typology detector.
100% offline executable using scikit-learn.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "tx_count",
    "total_amount_btc",
    "avg_amount_btc",
    "std_amount_btc",
    "unique_ip_count",
    "ip_reuse_max",
    "unique_countries_count",
    "unique_asn_count",
    "inter_arrival_time_min",
    "burst_score",
    "velocity_tx_per_hour",
    "in_degree",
    "out_degree",
    "fan_out_ratio",
    "fan_in_ratio",
    "pagerank",
]


class AnomalyDetectionEngine:
    """
    Genuine ML detection engine providing:
    1. Unsupervised Anomaly Detection via Isolation Forest.
    2. Supervised typology classification via Random Forest.
    """

    def __init__(self, contamination: float = 0.12, random_state: int = 42):
        self.random_state = random_state
        self.contamination = contamination
        self.scaler = StandardScaler()
        
        # Unsupervised Isolation Forest
        self.isolation_forest = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )

        # Supervised Random Forest
        self.classifier = RandomForestClassifier(
            n_estimators=120,
            max_depth=6,
            random_state=random_state,
            class_weight="balanced",
            n_jobs=-1,
        )

        self.is_anomaly_fitted = False
        self.is_classifier_fitted = False

    def fit_anomaly_detector(self, X: pd.DataFrame) -> None:
        """Fits the Isolation Forest on the feature matrix."""
        features = X[FEATURE_COLUMNS].fillna(0.0).values
        scaled_features = self.scaler.fit_transform(features)
        self.isolation_forest.fit(scaled_features)
        self.is_anomaly_fitted = True

    def fit_classifier(self, X: pd.DataFrame, y: np.ndarray | pd.Series) -> None:
        """Fits the supervised Random Forest classifier on labeled training examples."""
        features = X[FEATURE_COLUMNS].fillna(0.0).values
        self.classifier.fit(features, y)
        self.is_classifier_fitted = True

    def predict_anomaly_scores(self, X: pd.DataFrame) -> np.ndarray:
        """
        Computes continuous anomaly scores in range [0.0, 1.0].
        Higher score = more anomalous.
        """
        if not self.is_anomaly_fitted:
            self.fit_anomaly_detector(X)

        features = X[FEATURE_COLUMNS].fillna(0.0).values
        scaled_features = self.scaler.transform(features)
        
        # decision_function gives negative values for anomalies, positive for normal
        raw_scores = self.isolation_forest.decision_function(scaled_features)
        
        # Invert and normalize to [0, 1] using min-max scaling
        # Typical range of decision_function is ~ [-0.3, 0.3]
        inverted = -raw_scores
        min_val = np.min(inverted)
        max_val = np.max(inverted)
        if max_val > min_val:
            normalized_scores = (inverted - min_val) / (max_val - min_val)
        else:
            normalized_scores = np.zeros_like(inverted)

        return np.round(normalized_scores, 4)

    def predict_suspicious_probabilities(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predicts probability of suspicious behavior if classifier is fitted.
        Falls back to anomaly scores if no supervised labels were provided.
        """
        if not self.is_classifier_fitted:
            return self.predict_anomaly_scores(X)

        features = X[FEATURE_COLUMNS].fillna(0.0).values
        classes = list(getattr(self.classifier, "classes_", []))
        if len(classes) <= 1:
            single_val = 1.0 if classes and classes[0] in (1, 1.0, True, "1") else 0.0
            return np.full(len(features), single_val)

        pos_idx = 1
        for idx, c in enumerate(classes):
            if c in (1, 1.0, True, "1", "suspicious", "anomalous"):
                pos_idx = idx
                break

        probs = self.classifier.predict_proba(features)[:, pos_idx]
        return np.round(probs, 4)

    def get_feature_importances(self) -> Dict[str, float]:
        """Returns relative feature importance from the supervised classifier."""
        if not self.is_classifier_fitted:
            return {f: round(1.0 / len(FEATURE_COLUMNS), 4) for f in FEATURE_COLUMNS}
        importances = self.classifier.feature_importances_
        return {f: round(float(imp), 4) for f, imp in zip(FEATURE_COLUMNS, importances)}

    def save_model(self, path: str | Path = "models/saved/ml_detector.joblib") -> None:
        """Serializes model artifacts to local disk."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, p)

    @classmethod
    def load_model(cls, path: str | Path = "models/saved/ml_detector.joblib") -> "AnomalyDetectionEngine":
        """Deserializes model artifacts from local disk."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Saved model artifact not found: {p}")
        return joblib.load(p)
