import streamlit as st

def render_aquarium_widget(risk_class: int, status_text: str, ratio_hormiga: float, meta_usd: float, exchange_rate: float):
    """Renderiza el Acuario Financiero Frutiger Aero según la predicción de Random Forest."""
    if risk_class == 0:
        css_class = "aquarium-crystal"
        emoji_env = "🐠 🫧 🌿 ☀️"
        desc = "Agua cristalina: Tu ritmo de ahorro protege tu meta mensual y mantiene a raya los gastos hormiga."
    elif risk_class == 1:
        css_class = "aquarium-warning"
        emoji_env = "🐡 💧 🌾 ⛅"
        desc = "Agua semi-turbia: Llegarás a fin de mes sin deuda, pero las fugas diarias están frenando tu meta de ahorro."
    else:
        css_class = "aquarium-danger"
        emoji_env = "⚠️ 🫧 🌊 ⛈️"
        desc = "Alerta de turbidez crítica: Alta probabilidad de déficit antes de la segunda quincena."

    html_block = f"""
    <div class="aquarium-box {css_class}">
        <div style="font-size: 2.2rem; margin-bottom: 6px;">{emoji_env}</div>
        <h3 style="margin: 0; font-weight: 800;">Estado del Acuario: {status_text}</h3>
        <p style="margin: 8px 0 14px 0; font-size: 0.95rem; font-weight: 500;">{desc}</p>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px; background: rgba(255,255,255,0.35); border-radius: 14px; padding: 12px;">
            <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; font-weight: 700;">Índice Gasto Hormiga</span><br>
                <span style="font-size: 1.3rem; font-weight: 800;">{ratio_hormiga * 100:.1f}%</span>
            </div>
            <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; font-weight: 700;">Meta en Divisa (API Vivo)</span><br>
                <span style="font-size: 1.3rem; font-weight: 800;">${meta_usd:,.2f} USD</span>
            </div>
            <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; font-weight: 700;">Tipo de Cambio</span><br>
                <span style="font-size: 1.3rem; font-weight: 800;">${exchange_rate:.2f} MXN</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html_block, unsafe_allow_html=True)