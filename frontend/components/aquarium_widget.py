import streamlit as st


def _get_aero_cube_plant_svg(risk_class: int) -> str:
    """Genera un ícono SVG Frutiger Aero de un dado de cristal con una plantita brotando."""
    if risk_class == 0:  # Óptimo
        cube_stroke = "#7ef9ff"
        cube_fill = "rgba(126, 249, 255, 0.22)"
        leaf_main = "#39ff88"
        leaf_shadow = "#14b866"
        glow = "rgba(0, 240, 255, 0.40)"
    elif risk_class == 1:  # Semi-Turbio (Precaución)
        cube_stroke = "#ffe680"
        cube_fill = "rgba(255, 230, 128, 0.20)"
        leaf_main = "#a3ff57"
        leaf_shadow = "#5ec229"
        glow = "rgba(255, 230, 128, 0.35)"
    else:  # Crítico
        cube_stroke = "#ff8585"
        cube_fill = "rgba(255, 133, 133, 0.20)"
        leaf_main = "#ff9f43"
        leaf_shadow = "#d96b14"
        glow = "rgba(255, 133, 133, 0.35)"

    return (
        f'<svg width="56" height="56" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" '
        f'style="filter: drop-shadow(0 4px 10px {glow});">'
        f'<polygon points="32,16 52,27 52,49 32,60 12,49 12,27" '
        f'fill="{cube_fill}" stroke="{cube_stroke}" stroke-width="2" stroke-linejoin="round"/>'
        f'<polyline points="12,27 32,38 52,27" stroke="{cube_stroke}" stroke-width="1.6" stroke-opacity="0.75" fill="none"/>'
        f'<line x1="32" y1="38" x2="32" y2="60" stroke="{cube_stroke}" stroke-width="1.6" stroke-opacity="0.75"/>'
        f'<circle cx="20" cy="40" r="1.8" fill="#ffffff" fill-opacity="0.8"/>'
        f'<circle cx="25" cy="46" r="1.8" fill="#ffffff" fill-opacity="0.8"/>'
        f'<circle cx="43" cy="42" r="2" fill="#ffffff" fill-opacity="0.8"/>'
        f'<path d="M32 34 C32 26, 32 20, 32 14" stroke="{leaf_main}" stroke-width="2.6" stroke-linecap="round"/>'
        f'<path d="M32 22 C24 21, 19 15, 21 10 C27 10, 31 15, 32 22 Z" '
        f'fill="{leaf_main}" stroke="{leaf_shadow}" stroke-width="1"/>'
        f'<path d="M32 18 C39 16, 45 11, 43 6 C37 6, 33 11, 32 18 Z" '
        f'fill="{leaf_main}" stroke="{leaf_shadow}" stroke-width="1"/>'
        f'<ellipse cx="23" cy="24" rx="4" ry="1.6" transform="rotate(-25 23 24)" fill="#ffffff" fill-opacity="0.65"/>'
        f'</svg>'
    )


def render_aquarium_widget(
    risk_class: int,
    status_text: str,
    ratio_hormiga: float,
    meta_usd: float,
    exchange_rate: float,
) -> None:
    if risk_class == 0:
        css_class = "status-optimal"
        desc = "Agua cristalina: Tu ritmo de gasto está alineado con tu meta de ahorro mensual."
    elif risk_class == 1:
        css_class = "status-warning"
        desc = "Agua semi-turbia: Llegarás a fin de mes sin deuda, pero las fugas diarias están frenando tu meta de ahorro."
    else:
        css_class = "status-critical"
        desc = "Alerta de turbidez crítica: Alta probabilidad de déficit antes de la segunda quincena."

    icon_svg = _get_aero_cube_plant_svg(risk_class)

    html_block = f"""
    <div class="aquarium-box {css_class}">
        <div style="margin-bottom: 8px; display: flex; align-items: center;">{icon_svg}</div>
        <h3 style="margin: 0; font-weight: 800;">Estado del Acuario: {status_text}</h3>
        <p style="margin: 8px 0 14px 0; font-size: 0.95rem; font-weight: 500;">{desc}</p>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 12px;">
            <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; font-weight: 700; opacity: 0.85;">ÍNDICE GASTO HORMIGA</span><br>
                <span style="font-size: 1.3rem; font-weight: 800;">{ratio_hormiga * 100:.1f}%</span>
            </div>
            <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; font-weight: 700; opacity: 0.85;">META EN DIVISA (API VIVO)</span><br>
                <span style="font-size: 1.3rem; font-weight: 800;">${meta_usd:,.2f} USD</span>
            </div>
            <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; font-weight: 700; opacity: 0.85;">TIPO DE CAMBIO</span><br>
                <span style="font-size: 1.3rem; font-weight: 800;">${exchange_rate:.2f} MXN</span>
            </div>
        </div>
    </div>
    """

    st.markdown(html_block, unsafe_allow_html=True)