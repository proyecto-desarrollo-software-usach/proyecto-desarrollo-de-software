from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from explore_exoplanets import (
    available_plot_columns,
    load_catalog,
)

PLOTLY_CONFIG = {
    "responsive": True,
    "displaylogo": False,
    "scrollZoom": False,
}

# El catálogo se vuelve a consultar automáticamente en NASA cada 24 horas.
# Streamlit conserva el resultado entre ejecuciones dentro de este intervalo.
CATALOG_REFRESH_SECONDS = 24 * 60 * 60

# -----------------------------------------------------------------------------
# Identidad visual del Atlas
# -----------------------------------------------------------------------------
# Se evita el patrón visual típico de dashboard "IA" (Inter + tarjetas muy
# redondeadas + gradientes azules). La interfaz toma una estética de catálogo
# científico / panel de observación: superficies planas, líneas finas, tipografía
# técnica y acentos cálidos.
THEME_TOKENS = {
    "dark": {
        "bg": "#0B1015",
        "bg_alt": "#0F161D",
        "surface": "#121B23",
        "surface_strong": "#18232D",
        "surface_hover": "#21303B",
        "text": "#E9EEF2",
        "text_soft": "#C3CDD5",
        "text_muted": "#8F9CA7",
        "border": "#2A3945",
        "border_strong": "#435563",
        "accent": "#F2A341",
        "accent_soft": "#FFD08A",
        "accent_2": "#45B8A8",
        "danger": "#F06A61",
        "grid": "rgba(143, 156, 167, 0.095)",
        "shadow": "rgba(0, 0, 0, 0.30)",
    },
    "light": {
        "bg": "#F3F0E8",
        "bg_alt": "#ECE7DC",
        "surface": "#FBF8F1",
        "surface_strong": "#F4EEE3",
        "surface_hover": "#E9E1D4",
        "text": "#20272D",
        "text_soft": "#46515A",
        "text_muted": "#6B777F",
        "border": "#D3CABD",
        "border_strong": "#A99D8E",
        "accent": "#A94C1F",
        "accent_soft": "#C76A37",
        "accent_2": "#0B746B",
        "danger": "#A83C35",
        "grid": "rgba(70, 81, 90, 0.085)",
        "shadow": "rgba(47, 39, 28, 0.10)",
    },
}

PLOT_THEMES = {
    "dark": {
        "text": "#E9EEF2",
        "muted": "#9BA8B2",
        "grid": "rgba(155, 168, 178, 0.14)",
        "axis": "#81909C",
        "legend_bg": "rgba(18, 27, 35, 0.96)",
        "legend_border": "#344551",
        "marker_border": "#0B1015",
        "single": "#F2A341",
        "palette": [
            "#4DA3FF",  # azul
            "#FF9D2E",  # naranja
            "#40C98A",  # verde
            "#F05B61",  # rojo
            "#B983FF",  # violeta
            "#F0D04C",  # amarillo
            "#2EC4B6",  # turquesa
            "#FF6FAE",  # magenta
            "#A8C94A",  # lima
            "#C98B5B",  # cobre
            "#8FA6FF",  # índigo
            "#F38B7A",  # coral
        ],
        "continuous": [
            [0.00, "#3A2C74"],
            [0.20, "#3558A6"],
            [0.40, "#1F8A9E"],
            [0.60, "#3DB57C"],
            [0.80, "#E1BE3E"],
            [1.00, "#EE7048"],
        ],
    },
    "light": {
        "text": "#20272D",
        "muted": "#63717A",
        "grid": "rgba(70, 81, 90, 0.14)",
        "axis": "#74818A",
        "legend_bg": "rgba(251, 248, 241, 0.96)",
        "legend_border": "#C9BFB1",
        "marker_border": "#FFFDF8",
        "single": "#A94C1F",
        "palette": [
            "#005FB8",  # azul
            "#C96800",  # naranja
            "#087A4E",  # verde
            "#C83E46",  # rojo
            "#7442A8",  # violeta
            "#A27A00",  # mostaza
            "#007C74",  # turquesa
            "#B83272",  # magenta
            "#627D16",  # oliva
            "#8E542D",  # cobre
            "#4D5FB8",  # índigo
            "#B95342",  # coral oscuro
        ],
        "continuous": [
            [0.00, "#38236D"],
            [0.20, "#244B91"],
            [0.40, "#087A86"],
            [0.60, "#238A5B"],
            [0.80, "#B38B00"],
            [1.00, "#C94D2E"],
        ],
    },
}

MARKER_SYMBOLS = [
    "circle",
    "diamond",
    "square",
    "triangle-up",
    "cross",
    "x",
    "star",
    "hexagon",
    "triangle-down",
    "pentagon",
    "hourglass",
    "bowtie",
]

DISCOVERY_METHOD_ES = {
    "Transit": "Tránsito",
    "Radial Velocity": "Velocidad radial",
    "Imaging": "Imagen directa",
    "Microlensing": "Microlente gravitacional",
    "Pulsar Timing": "Cronometría de púlsares",
    "Transit Timing Variations": "Variaciones del tiempo de tránsito",
    "Eclipse Timing Variations": "Variaciones del tiempo de eclipse",
    "Orbital Brightness Modulation": "Modulación del brillo orbital",
    "Astrometry": "Astrometría",
    "Pulsation Timing Variations": "Variaciones temporales de pulsación",
    "Disk Kinematics": "Cinemática de disco",
}

