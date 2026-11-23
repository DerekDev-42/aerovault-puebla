import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

HOLO_DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(5, 20, 24, 0.78)",
    plot_bgcolor="rgba(3, 14, 17, 0.72)",
    font=dict(family="Outfit, sans-serif", color="#e8fbf9", size=12),
    title_font=dict(family="Space Grotesk, sans-serif", color="#7efce8", size=16),
    xaxis=dict(
        gridcolor="rgba(94, 252, 232, 0.12)",
        zerolinecolor="rgba(94, 252, 232, 0.22)",
        tickfont=dict(color="#c5ece8"),
        title_font=dict(color="#9ef8ee"),
    ),
    yaxis=dict(
        gridcolor="rgba(94, 252, 232, 0.12)",
        zerolinecolor="rgba(94, 252, 232, 0.22)",
        tickfont=dict(color="#c5ece8"),
        title_font=dict(color="#9ef8ee"),
    ),
    legend=dict(
        bgcolor="rgba(5, 20, 24, 0.75)",
        bordercolor="rgba(94, 252, 232, 0.30)",
        borderwidth=1,
        font=dict(color="#e8fbf9"),
    ),
    margin=dict(t=55, b=40, l=20, r=20),
)

def plot_puebla_municipality_chart(df: pd.DataFrame):
    summary = df.groupby(["municipio_puebla", "zona_territorial"], as_index=False).agg(
        ingreso_medio=("ingreso_mensual_mxn", "mean"),
        gasto_hormiga_medio=("gasto_hormiga_real_mxn", "mean"),
        estudiantes=("student_id", "count"),
    )
    fig = px.bar(
        summary.sort_values("gasto_hormiga_medio", ascending=True),
        x="gasto_hormiga_medio",
        y="municipio_puebla",
        color="zona_territorial",
        orientation="h",
        title="Gasto Hormiga Promedio Mensual por Municipio en Puebla (MXN)",
        labels={
            "gasto_hormiga_medio": "Gasto Hormiga (MXN)",
            "municipio_puebla": "Municipio",
            "zona_territorial": "Zona",
        },
        color_discrete_sequence=["#5efce8", "#00b4d8", "#736efe"],
    )
    fig.update_traces(marker_line_color="rgba(255,255,255,0.4)", marker_line_width=1)
    fig.update_layout(**HOLO_DARK_LAYOUT)
    return fig

def plot_elbow_curve(elbow_dict: dict):
    ks = [int(k.split("_")[1]) for k in elbow_dict.keys()]
    inertias = list(elbow_dict.values())
    fig = go.Figure(
        data=go.Scatter(
            x=ks,
            y=inertias,
            mode="lines+markers",
            line=dict(color="#5efce8", width=3.5),
            marker=dict(size=11, color="#00b4d8", line=dict(color="#ffffff", width=2)),
            fill="tozeroy",
            fillcolor="rgba(94, 252, 232, 0.08)",
        )
    )
    fig.update_layout(
        title="Método del Codo (Inercia K-Means)",
        xaxis_title="Número de Clústeres (k)",
        yaxis_title="Inercia Intra-Clúster",
        **HOLO_DARK_LAYOUT,
    )
    return fig

def plot_confusion_matrix(cm: list):
    labels = ["Salud Financiera (0)", "Equilibrio (1)", "Déficit Crítico (2)"]
    fig = px.imshow(
        cm,
        x=labels,
        y=labels,
        text_auto=True,
        color_continuous_scale=[[0.0, "#041215"], [0.45, "#005f73"], [1.0, "#5efce8"]],
        title="Matriz de Confusión — Random Forest (Test Puebla)",
    )
    fig.update_traces(textfont=dict(color="#ffffff", size=15, family="Space Grotesk"))
    fig.update_layout(**HOLO_DARK_LAYOUT)
    return fig