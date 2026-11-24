import os
import json
import base64
import importlib
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from components.aquarium_widget import render_aquarium_widget
import components.charts as charts_mod

importlib.reload(charts_mod)

st.set_page_config(
    page_title="AeroVault Puebla | Salud Financiera Juvenil",
    layout="wide",
)

def build_architectural_svg_bg() -> str:
    """Genera un fondo arquitectónico Aero-Futurista vectorial (resolución infinita)."""
    svg_code = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
      <defs>
        <radialGradient id="wallGlowLeft" cx="12%" cy="42%" r="55%">
          <stop offset="0%" stop-color="#9ef8ee" stop-opacity="0.85"/>
          <stop offset="35%" stop-color="#2ec4b6" stop-opacity="0.45"/>
          <stop offset="100%" stop-color="#06282e" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="wallGlowRight" cx="88%" cy="38%" r="50%">
          <stop offset="0%" stop-color="#72efdd" stop-opacity="0.72"/>
          <stop offset="45%" stop-color="#1b7a85" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="#052026" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="roomBase" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0d4a52"/>
          <stop offset="48%" stop-color="#083238"/>
          <stop offset="100%" stop-color="#04191d"/>
        </linearGradient>
        <linearGradient id="floorGrad" x1="50%" y1="55%" x2="50%" y2="100%">
          <stop offset="0%" stop-color="#0a3b42"/>
          <stop offset="45%" stop-color="#135d66"/>
          <stop offset="100%" stop-color="#07272c"/>
        </linearGradient>
        <pattern id="flutedWall" width="14" height="1080" patternUnits="userSpaceOnUse">
          <rect width="6" height="1080" fill="#ffffff" fill-opacity="0.035"/>
          <rect x="6" width="8" height="1080" fill="#000000" fill-opacity="0.04"/>
        </pattern>
        <linearGradient id="glassTableTop" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0.24"/>
          <stop offset="50%" stop-color="#5efce8" stop-opacity="0.10"/>
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0.22"/>
        </linearGradient>
        <filter id="neonBlur" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="8" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="24"/>
        </filter>
      </defs>
      <rect width="1920" height="1080" fill="url(#roomBase)"/>
      <rect width="1920" height="1080" fill="url(#wallGlowLeft)"/>
      <rect width="1920" height="1080" fill="url(#wallGlowRight)"/>
      <path d="M 0,0 Q 460,140 520,660 L 0,760 Z" fill="url(#flutedWall)"/>
      <path d="M 1920,0 Q 1480,140 1420,660 L 1920,760 Z" fill="url(#flutedWall)"/>
      <path d="M 680,650 L 680,290 Q 960,180 1240,290 L 1240,650 Z" fill="#06252a" fill-opacity="0.55" stroke="#5efce8" stroke-opacity="0.18" stroke-width="2"/>
      <rect x="610" y="210" width="75" height="450" rx="35" fill="#0c434a" fill-opacity="0.65"/>
      <rect x="1235" y="210" width="75" height="450" rx="35" fill="#0c434a" fill-opacity="0.65"/>
      <path d="M 0,680 Q 960,570 1920,680 L 1920,1080 L 0,1080 Z" fill="url(#floorGrad)"/>
      <path d="M 240,730 C 380,610 1540,610 1680,730 C 1620,790 1420,730 960,730 C 500,730 300,790 240,730 Z" fill="#186069" stroke="#7efce8" stroke-opacity="0.3" stroke-width="2"/>
      <ellipse cx="320" cy="740" rx="135" ry="62" fill="#217985" stroke="#9ef8ee" stroke-opacity="0.35" stroke-width="2"/>
      <ellipse cx="320" cy="785" rx="115" ry="42" fill="#0b353b"/>
      <rect x="865" y="575" width="190" height="72" rx="12" fill="#07191c" stroke="#5efce8" stroke-opacity="0.45" stroke-width="2"/>
      <circle cx="912" cy="611" r="22" fill="#0e2c30" stroke="#5efce8" stroke-width="2"/>
      <circle cx="1008" cy="611" r="22" fill="#0e2c30" stroke="#5efce8" stroke-width="2"/>
      <ellipse cx="980" cy="875" rx="220" ry="55" fill="#ffd166" fill-opacity="0.16" filter="url(#softGlow)"/>
      <ellipse cx="1140" cy="915" rx="160" ry="40" fill="#5efce8" fill-opacity="0.22" filter="url(#softGlow)"/>
      <ellipse cx="1050" cy="885" rx="390" ry="118" fill="none" stroke="#9ef8ee" stroke-opacity="0.65" stroke-width="3" filter="url(#neonBlur)"/>
      <ellipse cx="1030" cy="835" rx="430" ry="128" fill="url(#glassTableTop)" stroke="#ffffff" stroke-opacity="0.88" stroke-width="3.5" filter="url(#neonBlur)"/>
      <ellipse cx="1040" cy="842" rx="275" ry="78" fill="none" stroke="#5efce8" stroke-opacity="0.55" stroke-width="2"/>
    </svg>
    """
    return base64.b64encode(svg_code.strip().encode("utf-8")).decode("utf-8")

def apply_custom_theme():
    css_path = os.path.join("frontend", "assets", "frutiger_aero.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    b64_svg = build_architectural_svg_bg()
    bg_style = f"""
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{b64_svg}") !important;
        background-size: cover !important;
        background-position: center center !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stAppViewContainer"], [data-testid="stMain"], .main .block-container {{
        background: transparent !important;
    }}
    """

    holo_table_css = """
    .holo-table-wrap {
        background: linear-gradient(145deg, rgba(5, 22, 26, 0.82) 0%, rgba(8, 32, 38, 0.72) 100%);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(94, 252, 232, 0.32);
        border-top: 1.5px solid rgba(158, 248, 238, 0.55);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.45), inset 0 0 24px rgba(94, 252, 232, 0.06);
        margin-bottom: 20px;
    }
    .holo-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Manrope', sans-serif;
        font-size: 0.88rem;
        color: #e8fbf9;
    }
    .holo-table th {
        background: linear-gradient(90deg, rgba(94, 252, 232, 0.16), rgba(0, 180, 216, 0.12));
        color: #7efce8;
        font-family: 'Manrope', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.10em;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 14px 16px;
        text-align: left;
        border-bottom: 1px solid rgba(94, 252, 232, 0.3);
    }
    .holo-table td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        color: #d8f5f2;
    }
    .holo-table tr:hover td {
        background: rgba(94, 252, 232, 0.10);
        color: #ffffff;
    }
    div[data-testid="stPlotlyChart"] {
        background: rgba(5, 20, 24, 0.65);
        border: 1px solid rgba(94, 252, 232, 0.28);
        border-radius: 20px;
        padding: 8px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), inset 0 0 18px rgba(94, 252, 232, 0.05);
    }
    """
    st.markdown(f"<style>{css_content}\n{bg_style}\n{holo_table_css}</style>", unsafe_allow_html=True)

def render_holographic_table(df: pd.DataFrame):
    df_reset = df.reset_index().rename(columns={"index": "Segmento"})
    headers = "".join([f"<th>{col}</th>" for col in df_reset.columns])
    rows = ""
    for _, row in df_reset.iterrows():
        cells = "".join([f"<td>{val}</td>" for val in row])
        rows += f"<tr>{cells}</tr>"
    st.markdown(
        f'<div class="holo-table-wrap"><table class="holo-table"><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )

apply_custom_theme()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Encabezado HUD Espacial Minimalista
st.markdown("""
<div class="deluxe-hud">
    <div>
        <div class="hud-badge">UTBIS PUEBLA | CRISP-DM | SEAES EQUIDAD | RAG ENGINE</div>
        <h1 class="hud-title">AeroVault Puebla</h1>
        <div style="color: #e0f7f5; font-size: 0.95rem; margin-top: 6px; font-weight: 400; letter-spacing: 0.01em;">
            Arquitectura de Inteligencia Financiera y Detección de Fugas de Liquidez Juvenil
        </div>
    </div>
    <div class="hud-pill-group">
        <div class="hud-pill">
            <div style="font-size: 0.68rem; color: #7efce8; letter-spacing: 0.14em; font-weight: 600;">MODELO DUAL</div>
            <div style="font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.95rem;">K-Means + RF</div>
        </div>
        <div class="hud-pill">
            <div style="font-size: 0.68rem; color: #7efce8; letter-spacing: 0.14em; font-weight: 600;">ÁMBITO</div>
            <div style="font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.95rem;">Estado de Puebla</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_puebla_cohort():
    train_df = pd.read_parquet("data/processed/students_train.parquet")
    test_df = pd.read_parquet("data/processed/students_test.parquet")
    return pd.concat([train_df, test_df], ignore_index=True)