DEFAULT_COLUMN_LABELS = {
    "pl_name": "Exoplaneta",
    "hostname": "Estrella anfitriona",
    "discoverymethod": "Método de descubrimiento",
    "system_planet_count": "Planetas en el sistema",
    "pl_orbsmax": "Semieje mayor (UA)",
    "pl_orbper": "Período orbital (días)",
    "pl_rade": "Radio (radios terrestres)",
    "pl_bmasse": "Masa (masas terrestres)",
    "pl_orbeccen": "Excentricidad orbital",
    "st_mass": "Masa estelar (masas solares)",
    "st_teff": "Temperatura estelar (K)",
    "sy_pnum": "Planetas en el sistema",
    "sy_snum": "Estrellas en el sistema",
}

TABLE_COLUMN_LABELS = {
    "pl_name": "Exoplaneta",
    "hostname": "Estrella anfitriona",
    "discoverymethod": "Método de descubrimiento",
    "pl_orbsmax": "Semieje mayor (UA)",
    "pl_orbper": "Período orbital (días)",
    "pl_rade": "Radio (R⊕)",
    "pl_bmasse": "Masa (M⊕)",
    "pl_orbeccen": "Excentricidad",
    "st_mass": "Masa estelar (M☉)",
    "st_teff": "Temperatura estelar (K)",
}

BASE_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background-color: var(--atlas-bg);
    background-image:
        linear-gradient(var(--atlas-grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--atlas-grid) 1px, transparent 1px);
    background-size: 46px 46px;
    color: var(--atlas-text);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--atlas-text) !important;
    letter-spacing: -0.02em;
}

p, label, li,
[data-testid="stCaptionContainer"],
[data-testid="stMarkdownContainer"] {
    color: var(--atlas-text-soft);
}

[data-testid="stCaptionContainer"] p {
    color: var(--atlas-text-muted) !important;
}

/* Cabecera: catálogo científico, no tarjeta genérica con gradiente. */
.hero {
    position: relative;
    margin-bottom: 2.1rem;
    padding: 2.15rem 2.35rem 1.7rem;
    overflow: hidden;
    background: var(--atlas-surface);
    border: 1px solid var(--atlas-border-strong);
    border-radius: 8px;
    box-shadow: 8px 8px 0 var(--atlas-bg-alt);
}

.hero::before,
.hero::after {
    content: '';
    position: absolute;
    pointer-events: none;
}

.hero::before {
    inset: 0;
    background:
        linear-gradient(90deg, transparent 49.7%, var(--atlas-grid) 50%, transparent 50.3%),
        linear-gradient(transparent 49.7%, var(--atlas-grid) 50%, transparent 50.3%);
    background-size: 90px 90px;
    opacity: 0.7;
}

.hero::after {
    top: 0;
    left: 0;
    width: 84px;
    height: 4px;
    background: var(--atlas-accent);
}

.hero > * {
    position: relative;
    z-index: 1;
}

.hero-kicker {
    margin-bottom: 0.75rem;
    color: var(--atlas-accent) !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.hero h1 {
    margin: 0 0 0.8rem;
    color: var(--atlas-text) !important;
    font-size: clamp(2.15rem, 5vw, 3.35rem);
    font-weight: 700;
    line-height: 1;
}

.hero p {
    max-width: 830px;
    margin: 0;
    color: var(--atlas-text-soft) !important;
    font-size: 1.02rem;
    line-height: 1.65;
}

.hero-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem 1.25rem;
    margin-top: 1.35rem;
    padding-top: 0.9rem;
    border-top: 1px solid var(--atlas-border);
    color: var(--atlas-text-muted);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.hero-meta strong {
    color: var(--atlas-accent-2);
    font-weight: 600;
}

/* Contenedores: más parecidos a módulos de observatorio que a cards. */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 8px;
    border-color: var(--atlas-border) !important;
    background: color-mix(in srgb, var(--atlas-surface) 94%, transparent);
}

[data-testid="stMetric"] {
    position: relative;
    min-height: 112px;
    padding: 1.15rem 1.2rem;
    background: var(--atlas-surface);
    border: 1px solid var(--atlas-border);
    border-radius: 6px;
    box-shadow: none;
}

[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    width: 28px;
    height: 3px;
    background: var(--atlas-accent);
}

[data-testid="stMetricLabel"] p {
    color: var(--atlas-text-muted) !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    font-weight: 500;
    letter-spacing: 0.035em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: var(--atlas-text) !important;
    font-weight: 700;
    letter-spacing: -0.03em;
}

[data-testid="stMainBlockContainer"] > div > div {
    gap: 1.05rem;
}

[data-testid="stVerticalBlock"] {
    gap: 0.95rem;
}

[data-testid="stHorizontalBlock"] {
    gap: 0.9rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--atlas-bg-alt) !important;
    border-right: 1px solid var(--atlas-border) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: var(--atlas-text) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] span {
    color: var(--atlas-text-soft) !important;
}

[data-testid="stSidebar"] h3 {
    margin-top: 0.3rem;
    margin-bottom: 0.7rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    font-weight: 600;
    letter-spacing: 0.055em;
    text-transform: uppercase;
}

[data-testid="stSidebar"] hr,
hr {
    border-color: var(--atlas-border) !important;
}

