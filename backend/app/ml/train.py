"""Train and persist Random Forest Classifier for PreBurn Stubble Burning Risk Prediction."""

import os
import json
import logging
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score
from app.ml.dataset import generate_synthetic_dataset, FEATURE_NAMES, DATASET_PATH

logger = logging.getLogger("preburn.ml.train")

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "stubble_rf_model.joblib")
METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")


def train_model(force_dataset_regen: bool = False) -> str:
    """Train Random Forest model using the dataset and persist to disk."""
    os.makedirs(MODELS_DIR, exist_ok=True)

    # 1. Ensure dataset exists
    if not os.path.exists(DATASET_PATH) or force_dataset_regen:
        logger.info("Generating synthetic training dataset...")
        generate_synthetic_dataset(num_samples=2500)

    # 2. Load dataset with numpy
    data = np.genfromtxt(DATASET_PATH, delimiter=",", skip_header=1)
    X = data[:, :-1]
    y = data[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Train Random Forest Classifier
    rf = RandomForestClassifier(
        n_estimators=120,
        max_depth=9,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)

    # 4. Evaluate
    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1]

    acc = round(float(accuracy_score(y_test, y_pred)), 4)
    roc = round(float(roc_auc_score(y_test, y_prob)), 4)
    prec = round(float(precision_score(y_test, y_pred)), 4)
    rec = round(float(recall_score(y_test, y_pred)), 4)

    # Feature importances
    importances = {
        name: round(float(imp), 4)
        for name, imp in zip(FEATURE_NAMES, rf.feature_importances_)
    }

    metrics = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 120,
        "max_depth": 9,
        "accuracy": acc,
        "roc_auc": roc,
        "precision": prec,
        "recall": rec,
        "feature_names": FEATURE_NAMES,
        "feature_importances": importances,
        "training_samples": len(X_train),
        "test_samples": len(X_test)
    }

    # 5. Persist model and metrics
    joblib.dump(rf, MODEL_PATH)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    logger.info(
        f"Random Forest model saved to {MODEL_PATH} "
        f"(Accuracy: {acc*100:.1f}%, ROC-AUC: {roc:.3f})"
    )
    return MODEL_PATH


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_model()
