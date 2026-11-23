import os
import pandas as pd
import numpy as np
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

def remove_outliers_iqr(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Detección y recorte (Winsorization/IQR) de valores atípicos extremos."""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = max(0.0, Q1 - 1.5 * IQR)
    upper_bound = Q3 + 3.0 * IQR  # Umbral conservador para no perder gastos fijos legítimos
    clean_df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)].copy()
    print(f"[ETL-IQR] Registros filtrados en '{column}': {len(df) - len(clean_df)} outliers eliminados.")
    return clean_df

def upload_to_s3_warehouse(local_path: str, s3_key: str):
    """Sincroniza archivos procesados con el Data Warehouse en AWS S3."""
    bucket_name = os.getenv("S3_BUCKET_NAME")
    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    if not bucket_name or not aws_key or aws_key == "tu_access_key":
        print(f"[DW Local Mode] AWS S3 no configurado aún. Archivo listo para sync en: {local_path}")
        return False

    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_key,
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        s3.upload_file(local_path, bucket_name, s3_key)
        print(f"[AWS S3 DW] Subido exitosamente -> s3://{bucket_name}/{s3_key}")
        return True
    except (NoCredentialsError, ClientError) as e:
        print(f"[AWS S3 Warning] No se pudo subir a S3 ({e}). Conservando copia local.")
        return False

def run_etl_pipeline():
    print("=== INICIANDO PIPELINE ETL CRISP-DM (AEROVAULT PUEBLA) ===")
    os.makedirs("data/processed", exist_ok=True)

    # 1. EXTRACT
    df_students = pd.read_csv("data/raw/puebla_students_raw.csv")
    df_tx = pd.read_csv("data/raw/puebla_transactions_raw.csv")

    # 2. TRANSFORM - Limpieza de nulos y outliers
    nulos_antes = df_students["gasto_acumulado_dia15_mxn"].isna().sum()
    df_students["gasto_acumulado_dia15_mxn"] = df_students.groupby("fuente_ingreso")[
        "gasto_acumulado_dia15_mxn"
    ].transform(lambda x: x.fillna(x.median()))
    print(f"[ETL-Nulos] {nulos_antes} valores nulos imputados por mediana estratificada.")

    df_tx_clean = remove_outliers_iqr(df_tx, "monto_mxn")

    # 3. FEATURE ENGINEERING (Ingeniería de Atributos)
    # Agregación de comportamiento transaccional por estudiante
    tx_agg = df_tx_clean.groupby("student_id").agg(
        tx_count=("tx_id", "count"),
        ticket_promedio_mxn=("monto_mxn", "mean"),
        pct_tx_nocturnas=("hora_decimal", lambda x: np.mean((x >= 21.0) | (x <= 3.0))),
        pct_tx_fin_semana=("dia_semana", lambda x: np.mean(x >= 4)),
        freq_comercio_promedio=("frecuencia_mensual_comercio", "mean"),
    ).reset_index()

    df_master = pd.merge(df_students, tx_agg, on="student_id", how="inner")

    # Nuevas variables derivadas de alto valor predictivo
    df_master["ratio_gasto_hormiga"] = (
        df_master["gasto_hormiga_real_mxn"] / df_master["ingreso_mensual_mxn"]
    ).round(4)
    df_master["velocidad_desgaste_quincenal"] = (
        df_master["gasto_acumulado_dia15_mxn"] / df_master["ingreso_mensual_mxn"]
    ).round(4)
    df_master["indice_presion_foraneo"] = np.where(
        df_master["es_foraneo"] == 1,
        (df_master["gasto_acumulado_dia15_mxn"] * 1.15) / df_master["ingreso_mensual_mxn"],
        df_master["velocidad_desgaste_quincenal"],
    ).round(4)

    # 4. PARTICIONAMIENTO ESTRATIFICADO (80% Train / 20% Test)
    train_df, test_df = train_test_split(
        df_master,
        test_size=0.20,
        random_state=42,
        stratify=df_master["estado_riesgo_fin_mes"],
    )

    # Guardar en formato columnar Parquet (estándar Data Warehouse)
    tx_clean_path = "data/processed/transactions_clean.parquet"
    train_path = "data/processed/students_train.parquet"
    test_path = "data/processed/students_test.parquet"

    df_tx_clean.to_parquet(tx_clean_path, index=False)
    train_df.to_parquet(train_path, index=False)
    test_df.to_parquet(test_path, index=False)

    print(f"[ETL-Split] Train: {len(train_df)} registros | Test: {len(test_df)} registros.")

    # 5. LOAD (Sincronización con Data Warehouse AWS S3)
    upload_to_s3_warehouse("data/raw/puebla_students_raw.csv", "raw/puebla_students_raw.csv")
    upload_to_s3_warehouse(tx_clean_path, "processed/transactions_clean.parquet")
    upload_to_s3_warehouse(train_path, "processed/students_train.parquet")
    upload_to_s3_warehouse(test_path, "processed/students_test.parquet")
    print("=== PIPELINE ETL COMPLETADO CON ÉXITO ===")

if __name__ == "__main__":
    run_etl_pipeline()