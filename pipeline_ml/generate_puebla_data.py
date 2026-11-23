import os
import hashlib
import numpy as np
import pandas as pd

def hash_id(raw_id: str) -> str:
    """Anonimización SHA-256 en cumplimiento con LFPDPPP (Gobernanza Ética)."""
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]

def generate_puebla_datasets(n_students: int = 800, seed: int = 42):
    np.random.seed(seed)
    os.makedirs("data/raw", exist_ok=True)

    # Municipios y corredores universitarios/industriales reales de Puebla
    municipios_puebla = [
        ("Puebla Capital", "Urbano", 0.35),
        ("San Andrés Cholula", "Urbano", 0.14),
        ("San Pedro Cholula", "Urbano", 0.10),
        ("San José Chiapa (Ciudad Modelo)", "Semiurbano", 0.12),
        ("Tehuacán", "Urbano", 0.09),
        ("Atlixco", "Semiurbano", 0.07),
        ("San Martín Texmelucan", "Semiurbano", 0.06),
        ("Teziutlán", "Rural/Sierra", 0.04),
        ("Zacatlán", "Rural/Sierra", 0.03),
    ]
    mun_names = [m[0] for m in municipios_puebla]
    mun_types = {m[0]: m[1] for m in municipios_puebla}
    mun_probs = [m[2] for m in municipios_puebla]

    generos = ["Femenino", "Masculino", "No Binario"]
    genero_probs = [0.49, 0.48, 0.03]

    tipos_ingreso = ["Beca Pública", "Apoyo Familiar", "Empleo Medio Tiempo", "Mixto (Beca + Trabajo)"]
    ingreso_probs = [0.28, 0.30, 0.22, 0.20]

    students = []
    transactions = []

    print("Generando cohorte universitaria del Estado de Puebla (calibrada ENIGH/ENIF)...")

    for i in range(n_students):
        student_uuid = hash_id(f"UTBIS_PUE_2026_{i:04d}")
        edad = np.random.randint(18, 28)
        genero = np.random.choice(generos, p=genero_probs)
        municipio = np.random.choice(mun_names, p=mun_probs)
        zona = mun_types[municipio]
        es_foraneo = 1 if (zona != "Urbano" or np.random.rand() < 0.35) else 0
        fuente_ingreso = np.random.choice(tipos_ingreso, p=ingreso_probs)

        # Ingreso mensual realista en MXN para jóvenes en Puebla
        base_income = {
            "Beca Pública": np.random.normal(3200, 450),
            "Apoyo Familiar": np.random.normal(4500, 900),
            "Empleo Medio Tiempo": np.random.normal(5800, 1100),
            "Mixto (Beca + Trabajo)": np.random.normal(6900, 1200),
        }[fuente_ingreso]
        ingreso_mensual = round(max(1800.0, base_income), 2)

        # Meta de ahorro mensual (ej. equipo de cómputo, viaje, titulación)
        meta_ahorro = round(ingreso_mensual * np.random.uniform(0.12, 0.25), 2)

        # Perfil oculto de comportamiento para simular transacciones realistas
        propension_hormiga = np.random.beta(2.2, 2.5)
        n_tx = np.random.randint(25, 65)

        total_gastado = 0.0
        gasto_hormiga_acum = 0.0

        for t in range(n_tx):
            r = np.random.rand()
            if r < propension_hormiga * 0.65:
                # Patrón 1: Goteo diario / Gasto hormiga escolar (cafés, snacks, pasaje RUTA)
                monto = round(np.random.lognormal(mean=3.6, sigma=0.45), 2)  # ~$20 - $85 MXN
                hora = round(np.random.uniform(7.0, 19.5), 2)
                dia_semana = np.random.randint(0, 5)  # Lunes a Viernes
                frecuencia_comercio = np.random.randint(8, 25)
                categoria_raw = np.random.choice(["Cafetería/Snacks", "Transporte Urbano", "Papelería/Copias"])
                gasto_hormiga_acum += monto
            elif r < propension_hormiga:
                # Patrón 2: Fuga nocturna / digital (apps de comida, juegos, compras impulsivas)
                monto = round(np.random.lognormal(mean=5.1, sigma=0.4), 2)   # ~$110 - $320 MXN
                hora = round(np.random.choice([21.5, 22.3, 23.1, 0.5, 1.2]), 2)
                dia_semana = np.random.randint(4, 7)  # Viernes a Domingo
                frecuencia_comercio = np.random.randint(3, 9)
                categoria_raw = np.random.choice(["Delivery Nocturno", "Suscripciones/Apps", "Ocio Fin de Semana"])
                gasto_hormiga_acum += monto
            else:
                # Patrón 3: Gastos esenciales y fijos (renta foráneo, despensa, internet, colegiatura)
                monto = round(np.random.lognormal(mean=6.3, sigma=0.55), 2)  # ~$350 - $1500 MXN
                hora = round(np.random.uniform(9.0, 18.0), 2)
                dia_semana = np.random.randint(0, 7)
                frecuencia_comercio = np.random.randint(1, 3)
                categoria_raw = np.random.choice(["Vivienda/Servicios", "Despensa Básica", "Educación/Material"])

            total_gastado += monto
            transactions.append({
                "tx_id": hash_id(f"{student_uuid}_TX_{t}"),
                "student_id": student_uuid,
                "monto_mxn": monto,
                "hora_decimal": hora,
                "dia_semana": dia_semana,
                "frecuencia_mensual_comercio": frecuencia_comercio,
                "categoria_referencia": categoria_raw
            })

        # Cálculo de estado financiero real a fin de mes (Variable objetivo supervisada)
        balance_final = ingreso_mensual - total_gastado
        if balance_final >= meta_ahorro:
            estado_riesgo = 0  # Salud Financiera / Meta Cumplida
        elif balance_final >= 0:
            estado_riesgo = 1  # Equilibrio Ajustado (No cumple meta)
        else:
            estado_riesgo = 2  # Déficit Crítico / Riesgo de Vulnerabilidad

        students.append({
            "student_id": student_uuid,
            "edad": edad,
            "genero": genero,
            "municipio_puebla": municipio,
            "zona_territorial": zona,
            "es_foraneo": es_foraneo,
            "fuente_ingreso": fuente_ingreso,
            "ingreso_mensual_mxn": ingreso_mensual,
            "meta_ahorro_mxn": meta_ahorro,
            "gasto_acumulado_dia15_mxn": round(total_gastado * np.random.uniform(0.45, 0.62), 2),
            "total_gastado_mes_mxn": round(total_gastado, 2),
            "gasto_hormiga_real_mxn": round(gasto_hormiga_acum, 2),
            "estado_riesgo_fin_mes": estado_riesgo
        })

    df_students = pd.DataFrame(students)
    df_tx = pd.DataFrame(transactions)

    # Inyectar ruido realista (2% nulos y algunos outliers extremos) para validar el ETL
    null_idx = np.random.choice(df_students.index, size=int(len(df_students) * 0.02), replace=False)
    df_students.loc[null_idx, "gasto_acumulado_dia15_mxn"] = np.nan

    outlier_idx = np.random.choice(df_tx.index, size=15, replace=False)
    df_tx.loc[outlier_idx, "monto_mxn"] = df_tx.loc[outlier_idx, "monto_mxn"] * 18.0  # Errores de captura

    df_students.to_csv("data/raw/puebla_students_raw.csv", index=False, encoding="utf-8")
    df_tx.to_csv("data/raw/puebla_transactions_raw.csv", index=False, encoding="utf-8")
    print(f"Archivos crudos generados en data/raw/: {len(df_students)} perfiles y {len(df_tx)} transacciones.")

if __name__ == "__main__":
    generate_puebla_datasets()