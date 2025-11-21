"""
FairScore model loader and predictor.

Loads trained XGBoost model if available, otherwise uses placeholder.
"""

import pickle
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

MODEL_DIR = Path(__file__).parent
MODEL_PATH = MODEL_DIR / "fairscore_model.pkl"
SCALER_PATH = MODEL_DIR / "fairscore_scaler.pkl"

FEATURE_ORDER = [
    "avg_inflow",
    "avg_outflow",
    "savings_rate",
    "volatility",
    "academic_score",
    "part_time_income",
    "emi_count",
]


@dataclass
class FairScoreResult:
    score: int
    explanations: List[Dict[str, float]]
    suggestions: List[str]


class FairScoreModel:
    """
    FairScore model wrapper.
    Uses trained XGBoost if available, otherwise placeholder.
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.use_ml = False
        
        # Try to load trained model
        if MODEL_PATH.exists() and SCALER_PATH.exists():
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                with open(SCALER_PATH, "rb") as f:
                    self.scaler = pickle.load(f)
                self.use_ml = True
                print("Loaded trained XGBoost model")
            except Exception as e:
                print(f"Failed to load model: {e}. Using placeholder.")
                self._init_placeholder()
        else:
            print("No trained model found. Using placeholder.")
            self._init_placeholder()

    def _init_placeholder(self):
        """Initialize placeholder weights."""
        self.feature_weights = {
            "avg_monthly_inflow": 0.0005,
            "avg_monthly_outflow": -0.0003,
            "savings_rate": 30,
            "volatility": -20,
            "part_time_income": 0.001,
            "academic_score": 5,
            "emi_count": -2,
        }

    def predict(self, features: Dict[str, float]) -> FairScoreResult:
        """
        Predict FairScore from user features.
        
        Args:
            features: Dict with keys matching FEATURE_ORDER (or avg_monthly_inflow/outflow)
        
        Returns:
            FairScoreResult with score, explanations, suggestions
        """
        # Normalize feature names (handle both avg_monthly_inflow and avg_inflow)
        normalized = {}
        for key, value in features.items():
            # Map frontend names to backend names
            if key == "avg_monthly_inflow":
                normalized["avg_inflow"] = value
                normalized["avg_monthly_inflow"] = value  # Keep both for placeholder
            elif key == "avg_monthly_outflow":
                normalized["avg_outflow"] = value
                normalized["avg_monthly_outflow"] = value  # Keep both for placeholder
            else:
                normalized[key] = value
        
        if self.use_ml and self.model and self.scaler:
            return self._predict_ml(normalized)
        else:
            return self._predict_placeholder(normalized)

    def _predict_ml(self, features: Dict[str, float]) -> FairScoreResult:
        """Predict using trained XGBoost model."""
        # Build feature vector in correct order
        feature_vec = np.array([[features.get(f, 0) for f in FEATURE_ORDER]])
        
        # Scale
        feature_vec_scaled = self.scaler.transform(feature_vec)
        
        # Predict
        score = self.model.predict(feature_vec_scaled)[0]
        score = max(0, min(100, int(score)))
        
        # Get SHAP-like feature contributions (using feature importance approximation)
        # For MVP, use simple difference-based contributions
        contributions = []
        base_features = np.zeros((1, len(FEATURE_ORDER)))
        base_pred = self.model.predict(self.scaler.transform(base_features))[0]
        
        for i, feat_name in enumerate(FEATURE_ORDER):
            feat_value = features.get(feat_name, 0)
            if feat_value != 0:
                # Approximate contribution by setting feature to 0
                test_features = feature_vec_scaled.copy()
                test_features[0, i] = 0
                pred_without = self.model.predict(test_features)[0]
                contribution = score - pred_without
                contributions.append({
                    "feature": feat_name,
                    "contribution": round(contribution, 2),
                })
        
        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        top3 = contributions[:3]
        
        suggestions = self._generate_suggestions(features, top3)
        
        return FairScoreResult(score=score, explanations=top3, suggestions=suggestions)

    def _predict_placeholder(self, features: Dict[str, float]) -> FairScoreResult:
        """Predict using placeholder weighted sum."""
        base = 50
        contributions = []
        score = base
        
        # Map to placeholder feature names
        mapped_features = {
            "avg_monthly_inflow": features.get("avg_inflow", features.get("avg_monthly_inflow", 0)),
            "avg_monthly_outflow": features.get("avg_outflow", features.get("avg_monthly_outflow", 0)),
            "savings_rate": features.get("savings_rate", 0),
            "volatility": features.get("volatility", 0),
            "part_time_income": features.get("part_time_income", 0),
            "academic_score": features.get("academic_score", 0),
            "emi_count": features.get("emi_count", 0),
        }
        
        for feat, weight in self.feature_weights.items():
            value = mapped_features.get(feat, 0)
            contribution = value * weight
            contributions.append({"feature": feat, "contribution": round(contribution, 2)})
            score += contribution
        
        bounded_score = max(0, min(100, int(score)))
        sorted_contribs = sorted(contributions, key=lambda c: abs(c["contribution"]), reverse=True)[:3]
        suggestions = self._generate_suggestions(mapped_features, sorted_contribs)
        
        return FairScoreResult(score=bounded_score, explanations=sorted_contribs, suggestions=suggestions)

    def _generate_suggestions(self, features: Dict[str, float], top_contribs: List[Dict]) -> List[str]:
        """Generate improvement suggestions based on top contributions."""
        suggestions = []
        
        for contrib in top_contribs:
            feat = contrib["feature"]
            contrib_val = contrib["contribution"]
            
            if feat == "savings_rate" and contrib_val < 0:
                suggestions.append("Increase savings rate by automating monthly transfers.")
            elif feat == "volatility" and contrib_val < 0:
                suggestions.append("Reduce spending volatility by smoothing bill payments.")
            elif feat == "academic_score" and contrib_val < 0:
                suggestions.append("Improve academic performance to boost FairScore.")
            elif feat == "emi_count" and contrib_val < 0:
                suggestions.append("Reduce number of active EMIs to improve score.")
        
        if not suggestions:
            suggestions = [
                "Maintain consistent savings pattern.",
                "Reduce spending volatility for better score.",
            ]
        
        return suggestions[:3]


# Global model instance
model = FairScoreModel()
