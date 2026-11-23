import json
import joblib
import numpy as np
import pandas as pd

class AeroVaultMLService:
    def __init__(self):
        self.tx_scaler = joblib.load("pipeline_ml/artifacts/tx_scaler.joblib")
        self.kmeans = joblib.load("pipeline_ml/artifacts/kmeans_model.joblib")
        self.rf_model = joblib.load("pipeline_ml/artifacts/rf_risk_model.joblib")

        with open("pipeline_ml/artifacts/metrics_report.json", "r", encoding="utf-8") as f:
            self.metrics_report = json.load(f)

        self.cluster_labels = {
            int(k): v for k, v in self.metrics_report["unsupervised_kmeans"]["cluster_labels"].items()
        }
        self.risk_labels = {
            0: "Salud Financiera / Meta Cumplida",
            1: "Equilibrio Ajustado (Riesgo Moderado)",
            2: "Déficit Crítico / Vulnerabilidad Financiera",
        }

    def analyze_student_finances(self, payload: dict) -> dict:
        tx_list = payload["transacciones"]
        df_tx = pd.DataFrame([
            {
                "monto_mxn": t["monto_mxn"],
                "hora_decimal": t["hora_decimal"],
                "dia_semana": t["dia_semana"],
                "frecuencia_mensual_comercio": t["frecuencia_mensual"],
            }
            for t in tx_list
        ])

        # 1. Inferencia No Supervisada (K-Means)
        X_tx_scaled = self.tx_scaler.transform(df_tx)
        cluster_ids = self.kmeans.predict(X_tx_scaled)

        clustered_results = []
        gasto_hormiga_total = 0.0
        total_gasto_tx = 0.0

        for idx, t in enumerate(tx_list):
            cid = int(cluster_ids[idx])
            clabel = self.cluster_labels[cid]
            clustered_results.append({
                "concepto": t["concepto"],
                "monto_mxn": t["monto_mxn"],
                "cluster_id": cid,
                "cluster_label": clabel,
            })
            total_gasto_tx += t["monto_mxn"]
            if "Esenciales" not in clabel:
                gasto_hormiga_total += t["monto_mxn"]

        ingreso = payload["ingreso_mensual_mxn"]
        gasto_dia15 = payload["gasto_acumulado_dia15_mxn"]
        ratio_hormiga = round(gasto_hormiga_total / ingreso, 4)
        vel_quincenal = round(gasto_dia15 / ingreso, 4)
        presion_foraneo = round((gasto_dia15 * 1.15 / ingreso) if payload["es_foraneo"] == 1 else vel_quincenal, 4)

        # 2. Inferencia Supervisada (Random Forest)
        features_df = pd.DataFrame([{
            "edad": payload["edad"],
            "es_foraneo": payload["es_foraneo"],
            "ingreso_mensual_mxn": ingreso,
            "meta_ahorro_mxn": payload["meta_ahorro_mxn"],
            "gasto_acumulado_dia15_mxn": gasto_dia15,
            "ratio_gasto_hormiga": ratio_hormiga,
            "velocidad_desgaste_quincenal": vel_quincenal,
            "indice_presion_foraneo": presion_foraneo,
            "ticket_promedio_mxn": float(df_tx["monto_mxn"].mean()),
            "pct_tx_nocturnas": float(np.mean((df_tx["hora_decimal"] >= 21.0) | (df_tx["hora_decimal"] <= 3.0))),
            "genero": payload["genero"],
            "zona_territorial": payload["zona_territorial"],
            "fuente_ingreso": payload["fuente_ingreso"],
        }])

        pred_class = int(self.rf_model.predict(features_df)[0])
        proba = self.rf_model.predict_proba(features_df)[0]

        aquarium_map = {
            0: "Cristalino (Ecosistema Saludable)",
            1: "Semi-Turbio (Precaución de Liquidez)",
            2: "Turbio / Alerta Crítica (Exceso de Fugas)",
        }

        return {
            "aquarium_status": aquarium_map[pred_class],
            "total_gasto_analizado_mxn": round(total_gasto_tx, 2),
            "gasto_hormiga_detectado_mxn": round(gasto_hormiga_total, 2),
            "ratio_gasto_hormiga": ratio_hormiga,
            "clustered_transactions": clustered_results,
            "predicted_risk_class": pred_class,
            "predicted_risk_label": self.risk_labels[pred_class],
            "probabilities": {
                "salud_financiera": round(float(proba[0]), 4),
                "equilibrio_ajustado": round(float(proba[1]), 4),
                "deficit_critico": round(float(proba[2]), 4),
            },
        }

ml_service = AeroVaultMLService()