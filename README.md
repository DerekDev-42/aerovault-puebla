# AeroVault Puebla — Ecosistema Inteligente de Salud Financiera Juvenil

**Institución:** Universidad Tecnológica Bilingüe Internacional y Sustentable de Puebla (UTBIS Puebla)  
**Asignatura:** Extracción de Conocimiento en Bases de Datos  
**Programa:** Ingeniería en Desarrollo y Gestión de Software  

## 1. Pertinencia Territorial y Criterio Rector SEAES
- **Ámbito Geográfico:** Estado de Puebla (Puebla Capital, San José Chiapa / Ciudad Modelo, San Andrés Cholula, San Pedro Cholula, Tehuacán, Atlixco, San Martín Texmelucan, Teziutlán y Zacatlán).
- **Criterio Rector SEAES (Equidad Social y de Género):** Auditoría algorítmica de paridad demográfica (`< 0.10` de brecha entre géneros) y análisis territorial desagregado entre estudiantes locales y foráneos.
- **Gobernanza Ética (LFPDPPP):** Seudonimización mediante hash criptográfico `SHA-256` antes de persistir registros en el Data Warehouse.

## 2. Arquitectura y Flujo de Datos (CRISP-DM)
1. **Ingesta & ETL (`pipeline_ml/etl_warehouse.py`):** Imputación estadística, detección de valores atípicos mediante rango intercuartílico ($IQR$), particionamiento estratificado `80/20` en formato columnar `.parquet` y respaldo en **AWS S3 (`boto3`)**.
2. **Modelado Dual (`pipeline_ml/train_models.py`):**
   - *No Supervisado:* **K-Means ($k=3$) + PCA** para segmentar micro-transacciones (necesidades esenciales, gasto hormiga recurrente e impulsos nocturnos/delivery).
   - *Supervisado:* **Random Forest Classifier** ajustado mediante `GridSearchCV` y `StratifiedKFold(5)` para predecir riesgo de insolvencia al cierre de mes.
3. **Backend API (`backend/main.py`):** **FastAPI** con validación estricta **Pydantic**, persistencia relacional en **PostgreSQL** (`SQLAlchemy`), conversión en tiempo real `USD/MXN` vía **Frankfurter API** y motor de recomendaciones **LLM + RAG** fundamentado en lineamientos de **CONDUSEF**.
4. **Frontend (`frontend/app.py`):** Interfaz interactiva en **Streamlit** y **Plotly** con diseño arquitectónico translúcido.

## 3. Despliegue en Producción (Docker + AWS EC2)
```bash
cp .env.example .env
docker compose up -d --build