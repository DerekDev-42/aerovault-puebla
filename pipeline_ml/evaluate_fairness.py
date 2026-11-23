import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

def run_seaes_fairness_audit():
    print("=== AUDITORÍA DE EQUIDAD ALGORÍTMICA (CRITERIO RECTOR SEAES) ===")
    test_df = pd.read_parquet("data/processed/students_test.parquet")
    model = joblib.load("pipeline_ml/artifacts/rf_risk_model.joblib")

    with open("pipeline_ml/artifacts/training_metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)

    num_cols = metrics["supervised_random_forest"]["feature_columns_num"]
    cat_cols = metrics["supervised_random_forest"]["feature_columns_cat"]

    X_test = test_df[num_cols + cat_cols]
    y_test = test_df["estado_riesgo_fin_mes"]
    y_pred = model.predict(X_test)

    test_df["prediccion_riesgo"] = y_pred
    test_df["acierto"] = (test_df["estado_riesgo_fin_mes"] == test_df["prediccion_riesgo"]).astype(int)

    # 1. Desagregación por Género (SEAES: Equidad Social y de Género)
    gender_audit = {}
    for gen, group in test_df.groupby("genero"):
        tasa_riesgo_pred = float(np.mean(group["prediccion_riesgo"] == 2))
        exactitud_grupo = float(np.mean(group["acierto"]))
        gender_audit[gen] = {
            "muestra_test": int(len(group)),
            "exactitud_modelo": round(exactitud_grupo, 4),
            "tasa_alerta_deficit": round(tasa_riesgo_pred, 4),
            "gasto_hormiga_promedio_mxn": round(float(group["gasto_hormiga_real_mxn"].mean()), 2),
        }

    # Diferencia de Paridad Demográfica entre Femenino y Masculino
    dp_diff = abs(
        gender_audit.get("Femenino", {}).get("tasa_alerta_deficit", 0)
        - gender_audit.get("Masculino", {}).get("tasa_alerta_deficit", 0)
    )

    # 2. Desagregación Territorial Puebla (Urbano vs Semiurbano vs Rural/Sierra)
    territory_audit = {}
    for zona, group in test_df.groupby("zona_territorial"):
        territory_audit[zona] = {
            "muestra_test": int(len(group)),
            "exactitud_modelo": round(float(np.mean(group["acierto"])), 4),
            "ingreso_promedio_mxn": round(float(group["ingreso_mensual_mxn"].mean()), 2),
            "ratio_gasto_hormiga_medio": round(float(group["ratio_gasto_hormiga"].mean()), 4),
        }

    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    full_audit = {
        **metrics,
        "evaluation_details": {
            "confusion_matrix": cm,
            "classification_report": report,
        },
        "seaes_equidad_audit": {
            "criterio_rector": "Equidad Social y de Género (SEAES)",
            "demographic_parity_difference_gender": round(dp_diff, 4),
            "cumple_umbral_equidad_menor_10pct": bool(dp_diff < 0.10),
            "desglose_por_genero": gender_audit,
            "desglose_territorial_puebla": territory_audit,
        }
    }

    with open("pipeline_ml/artifacts/metrics_report.json", "w", encoding="utf-8") as f:
        json.dump(full_audit, f, indent=4, ensure_ascii=False)

    print(f"Diferencia de Paridad Demográfica (Género): {dp_diff:.4f} (< 0.10 = Sin sesgo discriminatorio)")
    print("Reporte completo guardado en pipeline_ml/artifacts/metrics_report.json")

if __name__ == "__main__":
    run_seaes_fairness_audit()