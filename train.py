"""Train a small Iris classifier and save it to disk.

Run:  python -m app.train
"""
import os

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_PATH = os.environ.get("MODEL_PATH", "model/iris_model.joblib")


def train(model_path: str = MODEL_PATH) -> float:
    """Train the model, save it, and return accuracy on a held-out test split."""
    iris = load_iris()
    x_train, x_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target
    )
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(x_train, y_train)
    accuracy = float(model.score(x_test, y_test))

    os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)
    joblib.dump({"model": model, "classes": list(iris.target_names)}, model_path)
    return accuracy


if __name__ == "__main__":
    acc = train()
    print(f"Model trained and saved to {MODEL_PATH} (test accuracy: {acc:.3f})")
