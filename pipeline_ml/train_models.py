import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    accuracy_score,
    f1_score,
    roc_auc_score,
)
from etl_warehouse import upload_to_s3_warehouse

def train_all_models():
    print("=== INICIANDO ENTRENAMIENTO ML (NO SUPERVISADO + SUPERVISADO) ===")
    os.makedirs("pipeline_ml/artifacts", exist_ok=True)

    # Cargar datasets limpios desde el Data Warehouse procesado
    df_tx = pd.read_parquet("data/processed/transactions_clean.parquet")
    train_df = pd.read_parquet("data/processed/students_train.parquet")
    test_df = pd.read_parquet("data/processed/students_test.parquet")

    # =========================================================================
    # FASE 1: APRENDIZAJE NO SUPERVISADO (K-Means + PCA para Gastos Hormiga)
    # =========================================================================
    print("\n--- [1/2] Entrenando Modelo No Supervisado (K-Means + PCA) ---")
    tx_features = ["monto_mxn", "hora_decimal", "dia_semana", "frecuencia_mensual_comercio"]
    X_tx = df_tx[tx_features].copy()

    tx_scaler = StandardScaler()
    X_tx_scaled = tx_scaler.fit_transform(X_tx)

    # Evaluación del Método del Codo (k = 2 a 5)
    elbow_inertias = {}
    for k in range(2, 6):
        km_test = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
        km_test.fit(X_tx_scaled)
        elbow_inertias[f"k_{k}"] = round(float(km_test.inertia_), 2)

    # Modelo óptimo seleccionado: k=3 (Goteo Diario, Fuga Nocturna, Consumo Esencial)
    kmeans = KMeans(n_clusters=3, init="k-means++", n_init=15, random_state=42)
    clusters = kmeans.fit_predict(X_tx_scaled)
    df_tx["cluster_id"] = clusters

    # Reducción de dimensionalidad con PCA (2 componentes para visualización 2D/3D)
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_tx_scaled)
    varianza_explicada = float(np.sum(pca.explained_variance_ratio_))

    # Métricas No Supervisadas (muestra estratificada de 5,000 tx para rapidez en Silueta)
    sample_idx = np.random.RandomState(42).choice(len(X_tx_scaled), size=min(5000, len(X_tx_scaled)), replace=False)
    sil_score = float(silhouette_score(X_tx_scaled[sample_idx], clusters[sample_idx]))
    db_score = float(davies_bouldin_score(X_tx_scaled, clusters))

    # Mapear semánticamente cada clúster según su ticket promedio y hora
    cluster_summary = df_tx.groupby("cluster_id").agg(
        monto_medio=("monto_mxn", "mean"),
        hora_media=("hora_decimal", "mean"),
        freq_media=("frecuencia_mensual_comercio", "mean"),
        conteo=("tx_id", "count")
    )
    # Ordenar por monto medio: menor monto = Goteo Diario, mayor monto = Esencial, intermedio = Nocturno/Digital
    ordered_ids = cluster_summary.sort_values("monto_medio").index.tolist()
    cluster_labels_map = {
        int(ordered_ids[0]): "Goteo Diario (Gasto Hormiga Escolar)",
        int(ordered_ids[1]): "Fuga Digital y Ocio Nocturno",
        int(ordered_ids[2]): "Gastos Esenciales y Fijos",
    }

    print(f"Silhouette Score: {sil_score:.4f} | Davies-Bouldin: {db_score:.4f} | Varianza PCA: {varianza_explicada:.2%}")
    print("Mapeo de Clústeres:", cluster_labels_map)

    # Guardar artefactos no supervisados
    joblib.dump(tx_scaler, "pipeline_ml/artifacts/tx_scaler.joblib")
    joblib.dump(kmeans, "pipeline_ml/artifacts/kmeans_model.joblib")
    joblib.dump(pca, "pipeline_ml/artifacts/pca_model.joblib")

    # =========================================================================
    # FASE 2: APRENDIZAJE SUPERVISADO (Random Forest + GridSearchCV)
    # =========================================================================
    print("\n--- [2/2] Entrenando Modelo Supervisado (Random Forest + Tuning) ---")
    num_cols = [
        "edad", "es_foraneo", "ingreso_mensual_mxn", "meta_ahorro_mxn",
        "gasto_acumulado_dia15_mxn", "ratio_gasto_hormiga",
        "velocidad_desgaste_quincenal", "indice_presion_foraneo",
        "ticket_promedio_mxn", "pct_tx_nocturnas"
    ]
    cat_cols = ["genero", "zona_territorial", "fuente_ingreso"]
    target_col = "estado_riesgo_fin_mes"

    X_train = train_df[num_cols + cat_cols]
    y_train = train_df[target_col]
    X_test = test_df[num_cols + cat_cols]
    y_test = test_df[target_col]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )

    # 1. Modelo Base (antes de optimización)
    base_pipeline = Pipeline([
        ("prep", preprocessor),
        ("clf", RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42))
    ])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    base_cv_f1 = float(np.mean(cross_val_score(base_pipeline, X_train, y_train, cv=cv, scoring="f1_macro")))

    # 2. Optimización de Hiperparámetros con GridSearchCV
    param_grid = {
        "clf__n_estimators": [100, 200],
        "clf__max_depth": [8, 12, None],
        "clf__min_samples_split": [2, 5],
        "clf__class_weight": ["balanced", None],
    }

    grid_search = GridSearchCV(
        Pipeline([("prep", preprocessor), ("clf", RandomForestClassifier(random_state=42))]),
        param_grid=param_grid,
        cv=cv,
        scoring="f1_macro",
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_

    # Evaluación en conjunto de prueba (Test 20%)
    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)

    test_acc = float(accuracy_score(y_test, y_pred))
    test_f1 = float(f1_score(y_test, y_pred, average="macro"))
    test_roc_auc = float(roc_auc_score(y_test, y_proba, multi_class="ovr", average="macro"))

    print(f"F1-Macro Base (CV): {base_cv_f1:.4f} -> F1-Macro Optimizado (CV): {grid_search.best_score_:.4f}")
    print(f"Test Accuracy: {test_acc:.4f} | Test F1-Macro: {test_f1:.4f} | Test ROC-AUC: {test_roc_auc:.4f}")
    print("Mejores Hiperparámetros:", grid_search.best_params_)

    # Guardar modelo supervisado y metadatos
    rf_path = "pipeline_ml/artifacts/rf_risk_model.joblib"
    joblib.dump(best_model, rf_path)

    training_summary = {
        "unsupervised_kmeans": {
            "n_clusters": 3,
            "silhouette_score": round(sil_score, 4),
            "davies_bouldin_index": round(db_score, 4),
            "pca_explained_variance": round(varianza_explicada, 4),
            "elbow_inertias": elbow_inertias,
            "cluster_labels": cluster_labels_map,
        },
        "supervised_random_forest": {
            "cv_folds": 5,
            "f1_macro_before_tuning": round(base_cv_f1, 4),
            "f1_macro_after_tuning": round(float(grid_search.best_score_), 4),
            "best_params": {k.replace("clf__", ""): v for k, v in grid_search.best_params_.items()},
            "test_accuracy": round(test_acc, 4),
            "test_f1_macro": round(test_f1, 4),
            "test_roc_auc_ovr": round(test_roc_auc, 4),
            "feature_columns_num": num_cols,
            "feature_columns_cat": cat_cols,
        }
    }

    with open("pipeline_ml/artifacts/training_metrics.json", "w", encoding="utf-8") as f:
        json.dump(training_summary, f, indent=4, ensure_ascii=False)

    # Subir artefactos al Data Warehouse (S3)
    for artifact_file in ["tx_scaler.joblib", "kmeans_model.joblib", "pca_model.joblib", "rf_risk_model.joblib", "training_metrics.json"]:
        upload_to_s3_warehouse(f"pipeline_ml/artifacts/{artifact_file}", f"artifacts/{artifact_file}")

    print("\n=== MODELOS ENTRENADOS Y GUARDADOS EN pipeline_ml/artifacts/ ===")

if __name__ == "__main__":
    train_all_models()