/* Menús emergentes y selects: todos siguen el tema activo. */
div[data-baseweb="popover"] {
    color: var(--atlas-text) !important;
}

div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {
    background: var(--atlas-surface-strong) !important;
    border: 1px solid var(--atlas-border) !important;
}

div[data-baseweb="menu"] li {
    color: var(--atlas-text) !important;
}

div[data-baseweb="menu"] li:hover {
    background: var(--atlas-surface-hover) !important;
    color: var(--atlas-text) !important;
}

[data-testid="stSidebar"] input::placeholder {
    color: var(--atlas-text-muted) !important;
    opacity: 1;
}

/* Botones sobrios, con geometría menos genérica. */
.stButton > button,
.stDownloadButton > button {
    min-height: 40px;
    border: 1px solid var(--atlas-border-strong) !important;
    border-radius: 5px !important;
    background: var(--atlas-surface-strong) !important;
    color: var(--atlas-text) !important;
    font-weight: 600;
    box-shadow: 3px 3px 0 var(--atlas-bg-alt);
    transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
}

.stButton > button p,
.stDownloadButton > button p {
    color: var(--atlas-text) !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--atlas-accent) !important;
    color: var(--atlas-text) !important;
    transform: translate(-1px, -1px);
    box-shadow: 5px 5px 0 var(--atlas-bg-alt);
}

.stButton > button:focus,
.stDownloadButton > button:focus {
    border-color: var(--atlas-accent) !important;
    box-shadow: 0 0 0 2px color-mix(in srgb, var(--atlas-accent) 22%, transparent) !important;
}

/* Sliders / toggles */
[data-baseweb="slider"] div[role="slider"] {
    background-color: var(--atlas-accent) !important;
    border-color: var(--atlas-accent) !important;
}

[data-testid="stCheckbox"] input:checked + div,
[role="switch"][aria-checked="true"] {
    background-color: var(--atlas-accent-2) !important;
}

/* Pestañas tipo ficha de catálogo, no pills. */
[data-baseweb="tab-list"] {
    gap: 0;
    overflow-x: auto;
    overflow-y: hidden;
    border-bottom: 1px solid var(--atlas-border);
    white-space: nowrap;
}

[data-baseweb="tab"] {
    flex-shrink: 0;
    border-radius: 0 !important;
    border-right: 1px solid var(--atlas-border);
    color: var(--atlas-text-muted) !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.02em;
}

[data-baseweb="tab"][aria-selected="true"] {
    background: var(--atlas-surface) !important;
    color: var(--atlas-text) !important;
}

[data-baseweb="tab-highlight"] {
    height: 3px !important;
    background-color: var(--atlas-accent) !important;
}

.block-container {
    max-width: 1560px;
    padding-top: 1.45rem;
    padding-bottom: 3rem;
    padding-left: clamp(1rem, 3.4vw, 3.6rem);
    padding-right: clamp(1rem, 3.4vw, 3.6rem);
}

[data-testid="stMainBlockContainer"],
[data-testid="stPlotlyChart"],
[data-testid="stDataFrame"] {
    width: 100% !important;
    max-width: 100% !important;
}

[data-testid="stPlotlyChart"] > div,
[data-testid="stPlotlyChart"] iframe {
    width: 100% !important;
    max-width: 100% !important;
}

h1, h2, h3, p, label, [data-testid="stMetricLabel"] {
    overflow-wrap: anywhere;
}

@media (max-width: 1024px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 1.7rem;
        margin-bottom: 1.6rem;
        box-shadow: 6px 6px 0 var(--atlas-bg-alt);
    }
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 0.7rem;
        padding-bottom: 1.4rem;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
    }

    .hero {
        padding: 1.25rem 1rem;
        margin-bottom: 1.1rem;
        border-radius: 6px;
        box-shadow: 4px 4px 0 var(--atlas-bg-alt);
    }

    .hero-kicker {
        font-size: 0.68rem;
        line-height: 1.35;
    }

    .hero h1 {
        font-size: clamp(1.75rem, 9vw, 2.3rem);
    }

    .hero p {
        font-size: 0.91rem;
        line-height: 1.5;
    }

    .hero-meta {
        gap: 0.45rem 0.8rem;
        font-size: 0.64rem;
    }

    h1 { font-size: 1.75rem !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.10rem !important; }

    [data-testid="stMetric"] {
        min-height: 94px;
        padding: 0.9rem;
    }

    [data-testid="stMetricLabel"] p {
        font-size: 0.70rem;
        line-height: 1.2;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.25rem;
    }

    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.8rem !important;
    }

    [data-testid="column"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 0 !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100% !important;
        min-height: 44px;
    }

    div[data-baseweb="select"],
    div[data-baseweb="input"] {
        width: 100% !important;
    }

    [data-testid="stDataFrame"] {
        overflow-x: auto;
    }
}

