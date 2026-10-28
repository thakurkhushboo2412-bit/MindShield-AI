"""Train and evaluate the MindShield AI model on simulated data."""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "activity_data.csv"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
FEATURES = [
    "screen_time_hours", "late_night_hours", "blocked_site_attempts",
    "unknown_contact_attempts", "rapid_app_switches", "sleep_hours",
    "educational_usage_pct", "weekend"
]
TARGET = "risk_level"

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError("Dataset missing. Run: python generate_data.py")

    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(
            n_estimators=250, max_depth=10, min_samples_leaf=3,
            class_weight="balanced", random_state=42, n_jobs=-1
        ))
    ])
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    labels = ["Low", "Medium", "High"]

    metrics = {
        "dataset_type": "SIMULATED — rule-generated educational data",
        "rows_total": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "features": FEATURES,
        "target": TARGET,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "macro_f1": float(f1_score(y_test, predictions, average="macro")),
        "classification_report": classification_report(
            y_test, predictions, labels=labels, output_dict=True, zero_division=0
        ),
        "confusion_matrix_labels": labels,
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=labels).tolist(),
        "note": "Metrics measure agreement with synthetic rule-generated labels only. They do not establish real-world child-safety accuracy."
    }

    MODEL_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "classes": list(model.classes_)},
                MODEL_DIR / "risk_model.joblib")
    with open(REPORT_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Model training complete.")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Macro F1: {metrics['macro_f1']:.3f}")
    print(classification_report(y_test, predictions, labels=labels, zero_division=0))
    print(f"Saved model: {MODEL_DIR / 'risk_model.joblib'}")
    print(f"Saved metrics: {REPORT_DIR / 'metrics.json'}")

if __name__ == "__main__":
    main()
