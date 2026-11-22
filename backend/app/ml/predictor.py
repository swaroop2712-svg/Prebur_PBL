"""PreBurn Machine Learning Predictor.

Uses a trained Scikit-Learn Random Forest Classifier to predict stubble-burning probability
and risk level for districts across North India for a 3-5 day horizon.
"""

import os
import logging
from typing import Dict, Any, Tuple
import joblib
import numpy as np

from app.ml.train import MODEL_PATH, train_model
from app.ml.dataset import FEATURE_NAMES
from app.utils.helpers import calculate_risk_level, get_risk_window_label

logger = logging.getLogger("preburn.ml.predictor")

# District historical burning baseline index (0-100) based on historical regional fire data
DISTRICT_HISTORICAL_BURNING_INDEX = {
    "ludhiana": 85.0,
    "sangrur": 82.0,
    "patiala": 76.0,
    "tarn taran": 74.0,
    "firozpur": 70.0,
    "jalandhar": 68.0,
    "moga": 66.0,
    "amritsar": 64.0,
    "faridkot": 62.0,
    "barnala": 60.0,
    "kaithal": 58.0,
    "kurukshetra": 56.0,
    "mansa": 55.0,
    "karnal": 54.0,
    "muktsar": 53.0,
    "gurdaspur": 52.0,
    "fatehabad": 51.0,
    "sirsa": 49.0,
    "bathinda": 48.0,
    "jind": 46.0,
    "fatehgarh sahib": 44.0,
    "ambala": 42.0,
    "fazilka": 38.0,
    "rohtak": 37.0,
    "kapurthala": 35.0,
    "nawanshahr": 34.0,
    "sonipat": 33.0,
    "hisar": 32.0,
    "hoshiarpur": 31.0,
    "panipat": 29.0,
    "sas nagar (mohali)": 28.0,
    "jhajjar": 27.0,
    "rupnagar": 26.0,
    "yamunanagar": 25.0,
    "bhiwani": 24.0,
    "pathankot": 22.0,
    "gurugram": 18.0,
    "faridabad": 15.0,
}


class MLPredictor:
    """Singleton-style predictor wrapping the trained Random Forest model."""

    _model = None

    @classmethod
    def get_model(cls):
        """Lazy load or train Random Forest model."""
        if cls._model is None:
            if not os.path.exists(MODEL_PATH):
                logger.info("Model file not found. Running automatic model training...")
                train_model()
            logger.info(f"Loading trained Random Forest model from {MODEL_PATH}")
            cls._model = joblib.load(MODEL_PATH)
        return cls._model

    @classmethod
    def compute_features(
        cls,
        district_name: str,
        horizon_days: int = 3,
        weather_data: Dict[str, float] = None
    ) -> Dict[str, float]:
        """Compute the 7 required input features for the ML model."""
        d_lower = district_name.strip().lower()
        hist_burning = DISTRICT_HISTORICAL_BURNING_INDEX.get(d_lower, 45.0)

        # Weather defaults or provided forecast values
        w = weather_data or {}
        temp = float(w.get("temperature", 30.5))
        humidity = float(w.get("humidity", 48.0))
        wind_speed = float(w.get("wind_speed", 10.0))
        rainfall = float(w.get("rainfall", 0.0))

        # Crop maturity (paddy harvesting readiness %):
        # Base maturity around peak season (75-88%), advancing with each horizon day
        horizon_factor = max(1, min(5, horizon_days))
        base_maturity = min(98.0, 72.0 + (hist_burning * 0.15) + (horizon_factor * 2.5))

        # Sowing-deadline pressure (wheat sowing window closing pressure 0-100):
        # As forecast horizon stretches into the optimal wheat sowing date, pressure mounts
        sowing_pressure = min(98.0, 50.0 + (hist_burning * 0.22) + (horizon_factor * 4.0))

        return {
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "wind_speed": round(wind_speed, 1),
            "rainfall": round(rainfall, 1),
            "crop_maturity": round(base_maturity, 1),
            "sowing_deadline_pressure": round(sowing_pressure, 1),
            "historical_burning_data": round(hist_burning, 1)
        }

    @classmethod
    def predict(
        cls,
        district_name: str,
        horizon_days: int = 3,
        weather_data: Dict[str, float] = None
    ) -> Tuple[float, str, str, Dict[str, float]]:
        """Run ML prediction with Random Forest model.

        Returns:
            (probability, risk_level, risk_window, feature_values)
        """
        model = cls.get_model()
        features = cls.compute_features(district_name, horizon_days, weather_data)

        # Build feature vector in exact order expected by model
        feature_vector = np.array([[
            features["temperature"],
            features["humidity"],
            features["wind_speed"],
            features["rainfall"],
            features["crop_maturity"],
            features["sowing_deadline_pressure"],
            features["historical_burning_data"]
        ]])

        # Predict probability for class 1 (burning event)
        probs = model.predict_proba(feature_vector)[0]
        # Class 1 probability
        raw_prob = probs[1] if len(probs) > 1 else probs[0]
        probability = round(float(raw_prob * 100.0), 1)

        # Clamp between 5% and 98% for realistic calibrated presentation
        probability = max(5.0, min(98.0, probability))

        risk_level = calculate_risk_level(probability)
        risk_window = get_risk_window_label(horizon_days)

        return probability, risk_level, risk_window, features
