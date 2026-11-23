import os
from backend.config import settings

def retrieve_knowledge_context() -> str:
    """Recupera el documento base de conocimiento financiero (RAG Retrieval)."""
    kb_path = "data/knowledge_base/guia_condusef_jovenes.md"
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Regla 50-30-20: Mantener gastos hormiga por debajo del 15% del ingreso mensual."

def generate_rag_advice(profile_summary: dict) -> str:
    """Genera recomendación personalizada combinando métricas ML + contexto RAG."""
    context_doc = retrieve_knowledge_context()

    prompt = f"""
    Eres el asesor financiero inteligente de AeroVault Puebla para jóvenes universitarios.
    Usa EXCLUSIVAMENTE el siguiente marco de referencia de educación financiera:
    {context_doc}

    Analiza el diagnóstico generado por los modelos de Machine Learning del estudiante:
    - Alias: {profile_summary['student_alias']} | Municipio: {profile_summary['municipio_puebla']} (Foráneo: {profile_summary['es_foraneo']})
    - Ingreso Mensual: ${profile_summary['ingreso_mensual_mxn']} MXN | Meta Ahorro: ${profile_summary['meta_ahorro_mxn']} MXN
    - Gasto Hormiga Detectado (K-Means): ${profile_summary['gasto_hormiga_detectado_mxn']} MXN ({profile_summary['ratio_gasto_hormiga']*100:.1f}% del ingreso)
    - Predicción de Riesgo Fin de Mes (Random Forest): {profile_summary['predicted_risk_label']}

    Redacta un diagnóstico empático, claro y accionable en máximo 3 párrafos breves (sin saludos robóticos) indicando qué clúster de gasto ajustar según la guía CONDUSEF.
    """

    if settings.LLM_API_KEY and settings.LLM_API_KEY != "tu_api_key_gemini_o_groq":
        try:
            from google import genai
            client = genai.Client(api_key=settings.LLM_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            print(f"[RAG Warning] Fallback local activado: {e}")

    # Motor RAG estructurado de respaldo cuando no hay API Key externa activa
    pct_hormiga = profile_summary["ratio_gasto_hormiga"] * 100
    riesgo = profile_summary["predicted_risk_label"]
    municipio = profile_summary["municipio_puebla"]

    if pct_hormiga > 15.0:
        return (
            f"De acuerdo con el marco CONDUSEF (Regla 50-30-20), tus gastos hormiga representan el {pct_hormiga:.1f}% "
            f"de tu ingreso mensual, superando el umbral saludable del 15%. El modelo K-Means detectó recurrencia en "
            f"consumos diarios y digitales que comprometen tu cierre de mes en {municipio} (Estado proyectado: {riesgo}).\n\n"
            f"Acción recomendada: Sustituye al menos 3 compras semanales de cafetería/snacks escolares y establece un tope "
            f"fijo para entregas nocturnas en fin de semana; esto liberará liquidez inmediata para proteger tu meta de ahorro."
        )
    return (
        f"Tu proporción de gasto hormiga ({pct_hormiga:.1f}%) se mantiene dentro del límite saludable (<15%) establecido "
        f"en la guía CONDUSEF para estudiantes en {municipio}. El clasificador Random Forest proyecta un escenario de '{riesgo}'.\n\n"
        f"Acción recomendada: Mantén tu ritmo de gasto controlado durante la segunda quincena y aparta un margen adicional "
        f"del 5% si tu meta de ahorro está sujeta a variación cambiaria en dólares."
    )