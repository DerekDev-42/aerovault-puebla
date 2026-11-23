from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class UserPuebla(Base):
    __tablename__ = "users_puebla"

    id = Column(Integer, primary_key=True, index=True)
    student_alias = Column(String(100), nullable=False)
    edad = Column(Integer, nullable=False)
    genero = Column(String(30), nullable=False)
    municipio_puebla = Column(String(100), nullable=False)
    zona_territorial = Column(String(50), nullable=False)
    es_foraneo = Column(Integer, default=0)
    fuente_ingreso = Column(String(80), nullable=False)
    ingreso_mensual_mxn = Column(Float, nullable=False)
    meta_ahorro_mxn = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("TransactionRecord", back_populates="user")
    predictions = relationship("PredictionLog", back_populates="user")

class TransactionRecord(Base):
    __tablename__ = "transactions_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_puebla.id"), nullable=False)
    concepto = Column(String(120), nullable=False)
    monto_mxn = Column(Float, nullable=False)
    hora_decimal = Column(Float, nullable=False)
    dia_semana = Column(Integer, nullable=False)
    frecuencia_mensual = Column(Integer, default=1)
    assigned_cluster_id = Column(Integer, nullable=False)
    assigned_cluster_label = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserPuebla", back_populates="transactions")

class PredictionLog(Base):
    __tablename__ = "ml_predictions_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_puebla.id"), nullable=False)
    gasto_acumulado_dia15_mxn = Column(Float, nullable=False)
    ratio_gasto_hormiga = Column(Float, nullable=False)
    predicted_risk_class = Column(Integer, nullable=False)
    predicted_risk_label = Column(String(80), nullable=False)
    success_probability = Column(Float, nullable=False)
    rag_advice = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserPuebla", back_populates="predictions")