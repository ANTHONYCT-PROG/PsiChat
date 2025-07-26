# backend/ml_models/style_classification/train.py

import os
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Rutas
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset_estilo.csv"
MODEL_PATH = BASE_DIR / "style_model.joblib"

def main():
    # 1. Verificar dataset
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"⚠️ Dataset no encontrado en: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    if "texto" not in df.columns or "estilo" not in df.columns:
        raise ValueError("❌ El CSV debe tener columnas 'texto' y 'estilo'.")

    df = df.dropna(subset=["texto", "estilo"])

    X = df["texto"]
    y = df["estilo"]

    # 2. Separar train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # 3. Pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=300))
    ])

    # 4. Entrenamiento
    pipeline.fit(X_train, y_train)

    # 5. Evaluación
    y_pred = pipeline.predict(X_test)
    print("🔎 Reporte de clasificación:")
    print(classification_report(y_test, y_pred))
    print("🧱 Matriz de confusión:")
    print(confusion_matrix(y_test, y_pred))

    # 6. Guardar modelo
    joblib.dump(pipeline, MODEL_PATH)
    print(f"✅ Modelo guardado en: {MODEL_PATH}")

if __name__ == "__main__":
    main()
