import os
import pickle

from django.conf import settings
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from startScan.models import Vulnerability

MODEL_PATH = os.path.join(settings.BASE_DIR, "ml_model.pkl")


def train_fp_model():
    """
    Train a simple ML model to predict false positives based on vulnerability features.
    This is a basic implementation for Phase 1.
    """
    # Fetch vulnerabilities with manual labels (assume some are labeled)
    vulns = Vulnerability.objects.filter(fp_confidence_score__isnull=False).values(
        "severity", "cvss_score", "name", "type", "fp_confidence_score"
    )

    if len(vulns) < 10:
        print("Not enough labeled data for training.")
        return

    # Simple features: severity, cvss_score, name length, type
    data = []
    labels = []
    for v in vulns:
        features = [
            v["severity"] or 0,
            v["cvss_score"] or 0,
            len(v["name"]) if v["name"] else 0,
            hash(v["type"]) % 1000 if v["type"] else 0,  # Simple hash for type
        ]
        data.append(features)
        labels.append(1 if v["fp_confidence_score"] > 0.5 else 0)  # Binary: FP or not

    X_train, X_test, y_train, y_test = train_test_split(
        data, labels, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model accuracy: {accuracy}")

    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)


def predict_fp(vuln):
    """
    Predict false positive confidence for a vulnerability.
    """
    if not os.path.exists(MODEL_PATH):
        return None

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    features = [
        vuln.severity,
        vuln.cvss_score or 0,
        len(vuln.name),
        hash(vuln.type) % 1000 if vuln.type else 0,
    ]

    prob = model.predict_proba([features])[0][1]  # Probability of being FP
    return prob
