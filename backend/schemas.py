from typing import List, Optional
from pydantic import BaseModel, Field

class TransactionInput(BaseModel):
    concepto: str = Field(..., example="Café y sándwich cafetería")
    monto_mxn: float = Field(..., gt=0, example=55.0)
    hora_decimal: float = Field(..., ge=0, le=24, example=10.5)
    dia_semana: int = Field(..., ge=0, le=6, example=2)
    frecuencia_mensual: int = Field(default=12, ge=1, example=15)

class FinancialAnalysisRequest(BaseModel):
    student_alias: str = Field(..., example="Derek_UTBIS")
    edad: int = Field(..., ge=17, le=35, example=21)
    genero: str = Field(..., example="Masculino")
    municipio_puebla: str = Field(..., example="San José Chiapa (Ciudad Modelo)")
    zona_territorial: str = Field(..., example="Semiurbano")
    es_foraneo: int = Field(..., ge=0, le=1, example=1)
    fuente_ingreso: str = Field(..., example="Mixto (Beca + Trabajo)")
    ingreso_mensual_mxn: float = Field(..., gt=0, example=5500.0)
    meta_ahorro_mxn: float = Field(..., ge=0, example=1000.0)
    gasto_acumulado_dia15_mxn: float = Field(..., ge=0, example=2600.0)
    transacciones: List[TransactionInput]

class ClusteredTxOutput(BaseModel):
    concepto: str
    monto_mxn: float
    cluster_id: int
    cluster_label: str

class FinancialAnalysisResponse(BaseModel):
    student_alias: str
    aquarium_status: str
    exchange_rate_usd_mxn: float
    meta_ahorro_usd: float
    total_gasto_analizado_mxn: float
    gasto_hormiga_detectado_mxn: float
    ratio_gasto_hormiga: float
    clustered_transactions: List[ClusteredTxOutput]
    predicted_risk_class: int
    predicted_risk_label: str
    probabilities: dict
    rag_financial_advice: str