# backend/ml_models/style_classification/train.py

import os
import argparse
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def main(dataset_path: str, output_dir: str):
    # 1. Verificar dataset
    dataset_file = Path(dataset_path)
    if not dataset_file.exists():
        raise FileNotFoundError(f"❌ Dataset no encontrado en {dataset_file.resolve()}")

    # 2. Cargar datos
    df = pd.read_csv(dataset_file)
    if "texto" not in df.columns or "estilo" not in df.columns:
        raise ValueError("El CSV debe tener columnas 'texto' y 'estilo'.")

    X = df["texto"]
    y = df["estilo"]

    # 3. Separar train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # 4. Crear pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=300))
    ])

    # 5. Entrenar modelo
    pipeline.fit(X_train, y_train)

    # 6. Evaluar modelo
    y_pred = pipeline.predict(X_test)
    print("\n🎯 Reporte de clasificación:")
    print(classification_report(y_test, y_pred))
    print("📊 Matriz de confusión:")
    print(confusion_matrix(y_test, y_pred))

    # 7. Guardar modelo
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    model_file = output_path / "style_model.joblib"
    joblib.dump(pipeline, model_file)
    print(f"\n✅ Modelo guardado en: {model_file.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrena un modelo de estilo comunicativo.")
    parser.add_argument("--dataset", type=str, default="dataset_estilo.csv", help="Ruta al CSV de entrenamiento")
    parser.add_argument("--output", type=str, default="ml_models/style_classification", help="Directorio de salida del modelo")
    args = parser.parse_args()
    main(args.dataset, args.output)
