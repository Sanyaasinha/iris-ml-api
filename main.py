"""Flask REST API that serves the Iris classifier.

Endpoints
  GET  /health   -> liveness check (used by Docker/EC2 health checks)
  GET  /info     -> which container/host served the request
  POST /predict  -> {"features": [sepal_len, sepal_wid, petal_len, petal_wid]}
"""
import os
import socket

import joblib
from flask import Flask, jsonify, request

from app.train import MODEL_PATH, train

FEATURE_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]


def load_model(path: str = MODEL_PATH):
    if not os.path.exists(path):
        train(path)  # first start without a baked model: train on the fly
    return joblib.load(path)


def create_app(model_path: str = MODEL_PATH) -> Flask:
    app = Flask(__name__)
    bundle = load_model(model_path)
    model, classes = bundle["model"], bundle["classes"]

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/info")
    def info():
        return jsonify(hostname=socket.gethostname(), version=os.environ.get("APP_VERSION", "dev"))

    @app.post("/predict")
    def predict():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or "features" not in data:
            return jsonify(error="JSON body must contain a 'features' list"), 400
        features = data["features"]
        if (
            not isinstance(features, list)
            or len(features) != len(FEATURE_NAMES)
            or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in features)
        ):
            return jsonify(error=f"'features' must be a list of {len(FEATURE_NAMES)} numbers: {FEATURE_NAMES}"), 400
        if any(v < 0 for v in features):
            return jsonify(error="feature values must be non-negative"), 400

        probs = model.predict_proba([features])[0]
        best = int(probs.argmax())
        return jsonify(
            prediction=classes[best],
            confidence=round(float(probs[best]), 4),
            probabilities={c: round(float(p), 4) for c, p in zip(classes, probs)},
        )

    return app


# Module-level app for gunicorn ("app.main:app"). Tests build their own via create_app().
app = create_app() if os.environ.get("CREATE_APP_ON_IMPORT", "1") == "1" else None