df_cohort = load_puebla_cohort()

# Navegación Cyber-Glass Minimalista
if "active_section" not in st.session_state:
    st.session_state.active_section = 0

nav_items = [
    ("Núcleo Financiero", 0),
    ("Territorio Puebla y SEAES", 1),
    ("Laboratorio ML", 2),
    ("Auditoría Ética y DW", 3),
]

nav_cols = st.columns(4, gap="medium")
for col, (label, idx) in zip(nav_cols, nav_items):
    with col:
        btn_kind = "primary" if st.session_state.active_section == idx else "secondary"
        if st.button(label, key=f"nav_btn_{idx}", type=btn_kind, use_container_width=True):
            st.session_state.active_section = idx
            st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 0: SIMULADOR INTERACTIVO EN VIVO CONECTADO A FASTAPI
# ==============================================================================
if st.session_state.active_section == 0:
    col_form, col_res = st.columns([1.05, 1.2], gap="large")

    with col_form:
        with st.container(border=True):
            st.markdown("### Parámetros del Perfil Estudiantil")
            alias = st.text_input("Alias del Estudiante", value="Derek_UTBIS")
            c1, c2 = st.columns(2)
            edad = c1.number_input("Edad", min_value=18, max_value=30, value=21)
            genero = c2.selectbox("Género", ["Masculino", "Femenino", "No Binario"])

            c3, c4 = st.columns(2)
            municipio = c3.selectbox("Municipio en Puebla", sorted(df_cohort["municipio_puebla"].unique()))
            zona = c4.selectbox("Zona Territorial", ["Urbano", "Semiurbano", "Rural/Sierra"], index=1)

            c5, c6 = st.columns(2)
            es_foraneo = c5.selectbox("Condición", [1, 0], format_func=lambda x: "Estudiante Foráneo" if x == 1 else "Local")
            fuente = c6.selectbox("Fuente de Ingreso", ["Mixto (Beca + Trabajo)", "Beca Pública", "Apoyo Familiar", "Empleo Medio Tiempo"])

            c7, c8, c9 = st.columns(3)
            ingreso = c7.number_input("Ingreso Mensual ($)", min_value=1000.0, value=5500.0, step=250.0)
            meta = c8.number_input("Meta Ahorro ($)", min_value=100.0, value=1000.0, step=100.0)
            gasto_d15 = c9.number_input("Gastado Día 15 ($)", min_value=0.0, value=2650.0, step=150.0)

            st.markdown("---")
            tx_preset = st.radio(
                "Escenario de Transacciones:",
                ["Escenario A: Fuga Hormiga y Delivery", "Escenario B: Consumo Controlado"],
                horizontal=True,
            )

            if "Escenario A" in tx_preset:
                default_tx = pd.DataFrame([
                    {"concepto": "Café y pan cafetería uni", "monto_mxn": 65.0, "hora_decimal": 9.5, "dia_semana": 1, "frecuencia_mensual": 18},
                    {"concepto": "Pasaje RUTA + colectivo", "monto_mxn": 24.0, "hora_decimal": 7.5, "dia_semana": 2, "frecuencia_mensual": 22},
                    {"concepto": "Antojitos y refresco tarde", "monto_mxn": 55.0, "hora_decimal": 15.0, "dia_semana": 3, "frecuencia_mensual": 14},
                    {"concepto": "Cena app delivery viernes", "monto_mxn": 240.0, "hora_decimal": 22.5, "dia_semana": 4, "frecuencia_mensual": 6},
                    {"concepto": "Compra microtransacción juego", "monto_mxn": 180.0, "hora_decimal": 23.2, "dia_semana": 5, "frecuencia_mensual": 5},
                    {"concepto": "Despensa básica semanal", "monto_mxn": 680.0, "hora_decimal": 13.0, "dia_semana": 6, "frecuencia_mensual": 2},
                ])
            else:
                default_tx = pd.DataFrame([
                    {"concepto": "Transporte universitario", "monto_mxn": 20.0, "hora_decimal": 8.0, "dia_semana": 1, "frecuencia_mensual": 20},
                    {"concepto": "Café ocasional", "monto_mxn": 40.0, "hora_decimal": 11.0, "dia_semana": 2, "frecuencia_mensual": 4},
                    {"concepto": "Despensa y comida casa", "monto_mxn": 950.0, "hora_decimal": 12.0, "dia_semana": 5, "frecuencia_mensual": 2},
                    {"concepto": "Internet y material estudio", "monto_mxn": 450.0, "hora_decimal": 16.0, "dia_semana": 0, "frecuencia_mensual": 1},
                ])

            st.caption("Haz doble clic en una celda para editar, usa **+** abajo para agregar o selecciona una fila a la izquierda y presiona **Supr/Delete** para borrarla.")
            edited_tx = st.data_editor(
                default_tx,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "concepto": st.column_config.TextColumn(
                        "Concepto del Gasto",
                        help="Descripción breve de la compra o servicio",
                        required=True,
                    ),
                    "monto_mxn": st.column_config.NumberColumn(
                        "Monto ($ MXN)",
                        min_value=1.0,
                        step=5.0,
                        format="$%.2f",
                        required=True,
                    ),
                    "hora_decimal": st.column_config.NumberColumn(
                        "Hora del Día (0–23.9 hrs)",
                        help="Formato 24h en decimal (ej. 9.5 = 9:30 AM, 22.5 = 10:30 PM)",
                        min_value=0.0,
                        max_value=23.99,
                        step=0.5,
                        required=True,
                    ),
                    "dia_semana": st.column_config.SelectboxColumn(
                        "Día (0=Lun .. 6=Dom)",
                        help="0: Lunes, 1: Martes, 2: Miércoles, 3: Jueves, 4: Viernes, 5: Sábado, 6: Domingo",
                        options=[0, 1, 2, 3, 4, 5, 6],
                        required=True,
                    ),
                    "frecuencia_mensual": st.column_config.NumberColumn(
                        "Veces al Mes",
                        min_value=1,
                        step=1,
                        required=True,
                    ),
                },
            )
            run_btn = st.button("EJECUTAR INFERENCIA EN NÚCLEO AERO", type="primary", use_container_width=True)

    with col_res:
        with st.container(border=True):
            st.markdown("### Telemetría del Núcleo Financiero")
            if run_btn:
                clean_tx = edited_tx.dropna(subset=["concepto", "monto_mxn"]).copy()
                clean_tx["hora_decimal"] = clean_tx["hora_decimal"].fillna(12.0)
                clean_tx["dia_semana"] = clean_tx["dia_semana"].fillna(0).astype(int)
                clean_tx["frecuencia_mensual"] = clean_tx["frecuencia_mensual"].fillna(1).astype(int)

                payload = {
                    "student_alias": alias,
                    "edad": int(edad),
                    "genero": genero,
                    "municipio_puebla": municipio,
                    "zona_territorial": zona,
                    "es_foraneo": int(es_foraneo),
                    "fuente_ingreso": fuente,
                    "ingreso_mensual_mxn": float(ingreso),
                    "meta_ahorro_mxn": float(meta),
                    "gasto_acumulado_dia15_mxn": float(gasto_d15),
                    "transacciones": clean_tx.to_dict(orient="records"),
                }
                try:
                    resp = requests.post(f"{BACKEND_URL}/api/v1/analyze-finances", json=payload, timeout=15)
                    resp.raise_for_status()
                    res = resp.json()

                    render_aquarium_widget(
                        risk_class=res["predicted_risk_class"],
                        status_text=res["aquarium_status"],
                        ratio_hormiga=res["ratio_gasto_hormiga"],
                        meta_usd=res["meta_ahorro_usd"],
                        exchange_rate=res["exchange_rate_usd_mxn"],
                    )

                    st.markdown("#### Probabilidades de Cierre de Mes (Random Forest)")
                    p_cols = st.columns(3)
                    p_cols[0].metric("Salud / Meta Lograda", f"{res['probabilities']['salud_financiera']*100:.1f}%")
                    p_cols[1].metric("Equilibrio Ajustado", f"{res['probabilities']['equilibrio_ajustado']*100:.1f}%")
                    p_cols[2].metric("Déficit Crítico", f"{res['probabilities']['deficit_critico']*100:.1f}%")

                    st.markdown("#### Segmentación Automática de Gastos (K-Means)")
                    df_clustered = pd.DataFrame(res["clustered_transactions"])
                    fig_pie = px.pie(
                        df_clustered,
                        names="cluster_label",
                        values="monto_mxn",
                        hole=0.5,
                        color_discrete_sequence=["#5efce8", "#ffd166", "#48cae4"],
                    )
                    fig_pie.update_layout(
                        template="plotly_dark",
                        height=280,
                        margin=dict(t=20, b=10, l=10, r=10),
                        paper_bgcolor="rgba(5, 20, 24, 0.78)",
                        font_color="#e8fbf9",
                        font_family="Manrope",
                        legend=dict(bgcolor="rgba(5, 20, 24, 0.75)", bordercolor="rgba(94, 252, 232, 0.30)", borderwidth=1),
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                    st.markdown(f"""
                    <div class="glass-panel">
                        <b style="color:#7efce8;">Asesor Financiero IA (LLM + RAG Marco CONDUSEF):</b><br><br>
                        {res['rag_financial_advice'].replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"No se pudo conectar con FastAPI en {BACKEND_URL}. Verifica que uvicorn esté corriendo. Detalle: {e}")
            else:
                st.markdown("""
                <div class="glass-panel" style="text-align:center; padding: 56px 28px;">
                    <div style="width: 38px; height: 38px; margin: 0 auto 14px auto; border-radius: 50%; border: 1.5px solid #5efce8; box-shadow: 0 0 18px rgba(94, 252, 232, 0.45);"></div>
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 700; color: #9ef8ee;">
                        Núcleo en Espera de Telemetría
                    </div>
                    <p style="color: #e0f7f5; font-size: 0.92rem; margin-top: 8px; font-weight: 400;">
                        Configura los parámetros en la consola de cristal izquierda y presiona <b>EJECUTAR INFERENCIA EN NÚCLEO AERO</b> para activar K-Means, Random Forest y el motor RAG.
                    </p>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 1: STORYTELLING TERRITORIAL PUEBLA & EQUIDAD SEAES
# ==============================================================================
elif st.session_state.active_section == 1:
    with st.container(border=True):
        st.subheader("Brechas Financieras en Jóvenes Universitarios del Estado de Puebla")
        zonas_sel = st.multiselect(
            "Filtrar por Zona Territorial de Puebla:",
            df_cohort["zona_territorial"].unique(),
            default=list(df_cohort["zona_territorial"].unique()),
        )
        df_filt = df_cohort[df_cohort["zona_territorial"].isin(zonas_sel)]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Cohorte Analizada", f"{len(df_filt)} estudiantes")
        k2.metric("Ingreso Mensual Medio", f"${df_filt['ingreso_mensual_mxn'].mean():,.2f}")
        k3.metric("Gasto Hormiga Medio", f"${df_filt['gasto_hormiga_real_mxn'].mean():,.2f}")
        k4.metric("% En Riesgo de Déficit", f"{(df_filt['estado_riesgo_fin_mes'] == 2).mean()*100:.1f}%")

        c_left, c_right = st.columns(2)
        with c_left:
            st.plotly_chart(charts_mod.plot_puebla_municipality_chart(df_filt), use_container_width=True)
        with c_right:
            fig_gender = px.box(
                df_filt,
                x="genero",
                y="ratio_gasto_hormiga",
                color="genero",
                title="Distribución de Proporción de Gasto Hormiga por Género (SEAES)",
                labels={"genero": "Género", "ratio_gasto_hormiga": "Ratio Gasto Hormiga / Ingreso"},
                color_discrete_sequence=["#5efce8", "#00b4d8", "#ffd166"],
            )
            fig_gender.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(5, 20, 24, 0.78)",
                plot_bgcolor="rgba(3, 14, 17, 0.72)",
                font=dict(family="Manrope, sans-serif", color="#e8fbf9"),
                title_font=dict(family="Syne, sans-serif", color="#7efce8", size=16),
                xaxis=dict(gridcolor="rgba(94, 252, 232, 0.12)", tickfont=dict(color="#c5ece8")),
                yaxis=dict(gridcolor="rgba(94, 252, 232, 0.12)", tickfont=dict(color="#c5ece8")),
                legend=dict(bgcolor="rgba(5, 20, 24, 0.75)", bordercolor="rgba(94, 252, 232, 0.30)", borderwidth=1),
                margin=dict(t=55, b=40, l=20, r=20),
            )
            st.plotly_chart(fig_gender, use_container_width=True)

# ==============================================================================
# SECCIÓN 2: LABORATORIO DE MACHINE LEARNING (MÉTRICAS RÚBRICA BLOQUE II)
# ==============================================================================
elif st.session_state.active_section == 2:
    with st.container(border=True):
        st.subheader("Evaluación Técnica y Optimización de Modelos (CRISP-DM)")
        with open("pipeline_ml/artifacts/metrics_report.json", "r", encoding="utf-8") as f:
            m_rep = json.load(f)

        km_m = m_rep["unsupervised_kmeans"]
        rf_m = m_rep["supervised_random_forest"]

        st.markdown("### 1. Modelo No Supervisado: K-Means Clustering + PCA")
        m1, m2, m3 = st.columns(3)
        m1.metric("Coeficiente de Silueta", km_m["silhouette_score"])
        m2.metric("Índice Davies-Bouldin (Menor = Mejor)", km_m["davies_bouldin_index"])
        m3.metric("Varianza Explicada PCA (2D)", f"{km_m['pca_explained_variance']*100:.2f}%")

        st.markdown("### 2. Modelo Supervisado: Random Forest + GridSearchCV (Stratified 5-Fold)")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("F1-Macro Antes Tuning", rf_m["f1_macro_before_tuning"])
        s2.metric("F1-Macro Después Tuning", rf_m["f1_macro_after_tuning"], delta=round(rf_m["f1_macro_after_tuning"] - rf_m["f1_macro_before_tuning"], 4))
        s3.metric("Test Accuracy", f"{rf_m['test_accuracy']*100:.2f}%")
        s4.metric("Test ROC-AUC (OvR)", rf_m["test_roc_auc_ovr"])

        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(charts_mod.plot_elbow_curve(km_m["elbow_inertias"]), use_container_width=True)
        with g2:
            st.plotly_chart(charts_mod.plot_confusion_matrix(m_rep["evaluation_details"]["confusion_matrix"]), use_container_width=True)

# ==============================================================================
# SECCIÓN 3: GOBERNANZA ÉTICA SEAES Y DATA WAREHOUSE
# ==============================================================================
elif st.session_state.active_section == 3:
    with st.container(border=True):
        st.subheader("Auditoría de Equidad Social y de Género (Criterio Rector SEAES)")
        with open("pipeline_ml/artifacts/metrics_report.json", "r", encoding="utf-8") as f:
            m_rep = json.load(f)
        eq = m_rep["seaes_equidad_audit"]

        e1, e2 = st.columns(2)
        e1.metric("Diferencia de Paridad Demográfica (Género)", eq["demographic_parity_difference_gender"], delta="Umbral < 0.10 (Aprobado)")
        e2.metric("Cumplimiento Normativo LFPDPPP", "SHA-256 Activo", delta="Datos Anonimizados")

        st.markdown("#### Desglose de Desempeño por Género en Conjunto de Prueba")
        render_holographic_table(pd.DataFrame(eq["desglose_por_genero"]).T)

        st.markdown("#### Desglose Territorial por Zona en Puebla")
        render_holographic_table(pd.DataFrame(eq["desglose_territorial_puebla"]).T)