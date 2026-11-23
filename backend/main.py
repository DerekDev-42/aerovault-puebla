from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.config import settings
from backend.database import engine, Base, get_db
from backend import models, schemas
from backend.external_apis import get_mxn_to_usd_rate
from backend.ml_service import ml_service
from backend.rag_advisor import generate_rag_advice

# Crear tablas relacionales automáticamente si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API RESTful de Extracción de Conocimiento para Salud Financiera Juvenil en Puebla (UTBIS).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "online", "service": settings.APP_NAME, "docs": "/docs"}

@app.get("/api/v1/metrics-audit")
def get_ml_and_seaes_metrics():
    """Devuelve las métricas completas de K-Means, Random Forest y Auditoría SEAES."""
    return ml_service.metrics_report

@app.get("/api/v1/exchange-rate")
async def get_realtime_exchange():
    """Consulta tipo de cambio USD -> MXN en tiempo real."""
    rate = await get_mxn_to_usd_rate()
    return {"base": "USD", "target": "MXN", "rate": rate}

@app.post("/api/v1/analyze-finances", response_model=schemas.FinancialAnalysisResponse)
async def analyze_finances(request: schemas.FinancialAnalysisRequest, db: Session = Depends(get_db)):
    """Ejecuta el pipeline completo: API Divisas + K-Means + Random Forest + RAG + Persistencia SQLAlchemy."""
    payload = request.model_dump()

    # 1. Consumo de API Externa (Frankfurter)
    usd_rate = await get_mxn_to_usd_rate()
    meta_usd = round(request.meta_ahorro_mxn / usd_rate, 2)

    # 2. Inferencia Dual ML (K-Means + Random Forest)
    ml_result = ml_service.analyze_student_finances(payload)

    # 3. Tecnología Emergente (LLM + RAG sobre guía financiera CONDUSEF)
    rag_context = {
        "student_alias": request.student_alias,
        "municipio_puebla": request.municipio_puebla,
        "es_foraneo": request.es_foraneo,
        "ingreso_mensual_mxn": request.ingreso_mensual_mxn,
        "meta_ahorro_mxn": request.meta_ahorro_mxn,
        "gasto_hormiga_detectado_mxn": ml_result["gasto_hormiga_detectado_mxn"],
        "ratio_gasto_hormiga": ml_result["ratio_gasto_hormiga"],
        "predicted_risk_label": ml_result["predicted_risk_label"],
    }
    advice_text = generate_rag_advice(rag_context)

    # 4. Persistencia Relacional con SQLAlchemy ORM
    db_user = models.UserPuebla(
        student_alias=request.student_alias,
        edad=request.edad,
        genero=request.genero,
        municipio_puebla=request.municipio_puebla,
        zona_territorial=request.zona_territorial,
        es_foraneo=request.es_foraneo,
        fuente_ingreso=request.fuente_ingreso,
        ingreso_mensual_mxn=request.ingreso_mensual_mxn,
        meta_ahorro_mxn=request.meta_ahorro_mxn,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    for idx, tx in enumerate(request.transacciones):
        c_info = ml_result["clustered_transactions"][idx]
        db.add(models.TransactionRecord(
            user_id=db_user.id,
            concepto=tx.concepto,
            monto_mxn=tx.monto_mxn,
            hora_decimal=tx.hora_decimal,
            dia_semana=tx.dia_semana,
            frecuencia_mensual=tx.frecuencia_mensual,
            assigned_cluster_id=c_info["cluster_id"],
            assigned_cluster_label=c_info["cluster_label"],
        ))

    db.add(models.PredictionLog(
        user_id=db_user.id,
        gasto_acumulado_dia15_mxn=request.gasto_acumulado_dia15_mxn,
        ratio_gasto_hormiga=ml_result["ratio_gasto_hormiga"],
        predicted_risk_class=ml_result["predicted_risk_class"],
        predicted_risk_label=ml_result["predicted_risk_label"],
        success_probability=ml_result["probabilities"]["salud_financiera"],
        rag_advice=advice_text,
    ))
    db.commit()

    return schemas.FinancialAnalysisResponse(
        student_alias=request.student_alias,
        aquarium_status=ml_result["aquarium_status"],
        exchange_rate_usd_mxn=usd_rate,
        meta_ahorro_usd=meta_usd,
        total_gasto_analizado_mxn=ml_result["total_gasto_analizado_mxn"],
        gasto_hormiga_detectado_mxn=ml_result["gasto_hormiga_detectado_mxn"],
        ratio_gasto_hormiga=ml_result["ratio_gasto_hormiga"],
        clustered_transactions=ml_result["clustered_transactions"],
        predicted_risk_class=ml_result["predicted_risk_class"],
        predicted_risk_label=ml_result["predicted_risk_label"],
        probabilities=ml_result["probabilities"],
        rag_financial_advice=advice_text,
    )