@media (max-width: 480px) {
    .block-container {
        padding-left: 0.45rem;
        padding-right: 0.45rem;
    }

    .hero {
        padding: 1rem 0.85rem;
    }

    [data-baseweb="tab"] {
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
    }
}
"""


PRESETS = {
    "Masa vs semieje mayor": {
        "x": "pl_orbsmax",
        "y": "pl_bmasse",
        "color": "discoverymethod",
        "log_x": True,
        "log_y": True,
    },
    "Radio vs semieje mayor": {
        "x": "pl_orbsmax",
        "y": "pl_rade",
        "color": "discoverymethod",
        "log_x": True,
        "log_y": True,
    },
    "Período vs semieje mayor": {
        "x": "pl_orbper",
        "y": "pl_orbsmax",
        "color": "pl_orbeccen",
        "log_x": True,
        "log_y": True,
    },
    "Radio vs temperatura estelar": {
        "x": "st_teff",
        "y": "pl_rade",
        "color": "st_mass",
        "log_x": False,
        "log_y": True,
    },
}


st.set_page_config(
    page_title="Atlas de Exoplanetas",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="auto",
)


def get_active_theme() -> str:
    """Devuelve el tema que Streamlit está mostrando realmente al usuario."""
    try:
        theme_type = st.context.theme.type
    except Exception:
        theme_type = "dark"

    return theme_type if theme_type in {"light", "dark"} else "dark"


def translate_discovery_method(value: object) -> str:
    if pd.isna(value):
        return "N/D"
    value_str = str(value)
    return DISCOVERY_METHOD_ES.get(value_str, value_str)


def apply_theme(theme_type: str) -> None:
    tokens = THEME_TOKENS[theme_type]
    css_variables = "\n".join(
        [
            ":root {",
            f"  --atlas-bg: {tokens['bg']};",
            f"  --atlas-bg-alt: {tokens['bg_alt']};",
            f"  --atlas-surface: {tokens['surface']};",
            f"  --atlas-surface-strong: {tokens['surface_strong']};",
            f"  --atlas-surface-hover: {tokens['surface_hover']};",
            f"  --atlas-text: {tokens['text']};",
            f"  --atlas-text-soft: {tokens['text_soft']};",
            f"  --atlas-text-muted: {tokens['text_muted']};",
            f"  --atlas-border: {tokens['border']};",
            f"  --atlas-border-strong: {tokens['border_strong']};",
            f"  --atlas-accent: {tokens['accent']};",
            f"  --atlas-accent-soft: {tokens['accent_soft']};",
            f"  --atlas-accent-2: {tokens['accent_2']};",
            f"  --atlas-danger: {tokens['danger']};",
            f"  --atlas-grid: {tokens['grid']};",
            f"  --atlas-shadow: {tokens['shadow']};",
            "}",
        ]
    )

    st.markdown(
        f"<style>{css_variables}\n{BASE_CSS}</style>",
        unsafe_allow_html=True,
    )


def get_catalog() -> pd.DataFrame:
    """
    Obtiene el catálogo más reciente desde NASA Exoplanet Archive.

    Streamlit conserva el resultado durante 24 horas para evitar descargas
    innecesarias. Cuando vence la caché, la siguiente ejecución consulta NASA
    nuevamente. Si NASA no está disponible, `load_catalog` utiliza el último
    CSV local válido como respaldo.
    """
    return load_catalog(force_download=True)


def format_axis_label(column: str, labels: dict[str, str]) -> str:
    return DEFAULT_COLUMN_LABELS.get(column, labels.get(column, column))


def set_preset_state(preset_name: str) -> None:
    preset = PRESETS[preset_name]
    st.session_state["x_axis"] = preset["x"]
    st.session_state["y_axis"] = preset["y"]
    st.session_state["color_mode"] = preset["color"]
    st.session_state["log_x"] = preset["log_x"]
    st.session_state["log_y"] = preset["log_y"]


def safe_mode_value(series: pd.Series) -> str:
    mode = series.dropna().mode()
    if mode.empty:
        return "N/D"
    return str(mode.iloc[0])


def build_scatter(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    color: str,
    size_mode: str,
    log_x: bool,
    log_y: bool,
    labels: dict[str, str],
    theme_type: str,
) -> px.scatter:
    required = ["pl_name", "hostname", "discoverymethod", x, y]

    if color != "none":
        required.append(color)

    if size_mode == "system":
        required.append("system_planet_count")

    columns = list(dict.fromkeys([column for column in required if column in df.columns]))
    plot_df = df[columns].dropna(subset=[x, y]).copy()

    if log_x:
        plot_df = plot_df[plot_df[x] > 0]

    if log_y:
        plot_df = plot_df[plot_df[y] > 0]

    plot_style = PLOT_THEMES[theme_type]

    if plot_df.empty:
        fig = px.scatter(pd.DataFrame({"x": [], "y": []}), x="x", y="y", height=560)
        fig.update_layout(
            title="No hay datos válidos para esta combinación de ejes y filtros.",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=plot_style["text"]),
        )
        return fig

    plot_df["_metodo_es"] = plot_df["discoverymethod"].map(translate_discovery_method)

    size = (
        "system_planet_count"
        if size_mode == "system" and "system_planet_count" in plot_df.columns
        else None
    )

    continuous = color in {"pl_orbeccen", "st_teff", "st_mass", "sy_pnum"}
    color_arg = None
    symbol_arg = None
    color_discrete_map = None
    symbol_map = None

    if color == "discoverymethod":
        color_arg = "_metodo_es"
        symbol_arg = "_metodo_es"
        raw_methods = sorted(plot_df["discoverymethod"].dropna().astype(str).unique().tolist())
        color_discrete_map = {
            translate_discovery_method(method): plot_style["palette"][index % len(plot_style["palette"])]
            for index, method in enumerate(raw_methods)
        }
        symbol_map = {
            translate_discovery_method(method): MARKER_SYMBOLS[index % len(MARKER_SYMBOLS)]
            for index, method in enumerate(raw_methods)
        }
    elif color != "none" and color in plot_df.columns:
        color_arg = color

    plot_labels = {
        **{column: format_axis_label(column, labels) for column in labels},
        **DEFAULT_COLUMN_LABELS,
        "_metodo_es": "Método de descubrimiento",
    }

    custom_columns = ["pl_name", "hostname", "_metodo_es"]
    if size:
        custom_columns.append("system_planet_count")

    fig = px.scatter(
        plot_df,
        x=x,
        y=y,
        color=color_arg,
        symbol=symbol_arg,
        size=size,
        custom_data=custom_columns,
        labels=plot_labels,
        color_continuous_scale=plot_style["continuous"] if continuous else None,
        color_discrete_sequence=plot_style["palette"],
        color_discrete_map=color_discrete_map,
        symbol_map=symbol_map,
        opacity=0.88,
        height=560,
    )

    x_label = format_axis_label(x, labels)
    y_label = format_axis_label(y, labels)
    hover_template = (
        "<b>%{customdata[0]}</b><br><br>"
        "Estrella anfitriona: %{customdata[1]}<br>"
        "Método de descubrimiento: %{customdata[2]}<br>"
        f"{x_label}: %{{x:.4g}}<br>"
        f"{y_label}: %{{y:.4g}}"
    )

    if size:
        hover_template += "<br>Planetas en el sistema: %{customdata[3]}"

    hover_template += "<extra></extra>"

    marker_update = dict(
        line=dict(width=0.8, color=plot_style["marker_border"]),
    )
    if color_arg is None:
        marker_update["color"] = plot_style["single"]

    fig.update_traces(
        marker=marker_update,
        hovertemplate=hover_template,
    )

    legend_title = "Método de descubrimiento" if color == "discoverymethod" else "Atributo"

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=plot_style["text"], family="IBM Plex Sans, sans-serif"),
        margin=dict(l=20, r=20, t=70, b=20),
        legend_title_text=legend_title,
        autosize=True,
        hoverlabel=dict(
            bgcolor=plot_style["legend_bg"],
            bordercolor=plot_style["legend_border"],
            font=dict(color=plot_style["text"], family="IBM Plex Sans, sans-serif"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor=plot_style["legend_bg"],
            bordercolor=plot_style["legend_border"],
            borderwidth=1,
            font=dict(color=plot_style["text"]),
        ),
    )

    if continuous and color_arg:
        fig.update_coloraxes(
            colorbar_title_text=format_axis_label(color, labels),
            colorbar_tickfont=dict(color=plot_style["text"]),
            colorbar_title_font=dict(color=plot_style["text"]),
        )

    fig.update_xaxes(
        type="log" if log_x else "linear",
        gridcolor=plot_style["grid"],
        zerolinecolor=plot_style["grid"],
        linecolor=plot_style["axis"],
        tickfont=dict(color=plot_style["muted"]),
        title_font=dict(color=plot_style["text"]),
    )

    fig.update_yaxes(
        type="log" if log_y else "linear",
        gridcolor=plot_style["grid"],
        zerolinecolor=plot_style["grid"],
        linecolor=plot_style["axis"],
        tickfont=dict(color=plot_style["muted"]),
        title_font=dict(color=plot_style["text"]),
    )

    return fig


def filter_catalog(
    df: pd.DataFrame,
    *,
    methods: list[str],
    planet_count_range: tuple[int, int],
    selected_hosts: list[str],
) -> pd.DataFrame:
    filtered = df.copy()

    # `methods` siempre representa de forma explícita los métodos que el
    # usuario quiere ver. Si la lista queda vacía en modo personalizado,
    # el resultado queda vacío en vez de restaurar filtros ocultos.
    if "discoverymethod" in filtered.columns:
        filtered = filtered[filtered["discoverymethod"].isin(methods)]

    if "system_planet_count" in filtered.columns:
        filtered = filtered[
            filtered["system_planet_count"].between(
                planet_count_range[0],
                planet_count_range[1],
            )
        ]

    if selected_hosts and "hostname" in filtered.columns:
        filtered = filtered[filtered["hostname"].isin(selected_hosts)]

    return filtered


def render_overview(df: pd.DataFrame) -> None:
    total_systems = df["hostname"].nunique()
    multi_systems = df.loc[df["system_planet_count"] > 1, "hostname"].nunique()

    with st.container(border=True):
        cols = st.columns(4)
        cols[0].metric("Planetas Confirmados", f"{len(df):,}".replace(",", "."))
        cols[1].metric("Sistemas Estelares", f"{total_systems:,}".replace(",", "."))
        cols[2].metric("Sistemas Múltiples", f"{multi_systems:,}".replace(",", "."))
        cols[3].metric("Métodos de Detección", df["discoverymethod"].nunique())


def render_sidebar(df: pd.DataFrame, labels: dict[str, str]) -> tuple[list[str], tuple[int, int], list[str], str, bool, str, bool, str, str]:
    with st.sidebar:
        st.markdown("### Panel de exploración")

        st.selectbox(
            "Vista sugerida",
            options=list(PRESETS.keys()),
            key="preset",
            on_change=lambda: set_preset_state(st.session_state["preset"]),
        )

        st.divider()
        st.markdown("### Filtros del catálogo")

        method_options = sorted(df["discoverymethod"].dropna().unique().tolist())

        # Se evita el significado ambiguo de un multiselect vacío.
        # En modo "todos", cualquier método nuevo publicado por NASA entra
        # automáticamente porque la lista proviene del catálogo descargado.
        show_all_methods = st.toggle(
            "Mostrar todos los métodos",
            value=True,
            key="show_all_methods",
            help=(
                "Incluye automáticamente todos los métodos de detección presentes "
                "en el catálogo actual de NASA, incluidos los que se incorporen en el futuro."
            ),
        )

        if show_all_methods:
            methods = method_options
            st.caption(f"{len(method_options)} métodos incluidos automáticamente.")
        else:
            methods = st.multiselect(
                "Métodos de descubrimiento",
                options=method_options,
                key="methods",
                placeholder="Selecciona uno o más métodos",
                format_func=translate_discovery_method,
            )

        min_planets = int(df["system_planet_count"].min())
        max_planets = int(df["system_planet_count"].max())

        planet_count_range = st.slider(
            "Planetas por sistema",
            min_value=min_planets,
            max_value=max_planets,
            value=(min_planets, max_planets),
        )

        st.divider()
        st.markdown("### Sistemas específicos")

        host_options = sorted(df["hostname"].dropna().unique().tolist())
        host_query = st.text_input(
            "Buscar estrella anfitriona",
            placeholder="Ej.: TRAPPIST, Kepler...",
        )

        matching_hosts = host_options
        if host_query:
            matching_hosts = [
                host for host in host_options
                if host_query.lower() in host.lower()
            ][:120]

        selected_hosts = st.multiselect(
            "Restringir a",
            options=matching_hosts,
            placeholder="Todos los sistemas",
        )

        st.divider()
        st.markdown("### Configuración del gráfico")

        x_axis = st.selectbox(
            "Eje X",
            options=list(labels.keys()),
            key="x_axis",
            format_func=lambda column: format_axis_label(column, labels),
        )

        log_x = st.toggle("Escala logarítmica (X)", key="log_x")

        y_axis = st.selectbox(
            "Eje Y",
            options=list(labels.keys()),
            key="y_axis",
            format_func=lambda column: format_axis_label(column, labels),
        )

        log_y = st.toggle("Escala logarítmica (Y)", key="log_y")

        color_mode = st.selectbox(
            "Color de los puntos",
            options=["none", "discoverymethod", *labels.keys()],
            key="color_mode",
            format_func=lambda value: (
                "Un solo color"
                if value == "none"
                else "Método de descubrimiento"
                if value == "discoverymethod"
                else format_axis_label(value, labels)
            ),
        )

        size_mode = st.radio(
            "Tamaño de los puntos",
            options=["fixed", "system"],
            key="size_mode",
            format_func=lambda value: (
                "Fijo"
                if value == "fixed"
                else "Según la cantidad de planetas del sistema"
            ),
        )

    return (
        methods,
        planet_count_range,
        selected_hosts,
        x_axis,
        log_x,
        y_axis,
        log_y,
        color_mode,
        size_mode,
    )


def render_visual_explorer(
    filtered: pd.DataFrame,
    labels: dict[str, str],
    *,
    x_axis: str,
    y_axis: str,
    color_mode: str,
    size_mode: str,
    log_x: bool,
    log_y: bool,
    theme_type: str,
) -> None:
    with st.container(border=True):
        st.subheader(
            f"Diagrama: {format_axis_label(y_axis, labels)} vs {format_axis_label(x_axis, labels)}"
        )

        st.caption(
            f"Mostrando **{len(filtered):,}** planetas en "
            f"**{filtered['hostname'].nunique():,}** sistemas estelares."
        )

        figure = build_scatter(
            filtered,
            x=x_axis,
            y=y_axis,
            color=color_mode,
            size_mode=size_mode,
            log_x=log_x,
            log_y=log_y,
            labels=labels,
            theme_type=theme_type,
        )

        figure.update_layout(
            xaxis_title=format_axis_label(x_axis, labels),
            yaxis_title=format_axis_label(y_axis, labels),
        )

        st.plotly_chart(figure, use_container_width=True, config=PLOTLY_CONFIG)


def render_top_systems(
    filtered: pd.DataFrame,
    labels: dict[str, str],
    theme_type: str,
) -> None:
    plot_style = PLOT_THEMES[theme_type]
    col1, col2 = st.columns([1.2, 1])

    with col1:
        with st.container(border=True):
            st.subheader("Sistemas multiplanetarios destacados")

            system_summary = (
                filtered.groupby("hostname")
                .agg(
                    planetas=("pl_name", "count"),
                    masa_estelar=("st_mass", "median"),
                    temp_estelar=("st_teff", "median"),
                    metodos=(
                        "discoverymethod",
                        lambda s: ", ".join(
                            sorted(
                                {
                                    translate_discovery_method(value)
                                    for value in s.dropna().astype(str)
                                }
                            )
                        ),
                    ),
                )
                .sort_values(["planetas", "hostname"], ascending=[False, True])
                .head(15)
                .reset_index()
            )

            system_summary_display = system_summary.rename(
                columns={
                    "hostname": "Estrella anfitriona",
                    "planetas": "Planetas",
                    "masa_estelar": "Masa estelar (M☉)",
                    "temp_estelar": "Temperatura estelar (K)",
                    "metodos": "Métodos de descubrimiento",
                }
            )

            st.dataframe(
                system_summary_display,
                use_container_width=True,
                hide_index=True,
            )

    with col2:
        with st.container(border=True):
            st.subheader("Integridad de parámetros")

            completeness = (
                filtered[list(labels.keys())]
                .notna()
                .sum()
                .sort_values(ascending=True)
                .rename("valores")
                .reset_index()
                .rename(columns={"index": "parámetro"})
            )

            completeness["parámetro"] = completeness["parámetro"].map(
                lambda column: format_axis_label(column, labels)
            )

            bar = px.bar(
                completeness,
                x="valores",
                y="parámetro",
                orientation="h",
                color="valores",
                labels={
                    "valores": "Registros disponibles",
                    "parámetro": "Parámetro",
                },
                color_continuous_scale=plot_style["continuous"],
                height=450,
            )

            bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=plot_style["text"], family="IBM Plex Sans, sans-serif"),
                autosize=True,
                margin=dict(l=10, r=20, t=10, b=20),
                coloraxis_showscale=False,
                yaxis_title="",
                xaxis_title="Registros disponibles",
                xaxis=dict(
                    gridcolor=plot_style["grid"],
                    tickfont=dict(color=plot_style["muted"]),
                    title_font=dict(color=plot_style["text"]),
                ),
                yaxis=dict(
                    tickfont=dict(color=plot_style["muted"]),
                ),
                hoverlabel=dict(
                    bgcolor=plot_style["legend_bg"],
                    bordercolor=plot_style["legend_border"],
                    font=dict(color=plot_style["text"]),
                ),
            )

            bar.update_traces(
                hovertemplate="Parámetro: %{y}<br>Registros disponibles: %{x}<extra></extra>"
            )

            st.plotly_chart(bar, use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
    st.subheader("Análisis de un sistema específico")

    if system_summary.empty:
        st.warning("No hay sistemas disponibles con los filtros actuales.")
        return

    selected_top_system = st.selectbox(
        "Selecciona un sistema para visualizar su arquitectura",
        options=system_summary["hostname"].tolist(),
        help="Elige una estrella para ver las métricas y la distribución de sus planetas.",
    )

    if not selected_top_system:
        return

    sys_df = (
        filtered[filtered["hostname"] == selected_top_system]
        .sort_values("pl_orbsmax", na_position="last")
        .copy()
    )

    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Planetas confirmados", len(sys_df))

        st_mass_val = sys_df["st_mass"].median()
        m2.metric(
            "Masa estelar (M☉)",
            f"{st_mass_val:.2f}" if pd.notna(st_mass_val) else "N/D",
        )

        st_teff_val = sys_df["st_teff"].median()
        m3.metric(
            "Temperatura estelar (K)",
            f"{st_teff_val:.0f}" if pd.notna(st_teff_val) else "N/D",
        )

        if "sy_snum" in sys_df.columns:
            stars = sys_df["sy_snum"].iloc[0]
            m4.metric(
                "Estrellas en el sistema",
                int(stars) if pd.notna(stars) else 1,
            )
        else:
            m4.metric(
                "Método principal",
                translate_discovery_method(safe_mode_value(sys_df["discoverymethod"])),
            )

        st.markdown(f"**Arquitectura orbital de {selected_top_system}**")

        x_col = "pl_orbper" if sys_df["pl_orbper"].notna().any() else "pl_orbsmax"
        y_col = "pl_bmasse" if sys_df["pl_bmasse"].notna().any() else "pl_rade"

        sys_df_plot = sys_df.dropna(subset=[x_col, y_col]).copy()
        sys_df_plot = sys_df_plot[(sys_df_plot[x_col] > 0) & (sys_df_plot[y_col] > 0)]

        if sys_df_plot.empty:
            st.warning("Este sistema no tiene datos positivos suficientes para graficar en escala logarítmica.")
        else:
            if sys_df_plot["pl_rade"].notna().any():
                sys_df_plot["marker_size"] = (
                    sys_df_plot["pl_rade"]
                    .fillna(sys_df_plot["pl_rade"].median())
                    .fillna(1.0)
                )
                size_col = "marker_size"
            else:
                size_col = None

            x_title = format_axis_label(x_col, labels)
            y_title = format_axis_label(y_col, labels)
            sys_df_plot["_metodo_es"] = sys_df_plot["discoverymethod"].map(
                translate_discovery_method
            )

            sys_fig = px.scatter(
                sys_df_plot,
                x=x_col,
                y=y_col,
                size=size_col,
                color="pl_name",
                text="pl_name",
                custom_data=["pl_name", "hostname", "_metodo_es"],
                labels={
                    x_col: x_title,
                    y_col: y_title,
                    "pl_name": "Exoplaneta",
                },
                log_x=True,
                log_y=True,
                color_discrete_sequence=plot_style["palette"],
                height=400,
            )

            sys_fig.update_traces(
                textposition="top center",
                marker=dict(
                    line=dict(width=0.9, color=plot_style["marker_border"])
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br><br>"
                    "Estrella anfitriona: %{customdata[1]}<br>"
                    "Método de descubrimiento: %{customdata[2]}<br>"
                    f"{x_title}: %{{x:.4g}}<br>"
                    f"{y_title}: %{{y:.4g}}"
                    "<extra></extra>"
                ),
            )

            sys_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=plot_style["text"], family="IBM Plex Sans, sans-serif"),
                autosize=True,
                showlegend=False,
                xaxis_title=x_title,
                yaxis_title=y_title,
                margin=dict(l=20, r=20, t=20, b=20),
                hoverlabel=dict(
                    bgcolor=plot_style["legend_bg"],
                    bordercolor=plot_style["legend_border"],
                    font=dict(color=plot_style["text"]),
                ),
            )

            sys_fig.update_xaxes(
                gridcolor=plot_style["grid"],
                zerolinecolor=plot_style["grid"],
                tickfont=dict(color=plot_style["muted"]),
            )

            sys_fig.update_yaxes(
                gridcolor=plot_style["grid"],
                zerolinecolor=plot_style["grid"],
                tickfont=dict(color=plot_style["muted"]),
            )

            st.plotly_chart(sys_fig, use_container_width=True, config=PLOTLY_CONFIG)

        visible_sys_columns = [
            "pl_name",
            "discoverymethod",
            "pl_orbsmax",
            "pl_orbper",
            "pl_bmasse",
            "pl_rade",
        ]

        visible_sys_columns = [
            column for column in visible_sys_columns
            if column in sys_df.columns
        ]

        sys_table = sys_df[visible_sys_columns].copy()
        if "discoverymethod" in sys_table.columns:
            sys_table["discoverymethod"] = sys_table["discoverymethod"].map(
                translate_discovery_method
            )
        sys_table = sys_table.rename(columns=TABLE_COLUMN_LABELS)

        st.dataframe(
            sys_table,
            use_container_width=True,
            hide_index=True,
        )


def render_csv_data(filtered: pd.DataFrame) -> None:
    with st.container(border=True):
        st.subheader("Catálogo filtrado")

        visible_columns = [
            "pl_name",
            "hostname",
            "discoverymethod",
            "pl_orbsmax",
            "pl_orbper",
            "pl_rade",
            "pl_bmasse",
            "pl_orbeccen",
            "st_mass",
            "st_teff",
        ]

        visible_columns = [
            column for column in visible_columns
            if column in filtered.columns
        ]

        catalog_display = filtered[visible_columns].copy()
        if "discoverymethod" in catalog_display.columns:
            catalog_display["discoverymethod"] = catalog_display["discoverymethod"].map(
                translate_discovery_method
            )
        catalog_display = catalog_display.rename(columns=TABLE_COLUMN_LABELS)

        st.dataframe(
            catalog_display,
            use_container_width=True,
            hide_index=True,
        )

        st.caption("Fuente: NASA Exoplanet Archive · actualización automática cada 24 horas.")


def initialize_session_state() -> None:
    if "preset" not in st.session_state:
        st.session_state["preset"] = "Masa vs semieje mayor"

    if "x_axis" not in st.session_state:
        set_preset_state(st.session_state["preset"])

    if "size_mode" not in st.session_state:
        st.session_state["size_mode"] = "fixed"


def validate_required_columns(df: pd.DataFrame) -> None:
    required_columns = [
        "pl_name",
        "hostname",
        "discoverymethod",
        "system_planet_count",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error(f"Faltan columnas requeridas en el catálogo: {missing_columns}")
        st.stop()


def main() -> None:
    theme_type = get_active_theme()
    apply_theme(theme_type)
    initialize_session_state()

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Atlas / Catálogo confirmado / NASA Exoplanet Archive</div>
            <h1>Atlas de Exoplanetas</h1>
            <p>
                Explorador interactivo del catálogo confirmado de exoplanetas. Aplica filtros físicos
                y orbitales para analizar semieje mayor, período, masa, radio y propiedades estelares
                en busca de patrones de arquitectura planetaria.
            </p>
            <div class="hero-meta">
                <span>Fuente <strong>NASA</strong></span>
                <span>Catálogo <strong>PS</strong></span>
                <span>Sincronización <strong>24 h</strong></span>
                <span>Vista <strong>interactiva</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = get_catalog()
    except Exception as error:
        st.error("No se pudo cargar el catálogo de exoplanetas.")
        st.exception(error)
        st.stop()

    validate_required_columns(df)

    labels = available_plot_columns(df)
    labels = {
        column: DEFAULT_COLUMN_LABELS.get(column, label)
        for column, label in labels.items()
    }

    if not labels:
        st.error("No hay columnas numéricas disponibles para graficar.")
        st.stop()

    render_overview(df)

    (
        methods,
        planet_count_range,
        selected_hosts,
        x_axis,
        log_x,
        y_axis,
        log_y,
        color_mode,
        size_mode,
    ) = render_sidebar(df, labels)

    filtered = filter_catalog(
        df,
        methods=methods,
        planet_count_range=planet_count_range,
        selected_hosts=selected_hosts,
    )

    if filtered.empty:
        st.warning("Los filtros actuales excluyen todos los datos del catálogo.")
        return

    tab1, tab2, tab3 = st.tabs(
        ["Exploración orbital", "Sistemas destacados", "Catálogo"]
    )

    with tab1:
        render_visual_explorer(
            filtered,
            labels,
            x_axis=x_axis,
            y_axis=y_axis,
            color_mode=color_mode,
            size_mode=size_mode,
            log_x=log_x,
            log_y=log_y,
            theme_type=theme_type,
        )

    with tab2:
        render_top_systems(filtered, labels, theme_type)

    with tab3:
        render_csv_data(filtered)


if __name__ == "__main__":
    main()