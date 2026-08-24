from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import streamlit as st

from explore_exoplanets import (
    available_plot_columns,
    load_catalog,
    read_metadata,
)

PLOTLY_CONFIG = {
    "responsive": True,
    "displaylogo": False,
    "scrollZoom": False,
}

# El Atlas renueva el catálogo una vez al día. La primera ejecución posterior
# a las 08:00 (hora de Chile) utiliza una nueva clave de caché y consulta NASA.
CATALOG_REFRESH_HOUR = 8
CATALOG_TIMEZONE = "America/Santiago"

THEME_TOKENS = {
    "dark": {
        "bg": "#071019",
        "bg_alt": "#0A1520",
        "surface": "#0E1B27",
        "surface_strong": "#142532",
        "surface_hover": "#1A3040",
        "text": "#F3F5F2",
        "text_soft": "#C7D2D6",
        "text_muted": "#82949E",
        "border": "#233947",
        "border_strong": "#395667",
        "accent": "#FFB258",
        "accent_soft": "#FFD39A",
        "accent_2": "#63DDD2",
        "danger": "#FF716B",
        "grid": "rgba(119, 167, 183, 0.075)",
        "shadow": "rgba(0, 0, 0, 0.38)",
    },
    "light": {
        "bg": "#F4F0E7",
        "bg_alt": "#EAE4D8",
        "surface": "#FCFAF5",
        "surface_strong": "#F1EBDF",
        "surface_hover": "#E6DED0",
        "text": "#17242B",
        "text_soft": "#40525B",
        "text_muted": "#6B7A80",
        "border": "#D2C8B9",
        "border_strong": "#9D9180",
        "accent": "#B64D25",
        "accent_soft": "#D36C3D",
        "accent_2": "#087A72",
        "danger": "#B43E39",
        "grid": "rgba(60, 85, 94, 0.075)",
        "shadow": "rgba(35, 43, 45, 0.13)",
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
    "Transit Timing Variations": "Variaciones en los tiempos de tránsito",
    "Eclipse Timing Variations": "Variaciones en los tiempos de eclipse",
    "Orbital Brightness Modulation": "Modulación del brillo orbital",
    "Astrometry": "Astrometría",
    "Pulsation Timing Variations": "Variaciones en los tiempos de pulsación",
    "Disk Kinematics": "Cinemática de disco",
}


APP_DIR = Path(__file__).resolve().parent
DETECTION_VIDEO_DIR = APP_DIR / "assets" / "metodos_deteccion"
CONCEPT_VIDEO_DIR = APP_DIR / "assets" / "conceptos"

MAIN_SECTIONS = [
    "Exploración orbital",
    "Sistemas destacados",
    "Catálogo",
    "Guía visual",
    "Métodos de detección",
]

CONCEPTS = [
    {
        "id": "exoplaneta",
        "title": "¿Qué es un exoplaneta?",
        "video": "Exoplanet.mp4",
        "group": "Fundamentos",
        "summary": (
            "Un exoplaneta es un mundo que orbita una estrella distinta del Sol. En el Atlas, "
            "cada planeta aparece vinculado a su estrella anfitriona y se describe mediante "
            "parámetros físicos y orbitales medidos —o inferidos— a partir de observaciones."
        ),
        "points": [
            "No pertenece al Sistema Solar.",
            "Puede detectarse de forma directa o, más comúnmente, por el efecto que produce sobre su estrella.",
            "No debe confundirse con un planeta errante, que no está ligado a una estrella anfitriona.",
        ],
    },
    {
        "id": "sistema-planetario",
        "title": "Sistema planetario",
        "video": "Sistema.mp4",
        "group": "Fundamentos",
        "summary": (
            "Un sistema planetario reúne una estrella anfitriona —o un sistema estelar— y los "
            "planetas que orbitan en torno a ella. Comparar sus planetas permite estudiar la "
            "arquitectura completa del sistema, no solo objetos aislados."
        ),
        "points": [
            "Un mismo sistema puede contener uno o varios exoplanetas confirmados.",
            "Los períodos y semiejes mayores ordenan la arquitectura orbital.",
            "Masa, radio y excentricidad ayudan a comparar la diversidad de sus planetas.",
        ],
    },
    {
        "id": "orbita",
        "title": "Órbita",
        "video": "Orbit.mp4",
        "group": "Fundamentos",
        "summary": (
            "La órbita es la trayectoria que describe un cuerpo bajo la acción gravitatoria. "
            "En sistemas planetarios puede ser casi circular o claramente elíptica; por eso "
            "un círculo perfecto es solo un caso particular."
        ),
        "points": [
            "La estrella se ubica en uno de los focos de una órbita elíptica idealizada.",
            "La forma se cuantifica mediante la excentricidad.",
            "El tamaño de la órbita se resume con el semieje mayor.",
        ],
    },
    {
        "id": "semieje-mayor",
        "title": "Semieje mayor (a)",
        "video": "Semieje.mp4",
        "group": "Parámetros orbitales",
        "summary": (
            "El semieje mayor es la mitad del eje más largo de una elipse y funciona como la "
            "escala característica de la órbita. En el Atlas se expresa normalmente en unidades astronómicas (UA)."
        ),
        "points": [
            "No es simplemente la distancia instantánea entre estrella y planeta.",
            "Para una órbita elíptica, a = (r_peri + r_apo) / 2.",
            "Un valor mayor suele corresponder a una órbita más extensa.",
        ],
    },
    {
        "id": "periodo-orbital",
        "title": "Período orbital (P)",
        "video": "Periodo.mp4",
        "group": "Parámetros orbitales",
        "summary": (
            "El período orbital es el tiempo que tarda el planeta en completar una vuelta alrededor "
            "de su estrella anfitriona. En el catálogo del Atlas se expresa en días."
        ),
        "points": [
            "Los períodos cortos corresponden a órbitas que se completan rápidamente.",
            "Está relacionado con el tamaño orbital mediante la dinámica kepleriana.",
            "Es uno de los parámetros que puede medirse con gran precisión en sistemas transitantes.",
        ],
    },
    {
        "id": "excentricidad",
        "title": "Excentricidad orbital (e)",
        "video": "Exc.mp4",
        "group": "Parámetros orbitales",
        "summary": (
            "La excentricidad mide cuánto se aparta una órbita de un círculo. Para una órbita "
            "planetaria ligada, e = 0 representa un círculo y 0 < e < 1 una elipse cada vez más alargada."
        ),
        "points": [
            "e = 0: órbita circular ideal.",
            "0 < e < 1: órbita elíptica.",
            "A mayor e, mayor diferencia entre las distancias de periastro y apoastro.",
        ],
    },
]

CONCEPT_BY_ID = {concept["id"]: concept for concept in CONCEPTS}
CONCEPT_BY_COLUMN = {
    "pl_orbsmax": "semieje-mayor",
    "pl_orbper": "periodo-orbital",
    "pl_orbeccen": "excentricidad",
}

DETECTION_METHODS = [
    {
        "title": "Tránsito",
        "archive_method": "Transit",
        "video": "Transito.mp4",
        "signal": "Disminución periódica del flujo estelar",
        "description": (
            "Cuando un exoplaneta pasa frente a su estrella desde nuestra línea de visión, "
            "bloquea una pequeña fracción de su luz. Si la caída de brillo se repite de forma "
            "periódica, el intervalo entre eventos permite determinar el período orbital y la profundidad "
            "del tránsito permite estimar el tamaño del exoplaneta en relación con su estrella."
        ),
        "examples": [
            "TRAPPIST-1 — sistema compacto de siete exoplanetas de tamaño terrestre detectados por tránsitos.",
            "Kepler-186 f — exoplaneta de tamaño terrestre descubierto mediante el método de tránsito.",
        ],
    },
    {
        "title": "Velocidad radial",
        "archive_method": "Radial Velocity",
        "video": "VelocidadRadial.mp4",
        "signal": "Desplazamiento Doppler de las líneas espectrales",
        "description": (
            "La estrella y el exoplaneta orbitan un centro de masa común. Ese pequeño movimiento "
            "hace que la estrella se acerque y se aleje periódicamente de nosotros, desplazando sus "
            "líneas espectrales por efecto Doppler. La amplitud y el período de la señal permiten "
            "estimar la órbita y la masa mínima del exoplaneta."
        ),
        "examples": [
            "51 Pegasi b — primer exoplaneta confirmado alrededor de una estrella similar al Sol mediante velocidad radial.",
            "Proxima Centauri b — exoplaneta alrededor de la estrella más cercana al Sol, detectado por velocidad radial.",
        ],
    },
    {
        "title": "Microlente gravitacional",
        "archive_method": "Microlensing",
        "video": "MicrolenteGravitacional.mp4",
        "signal": "Amplificación gravitacional temporal de una estrella de fondo",
        "description": (
            "Si una estrella pasa casi exactamente frente a otra más distante, su gravedad curva y "
            "amplifica la luz de la estrella de fondo. Un exoplaneta alrededor de la estrella que actúa "
            "como lente puede producir una anomalía breve adicional en esa amplificación. El método es "
            "especialmente sensible a mundos fríos y relativamente alejados de sus estrellas."
        ),
        "examples": [
            "OGLE-2005-BLG-390L b — mundo frío de pocas masas terrestres detectado mediante microlente gravitacional.",
        ],
    },
    {
        "title": "Imagen directa",
        "archive_method": "Imaging",
        "video": "ImagenDirecta.mp4",
        "signal": "Fotones del propio exoplaneta separados del resplandor estelar",
        "description": (
            "En lugar de inferir el exoplaneta a partir de cambios en su estrella, la imagen directa "
            "intenta registrar su propia luz. Como la estrella es muchísimo más brillante, se emplean "
            "coronógrafos y técnicas de alto contraste para suprimir el resplandor estelar. Funciona "
            "mejor con exoplanetas jóvenes, masivos y separados de su estrella."
        ),
        "examples": [
            "HR 8799 b, c, d y e — uno de los sistemas multiplanetarios de imagen directa más emblemáticos.",
            "β Pictoris b — gigante joven observado directamente alrededor de β Pictoris.",
        ],
    },
    {
        "title": "Astrometría",
        "archive_method": "Astrometry",
        "video": "Astrometria.mp4",
        "signal": "Pequeño desplazamiento de la posición de la estrella en el cielo",
        "description": (
            "La gravedad de un exoplaneta hace que su estrella describa un pequeño movimiento alrededor "
            "del centro de masa del sistema. La astrometría mide con gran precisión ese desplazamiento "
            "sobre el plano del cielo respecto de estrellas de referencia. Al recuperar la inclinación "
            "orbital, puede determinar la masa real del compañero y no solo una masa mínima."
        ),
        "examples": [
            "GJ 896 A b — planeta cuya señal astrométrica se midió alrededor de una de las componentes de un sistema binario.",
            "Gaia-4 b — exoplaneta confirmado a partir de una solución orbital astrométrica de Gaia y seguimiento espectroscópico.",
        ],
    },
    {
        "title": "Variaciones en los tiempos de tránsito",
        "archive_method": "Transit Timing Variations",
        "video": "VariacionesTiempoTransito.mp4",
        "signal": "Adelantos y retrasos respecto de una secuencia regular de tránsitos",
        "description": (
            "En un sistema con varios exoplanetas, las perturbaciones gravitacionales hacen que un tránsito "
            "pueda ocurrir ligeramente antes o después de lo esperado. Esas variaciones temporales, conocidas "
            "como TTV, permiten inferir la presencia y las masas de otros cuerpos, incluso cuando el exoplaneta "
            "perturbador no transita frente a la estrella."
        ),
        "examples": [
            "Kepler-19 c — compañero no transitante descubierto originalmente mediante las variaciones del tránsito de Kepler-19 b.",
            "Kepler-46 c — compañero detectado por el efecto que produce sobre los tiempos de tránsito de Kepler-46 b.",
        ],
    },
    {
        "title": "Variaciones en los tiempos de eclipse",
        "archive_method": "Eclipse Timing Variations",
        "video": "VariacionesTiempoEclipse.mp4",
        "signal": "Cambios en los tiempos de eclipse de una estrella binaria",
        "description": (
            "En una binaria eclipsante, los eclipses deberían repetirse con una cadencia muy precisa. Un "
            "compañero circumbinario puede desplazar el sistema alrededor de un centro de masa común y también "
            "perturbar dinámicamente las órbitas, haciendo que los eclipses lleguen antes o después de lo "
            "predicho. Es una técnica potente, aunque requiere descartar otras causas de variación temporal."
        ),
        "examples": [
            "DP Leo Ab — compañero circumbinario catalogado a partir de variaciones temporales de eclipse.",
        ],
    },
    {
        "title": "Cronometría de púlsares",
        "archive_method": "Pulsar Timing",
        "video": "TimingPulsar.mp4",
        "signal": "Cambios en el tiempo de llegada de pulsos extremadamente regulares",
        "description": (
            "Los púlsares emiten pulsos con una regularidad extraordinaria y pueden funcionar como relojes "
            "astronómicos. Si un exoplaneta los hace moverse alrededor de un centro de masa común, la distancia "
            "que recorre cada pulso hasta nosotros cambia ligeramente. Esos adelantos y retrasos permiten medir "
            "órbitas y masas con gran precisión."
        ),
        "examples": [
            "PSR B1257+12 c y d — integrantes del primer sistema de exoplanetas confirmado alrededor de un púlsar.",
            "PSR B1257+12 b — pequeño compañero del mismo sistema, también medido mediante cronometría de púlsares.",
        ],
    },
    {
        "title": "Cronometría de pulsaciones",
        "archive_method": "Pulsation Timing Variations",
        "video": "TimingPulsaciones.mp4",
        "signal": "Cambios de fase en pulsaciones estelares regulares",
        "description": (
            "Algunas estrellas variables pulsan con suficiente estabilidad como para actuar como relojes. "
            "Cuando un compañero planetario hace que la estrella se mueva, cambia ligeramente el tiempo de "
            "viaje de la luz y, por tanto, la fase observada de las pulsaciones. Una modulación periódica puede "
            "revelar la órbita del compañero."
        ),
        "examples": [
            "V391 Peg b — compañero catalogado mediante variaciones temporales de pulsación.",
            "KIC 7917485 b — compañero detectado mediante el mismo principio en datos de Kepler.",
        ],
    },
    {
        "title": "Modulación del brillo orbital",
        "archive_method": "Orbital Brightness Modulation",
        "video": "ModulacionBrilloOrbital.mp4",
        "signal": "Variación periódica del brillo total con la fase orbital",
        "description": (
            "El brillo combinado de una estrella y su exoplaneta puede cambiar durante la órbita incluso sin "
            "un tránsito. La señal puede contener luz reflejada o térmica del planeta, realce relativista por Doppler y pequeñas "
            "deformaciones gravitatorias de la estrella. Al repetirse con el período orbital, estas modulaciones "
            "permiten detectar o caracterizar compañeros cercanos."
        ),
        "examples": [
            "HAT-P-7 b — presenta una señal fotométrica orbital medible además de sus tránsitos y velocidad radial.",
            "KELT-9 b — gigante ultracaliente con modulación orbital registrada en su curva de fase.",
        ],
    },
    {
        "title": "Cinemática de disco",
        "archive_method": "Disk Kinematics",
        "video": "CinematicaDisco.mp4",
        "signal": "Desviaciones locales de la velocidad del gas respecto de la rotación kepleriana",
        "description": (
            "Un exoplaneta en formación puede perturbar el gas de su disco protoplanetario. Observaciones "
            "espectrales de alta resolución permiten reconstruir la velocidad del gas y buscar desviaciones "
            "locales respecto de una rotación aproximadamente kepleriana. Esas anomalías cinemáticas pueden "
            "delatar un planeta joven todavía inmerso en el disco."
        ),
        "examples": [
            "HD 97048 b — exoplaneta catalogado a partir de una perturbación cinemática en su disco protoplanetario.",
        ],
    },
]

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
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Manrope:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');

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

/* Navegación principal controlable desde los indicadores del resumen. */
[data-testid="stSegmentedControl"] {
    margin: 0.25rem 0 0.8rem;
}

[data-testid="stSegmentedControl"] button {
    border-radius: 0 !important;
    border-color: var(--atlas-border) !important;
    color: var(--atlas-text-soft) !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
    color: var(--atlas-text) !important;
    border-color: var(--atlas-accent) !important;
}

.atlas-metric-link {
    display: block;
    position: relative;
    min-height: 112px;
    padding: 1.15rem 1.2rem;
    background: var(--atlas-surface);
    border: 1px solid var(--atlas-border);
    border-radius: 6px;
    color: inherit !important;
    text-decoration: none !important;
    transition: transform 120ms ease, border-color 120ms ease;
}

.atlas-metric-link::before {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    width: 28px;
    height: 3px;
    background: var(--atlas-accent);
}

.atlas-metric-link:hover {
    border-color: var(--atlas-accent);
    transform: translate(-1px, -1px);
}

.atlas-metric-label {
    display: block;
    color: var(--atlas-text-muted);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    font-weight: 500;
    letter-spacing: 0.035em;
    text-transform: uppercase;
}

.atlas-metric-value {
    display: block;
    margin-top: 0.35rem;
    color: var(--atlas-text);
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.1;
}

.atlas-metric-action {
    display: block;
    margin-top: 0.55rem;
    color: var(--atlas-accent);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

[data-testid="stVideo"] video {
    width: 100% !important;
    border: 1px solid var(--atlas-border);
    border-radius: 6px;
    background: #000;
}

@media (max-width: 768px) {
    .atlas-metric-link {
        min-height: 94px;
        padding: 0.9rem;
    }

    .atlas-metric-value {
        font-size: 1.25rem;
    }
}

/* Guía visual: vocabulario científico integrado al flujo de exploración. */
.atlas-concept-header {
    margin: 0 0 0.45rem;
    color: var(--atlas-accent) !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.atlas-concept-copy {
    margin: 0;
    color: var(--atlas-text-soft) !important;
    line-height: 1.58;
}

.atlas-concept-video-note {
    margin-top: 0.35rem;
    color: var(--atlas-text-muted) !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
}

/* -------------------------------------------------------------------------
   Rediseño 2026 · cartografía celeste
   Una interfaz editorial y científica, con jerarquía clara y controles que
   se sienten parte de un instrumento de observación, no de un dashboard.
   ------------------------------------------------------------------------- */

html {
    scroll-behavior: smooth;
}

html, body, [class*="css"] {
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background-color: var(--atlas-bg);
    background-image:
        radial-gradient(circle at 82% 6%, color-mix(in srgb, var(--atlas-accent-2) 10%, transparent) 0, transparent 24rem),
        radial-gradient(circle at 18% 38%, color-mix(in srgb, var(--atlas-accent) 7%, transparent) 0, transparent 30rem),
        linear-gradient(var(--atlas-grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--atlas-grid) 1px, transparent 1px);
    background-size: auto, auto, 64px 64px, 64px 64px;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.48;
    background-image:
        radial-gradient(circle at 12% 18%, var(--atlas-text-muted) 0 1px, transparent 1.5px),
        radial-gradient(circle at 72% 34%, var(--atlas-text-muted) 0 1px, transparent 1.5px),
        radial-gradient(circle at 43% 78%, var(--atlas-text-muted) 0 1px, transparent 1.5px),
        radial-gradient(circle at 91% 83%, var(--atlas-text-muted) 0 1px, transparent 1.5px);
    background-size: 220px 220px, 310px 310px, 270px 270px, 360px 360px;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stSidebar"] {
    position: relative;
    z-index: 1;
}

[data-testid="stHeader"] {
    background: color-mix(in srgb, var(--atlas-bg) 78%, transparent) !important;
    border-bottom: 1px solid color-mix(in srgb, var(--atlas-border) 70%, transparent);
    backdrop-filter: blur(14px);
}

[data-testid="stToolbar"],
#MainMenu,
footer {
    visibility: hidden;
}

.block-container {
    max-width: 1480px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

h1, h2, h3, h4, h5, h6 {
    text-wrap: balance;
}

h1, h2 {
    font-family: 'Newsreader', Georgia, serif;
    font-weight: 600;
}

p, li {
    line-height: 1.65;
}

/* Hero editorial con una órbita construida íntegramente en CSS. */
.hero {
    isolation: isolate;
    display: grid;
    grid-template-columns: minmax(0, 1.35fr) minmax(260px, 0.65fr);
    align-items: center;
    min-height: 430px;
    margin-bottom: 1.35rem;
    padding: clamp(2rem, 5vw, 4.8rem);
    overflow: hidden;
    background:
        linear-gradient(112deg, color-mix(in srgb, var(--atlas-surface) 97%, transparent), color-mix(in srgb, var(--atlas-bg-alt) 91%, transparent));
    border: 1px solid var(--atlas-border-strong);
    border-radius: 2px 54px 2px 54px;
    box-shadow: 0 24px 70px -36px var(--atlas-shadow);
}

.hero::before {
    inset: auto -7rem -10rem auto;
    width: 30rem;
    height: 30rem;
    border: 1px solid color-mix(in srgb, var(--atlas-accent-2) 24%, transparent);
    border-radius: 50%;
    background: radial-gradient(circle, color-mix(in srgb, var(--atlas-accent-2) 9%, transparent), transparent 62%);
    opacity: 1;
}

.hero::after {
    top: 0;
    left: 0;
    width: 7rem;
    height: 5px;
    background: var(--atlas-accent);
    box-shadow: calc(100vw - 7rem) calc(430px - 5px) 0 var(--atlas-accent-2);
}

.hero-layout,
.hero-copy {
    position: relative;
    z-index: 2;
}

.hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.15rem;
    color: var(--atlas-accent) !important;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
}

.hero-kicker::before {
    content: '';
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--atlas-accent-2);
    box-shadow: 0 0 0 5px color-mix(in srgb, var(--atlas-accent-2) 12%, transparent);
}

.hero h1 {
    max-width: 760px;
    margin: 0 0 1.15rem;
    font-size: clamp(3rem, 6.3vw, 5.7rem);
    font-weight: 600;
    line-height: 0.88;
    letter-spacing: -0.055em;
}

.hero h1 span {
    display: block;
    color: var(--atlas-accent-soft);
    font-style: italic;
    font-weight: 500;
}

.hero p {
    max-width: 690px;
    font-size: clamp(0.98rem, 1.4vw, 1.12rem);
    line-height: 1.72;
}

.hero-meta {
    gap: 0.6rem;
    margin-top: 1.7rem;
    padding-top: 1.1rem;
}

.hero-meta span {
    padding: 0.38rem 0.58rem;
    border: 1px solid var(--atlas-border);
    border-radius: 999px;
    background: color-mix(in srgb, var(--atlas-surface-strong) 72%, transparent);
}

.hero-orbit {
    position: relative;
    z-index: 2;
    width: min(28vw, 330px);
    aspect-ratio: 1;
    justify-self: end;
}

.hero-orbit::before {
    content: '';
    position: absolute;
    inset: 43%;
    z-index: 3;
    border-radius: 50%;
    background: var(--atlas-accent);
    box-shadow:
        0 0 0 9px color-mix(in srgb, var(--atlas-accent) 12%, transparent),
        0 0 42px 8px color-mix(in srgb, var(--atlas-accent) 38%, transparent);
}

.orbit-ring {
    position: absolute;
    top: 50%;
    left: 50%;
    border: 1px solid color-mix(in srgb, var(--atlas-text-soft) 34%, transparent);
    border-radius: 50%;
    transform: translate(-50%, -50%) rotate(-24deg);
}

.orbit-ring:nth-child(1) {
    width: 96%;
    height: 36%;
}

.orbit-ring:nth-child(2) {
    width: 72%;
    height: 72%;
    border-color: color-mix(in srgb, var(--atlas-accent-2) 48%, transparent);
}

.orbit-ring:nth-child(3) {
    width: 44%;
    height: 90%;
    transform: translate(-50%, -50%) rotate(46deg);
}

.orbit-planet {
    position: absolute;
    z-index: 4;
    width: 15px;
    height: 15px;
    border: 3px solid var(--atlas-surface);
    border-radius: 50%;
    background: var(--atlas-accent-2);
    box-shadow: 0 0 22px color-mix(in srgb, var(--atlas-accent-2) 60%, transparent);
}

.orbit-planet.one { top: 27%; right: 8%; }
.orbit-planet.two { bottom: 8%; left: 29%; width: 10px; height: 10px; background: var(--atlas-accent-soft); }

.orbit-coordinates {
    position: absolute;
    right: 0;
    bottom: 0;
    color: var(--atlas-text-muted);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Resumen del catálogo: una sola banda de lectura, no cuatro tarjetas. */
.atlas-snapshot {
    margin: 0 0 1.45rem;
    border: 1px solid var(--atlas-border);
    border-radius: 18px 2px 18px 2px;
    background: color-mix(in srgb, var(--atlas-surface) 92%, transparent);
    box-shadow: 0 18px 55px -46px var(--atlas-shadow);
    overflow: hidden;
}

.atlas-snapshot-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--atlas-border);
    background: color-mix(in srgb, var(--atlas-surface-strong) 78%, transparent);
}

.atlas-snapshot-head span:first-child {
    color: var(--atlas-text);
    font-size: 0.84rem;
    font-weight: 700;
}

.atlas-snapshot-head span:last-child {
    color: var(--atlas-accent-2);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.atlas-stat-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
}

.atlas-stat {
    position: relative;
    min-height: 126px;
    padding: 1.25rem 1.2rem 1.1rem;
    border-right: 1px solid var(--atlas-border);
}

.atlas-stat:last-child {
    border-right: 0;
}

.atlas-stat-label {
    display: block;
    margin-bottom: 0.45rem;
    color: var(--atlas-text-muted);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}

.atlas-stat-value {
    display: block;
    color: var(--atlas-text);
    font-family: 'Newsreader', Georgia, serif;
    font-size: clamp(2rem, 3.5vw, 3rem);
    font-weight: 600;
    line-height: 1;
}

.atlas-stat-note {
    display: block;
    margin-top: 0.55rem;
    color: var(--atlas-text-muted);
    font-size: 0.7rem;
}

a.atlas-stat {
    color: inherit !important;
    text-decoration: none !important;
    transition: background-color 160ms ease;
}

a.atlas-stat:hover {
    background: var(--atlas-surface-hover);
}

a.atlas-stat .atlas-stat-note {
    color: var(--atlas-accent);
}

/* Encabezados de sección reutilizables. */
.atlas-section-heading {
    display: grid;
    grid-template-columns: minmax(130px, 0.28fr) minmax(0, 1fr);
    gap: clamp(1rem, 3vw, 2.5rem);
    align-items: start;
    margin: 1.8rem 0 1.2rem;
    padding-top: 1.2rem;
    border-top: 1px solid var(--atlas-border);
}

.atlas-section-index {
    color: var(--atlas-accent);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.11em;
    text-transform: uppercase;
}

.atlas-section-heading h2 {
    margin: -0.15rem 0 0.3rem;
    font-size: clamp(1.85rem, 4vw, 3rem);
    line-height: 1;
    letter-spacing: -0.035em;
}

.atlas-section-heading p {
    max-width: 780px;
    margin: 0;
    color: var(--atlas-text-muted) !important;
    font-size: 0.92rem;
}

.atlas-module-label {
    margin: 0 0 0.35rem;
    color: var(--atlas-accent) !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.67rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Navegación principal. */
[data-testid="stSegmentedControl"] {
    position: sticky;
    top: 3.2rem;
    z-index: 20;
    margin: 0 0 0.9rem;
    padding: 0.38rem;
    border: 1px solid var(--atlas-border);
    border-radius: 14px;
    background: color-mix(in srgb, var(--atlas-bg-alt) 86%, transparent);
    box-shadow: 0 12px 32px -26px var(--atlas-shadow);
    backdrop-filter: blur(16px);
}

[data-testid="stSegmentedControl"] button {
    min-height: 42px;
    border: 0 !important;
    border-radius: 9px !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 650 !important;
    letter-spacing: 0 !important;
    text-transform: none;
}

[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
    background: var(--atlas-surface-strong) !important;
    box-shadow: inset 0 0 0 1px var(--atlas-border-strong);
}

/* Módulos y controles. */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--atlas-border) !important;
    border-radius: 16px 3px 16px 3px;
    background: color-mix(in srgb, var(--atlas-surface) 94%, transparent);
    box-shadow: 0 20px 48px -44px var(--atlas-shadow);
}

[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPlotlyChart"]) {
    overflow: hidden;
}

[data-baseweb="select"] > div,
[data-baseweb="base-input"],
[data-testid="stTextInput"] input {
    min-height: 43px;
    border-color: var(--atlas-border-strong) !important;
    border-radius: 8px !important;
    background: var(--atlas-surface-strong) !important;
    color: var(--atlas-text) !important;
}

[data-baseweb="select"] > div:focus-within,
[data-baseweb="base-input"]:focus-within,
[data-testid="stTextInput"] input:focus {
    border-color: var(--atlas-accent-2) !important;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--atlas-accent-2) 12%, transparent) !important;
}

/* Streamlit coloca la etiqueta después del input; se evita teñir el texto. */
[data-testid="stCheckbox"] input:checked + div {
    background: transparent !important;
}

[data-testid="stCheckbox"] label:has(input:checked) > div:first-child {
    background: var(--atlas-accent-2) !important;
}

[data-baseweb="slider"] > div > div > div:last-child {
    background: color-mix(in srgb, var(--atlas-accent-2) 78%, var(--atlas-surface-strong)) !important;
}

.stButton > button,
.stDownloadButton > button {
    min-height: 43px;
    border-radius: 8px 2px 8px 2px !important;
    box-shadow: none;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px -16px var(--atlas-shadow);
}

.stDownloadButton > button {
    border-color: var(--atlas-accent) !important;
    background: var(--atlas-accent) !important;
}

.stDownloadButton > button p {
    color: var(--atlas-bg) !important;
}

[data-testid="stExpander"] {
    border-color: var(--atlas-border) !important;
    border-radius: 12px 2px 12px 2px !important;
    background: color-mix(in srgb, var(--atlas-surface) 90%, transparent);
}

[data-testid="stAlert"] {
    border-radius: 10px 2px 10px 2px;
}

[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--atlas-border);
    border-radius: 10px 2px 10px 2px;
}

[data-testid="stPlotlyChart"] {
    border-radius: 10px;
}

[data-baseweb="tab-list"] {
    padding: 0.28rem;
    border: 1px solid var(--atlas-border);
    border-radius: 10px;
    background: var(--atlas-bg-alt);
}

[data-baseweb="tab"] {
    border: 0 !important;
    border-radius: 7px !important;
}

[data-baseweb="tab"][aria-selected="true"] {
    background: var(--atlas-surface-strong) !important;
}

[data-baseweb="tab-highlight"] {
    display: none;
}

/* Panel lateral: índice y mesa de control. */
[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, color-mix(in srgb, var(--atlas-bg-alt) 96%, transparent), color-mix(in srgb, var(--atlas-surface) 88%, transparent)) !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 1.25rem;
}

.sidebar-brand {
    margin: 0.15rem 0 1.1rem;
    padding: 0.2rem 0.1rem 1rem;
    border-bottom: 1px solid var(--atlas-border);
}

.sidebar-brand span {
    display: block;
    color: var(--atlas-accent) !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.sidebar-brand strong {
    display: block;
    margin-top: 0.35rem;
    color: var(--atlas-text);
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.45rem;
    font-weight: 600;
}

[data-testid="stSidebar"] h3 {
    margin-top: 0.85rem;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
}

[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-size: 0.78rem;
    font-weight: 650;
}

[data-testid="stVideo"] video {
    border-radius: 12px 2px 12px 2px;
    box-shadow: 0 18px 44px -35px var(--atlas-shadow);
}

/* Accesibilidad y movimiento. */
:where(button, a, input, [role="slider"]):focus-visible {
    outline: 2px solid var(--atlas-accent-2) !important;
    outline-offset: 3px;
}

@media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
    }
}

@media (max-width: 980px) {
    .hero {
        grid-template-columns: minmax(0, 1fr) 220px;
        min-height: 390px;
        padding: 2.4rem;
    }

    .hero-orbit { width: 220px; }
    .atlas-stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .atlas-stat:nth-child(2) { border-right: 0; }
    .atlas-stat:nth-child(-n+2) { border-bottom: 1px solid var(--atlas-border); }
}

@media (max-width: 700px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    .hero {
        display: block;
        min-height: auto;
        padding: 2rem 1.25rem 1.6rem;
        border-radius: 2px 28px 2px 28px;
    }

    .hero::after {
        width: 5rem;
        box-shadow: none;
    }

    .hero h1 { font-size: clamp(2.75rem, 15vw, 4.2rem); }
    .hero-orbit { display: none; }
    .hero-meta span { font-size: 0.59rem; }

    .atlas-snapshot-head {
        align-items: flex-start;
        flex-direction: column;
        gap: 0.2rem;
    }

    .atlas-stat-grid { grid-template-columns: 1fr 1fr; }
    .atlas-stat { min-height: 112px; padding: 1rem 0.85rem; }
    .atlas-stat-value { font-size: 2rem; }
    .atlas-stat-label { font-size: 0.58rem; }

    .atlas-section-heading {
        display: block;
        margin-top: 1.2rem;
    }

    .atlas-section-index { display: block; margin-bottom: 0.7rem; }

    [data-testid="stSegmentedControl"] {
        position: relative;
        top: auto;
        overflow-x: auto;
    }

    [data-testid="stSegmentedControl"] > div {
        min-width: max-content;
    }
}

@media (max-width: 420px) {
    .atlas-stat-grid { grid-template-columns: 1fr; }
    .atlas-stat,
    .atlas-stat:nth-child(2) { border-right: 0; border-bottom: 1px solid var(--atlas-border); }
    .atlas-stat:last-child { border-bottom: 0; }
}
"""


PRESETS = {
    "Masa según el semieje mayor": {
        "x": "pl_orbsmax",
        "y": "pl_bmasse",
        "color": "discoverymethod",
        "log_x": True,
        "log_y": True,
    },
    "Radio según el semieje mayor": {
        "x": "pl_orbsmax",
        "y": "pl_rade",
        "color": "discoverymethod",
        "log_x": True,
        "log_y": True,
    },
    "Semieje mayor según el período": {
        "x": "pl_orbper",
        "y": "pl_orbsmax",
        "color": "pl_orbeccen",
        "log_x": True,
        "log_y": True,
    },
    "Radio según la temperatura estelar": {
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


def get_catalog_refresh_key() -> str:
    """Devuelve la ventana diaria de actualización iniciada a las 08:00 en Chile."""
    now = datetime.now(ZoneInfo(CATALOG_TIMEZONE))
    refresh_point = now.replace(
        hour=CATALOG_REFRESH_HOUR,
        minute=0,
        second=0,
        microsecond=0,
    )
    if now < refresh_point:
        refresh_point -= timedelta(days=1)
    return refresh_point.strftime("%Y-%m-%dT08:00")


@st.cache_data(show_spinner=False)
def get_catalog(refresh_key: str) -> pd.DataFrame:
    """
    Obtiene el catálogo desde NASA Exoplanet Archive una vez por ventana diaria.

    `refresh_key` cambia cada día a las 08:00 (hora de Chile). Si el archivo
    local ya fue descargado dentro de la ventana actual, se reutiliza incluso
    después de reiniciar la app. Si NASA no está disponible, `load_catalog`
    conserva su mecanismo de respaldo local.
    """
    should_download = True
    metadata = read_metadata()
    downloaded_at_raw = metadata.get("downloaded_at_utc")

    if downloaded_at_raw:
        try:
            downloaded_at = datetime.fromisoformat(str(downloaded_at_raw))
            refresh_start = datetime.strptime(
                refresh_key,
                "%Y-%m-%dT%H:%M",
            ).replace(tzinfo=ZoneInfo(CATALOG_TIMEZONE))
            should_download = downloaded_at < refresh_start
        except (TypeError, ValueError):
            should_download = True

    return load_catalog(force_download=should_download)


def format_axis_label(column: str, labels: dict[str, str]) -> str:
    return DEFAULT_COLUMN_LABELS.get(column, labels.get(column, column))


def format_count(value: int) -> str:
    """Formatea enteros con separador de miles habitual en español."""
    return f"{value:,}".replace(",", ".")


def render_section_heading(
    index: str,
    title: str,
    description: str,
    *,
    anchor: str | None = None,
) -> None:
    """Crea una entrada de sección consistente y fácil de recorrer."""
    anchor_markup = f'<span id="{anchor}"></span>' if anchor else ""
    st.markdown(
        f"""
        {anchor_markup}
        <header class="atlas-section-heading">
            <span class="atlas-section-index">{index}</span>
            <div>
                <h2>{title}</h2>
                <p>{description}</p>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


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
            title="Esta combinación de ejes y filtros no contiene valores representables.",
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
    method_count = df["discoverymethod"].nunique()

    st.markdown(
        f"""
        <section class="atlas-snapshot" aria-label="Resumen del catálogo">
            <div class="atlas-snapshot-head">
                <span>El universo conocido, en cifras</span>
                <span>Catálogo confirmado · disponible</span>
            </div>
            <div class="atlas-stat-grid">
                <div class="atlas-stat">
                    <span class="atlas-stat-label">Exoplanetas confirmados</span>
                    <strong class="atlas-stat-value">{format_count(len(df))}</strong>
                    <span class="atlas-stat-note">Mundos con registro activo</span>
                </div>
                <div class="atlas-stat">
                    <span class="atlas-stat-label">Sistemas estelares</span>
                    <strong class="atlas-stat-value">{format_count(total_systems)}</strong>
                    <span class="atlas-stat-note">Estrellas anfitrionas únicas</span>
                </div>
                <div class="atlas-stat">
                    <span class="atlas-stat-label">Sistemas múltiples</span>
                    <strong class="atlas-stat-value">{format_count(multi_systems)}</strong>
                    <span class="atlas-stat-note">Con más de un planeta</span>
                </div>
                <a class="atlas-stat" href="?section=metodos-deteccion#metodos-deteccion" target="_self">
                    <span class="atlas-stat-label">Métodos de detección</span>
                    <strong class="atlas-stat-value">{method_count}</strong>
                    <span class="atlas-stat-note">Conocer las técnicas →</span>
                </a>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def apply_section_query_parameter() -> None:
    """Permite abrir secciones concretas desde enlaces internos de la app."""
    try:
        requested = st.query_params.get("section")
    except Exception:
        requested = None

    section_map = {
        "metodos-deteccion": "Métodos de detección",
        "guia-visual": "Guía visual",
    }

    if requested in section_map:
        st.session_state["main_section"] = section_map[requested]
        try:
            st.query_params.clear()
        except Exception:
            pass


def render_main_navigation() -> str:
    """Navegación horizontal equivalente a pestañas, pero controlable por estado."""
    if hasattr(st, "segmented_control"):
        selected = st.segmented_control(
            "Sección principal",
            options=MAIN_SECTIONS,
            key="main_section",
            label_visibility="collapsed",
        )
        return selected or st.session_state.get("main_section", MAIN_SECTIONS[0])

    return st.radio(
        "Sección principal",
        options=MAIN_SECTIONS,
        key="main_section",
        horizontal=True,
        label_visibility="collapsed",
    )


def render_detection_methods(df: pd.DataFrame) -> None:
    render_section_heading(
        "05 · Cómo los encontramos",
        "Métodos de detección",
        "Un exoplaneta casi nunca se ve a simple vista. Estas animaciones conectan cada "
        "fenómeno físico con la señal que los astrónomos observan y miden.",
        anchor="metodos-deteccion",
    )

    method_titles = [method["title"] for method in DETECTION_METHODS]
    selected_method = st.selectbox(
        "Técnica que quieres explorar",
        options=["Todos", *method_titles],
        key="detection_method_view",
        help="Elige una técnica concreta o recorre las once disponibles.",
    )

    visible_methods = (
        DETECTION_METHODS
        if selected_method == "Todos"
        else [method for method in DETECTION_METHODS if method["title"] == selected_method]
    )

    for method in visible_methods:
        with st.container(border=True):
            video_col, info_col = st.columns([1.05, 1.25], vertical_alignment="center")

            with video_col:
                video_path = DETECTION_VIDEO_DIR / method["video"]
                if video_path.exists():
                    st.video(str(video_path), autoplay=False, loop=True, muted=True)
                else:
                    st.warning(
                        f"No se encontró el video `{method['video']}`. "
                        "Comprueba la carpeta `assets/metodos_deteccion`."
                    )

            with info_col:
                st.markdown(f"### {method['title']}")
                st.caption(f"Qué se observa · {method['signal']}")
                st.write(method["description"])

                count = int((df["discoverymethod"] == method["archive_method"]).sum())
                count_display = format_count(count)
                planet_label = (
                    "exoplaneta descubierto"
                    if count == 1
                    else "exoplanetas descubiertos"
                )
                st.caption(
                    f"En el catálogo actual hay {count_display} {planet_label} mediante "
                    f"**{translate_discovery_method(method['archive_method'])}**."
                )

                st.markdown("**Ejemplos destacados**")
                for example in method["examples"]:
                    st.markdown(f"- {example}")



def render_concept(concept: dict[str, object], *, compact: bool = False) -> None:
    """Renderiza una cápsula conceptual con video y explicación breve."""
    video_path = CONCEPT_VIDEO_DIR / str(concept["video"])

    if compact:
        video_col, info_col = st.columns([1.0, 1.15], vertical_alignment="center")
    else:
        video_col, info_col = st.columns([1.05, 1.25], vertical_alignment="center")

    with video_col:
        if video_path.exists():
            st.video(str(video_path), autoplay=False, loop=True, muted=True)
        else:
            st.info(
                f"Animación pendiente: `{concept['video']}`. "
                "Renderiza el script Manim correspondiente y copia el MP4 a `assets/conceptos`."
            )

    with info_col:
        st.markdown(
            f'<p class="atlas-concept-header">{concept["group"]}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(f"### {concept['title']}")
        st.write(concept["summary"])
        for point in concept["points"]:
            st.markdown(f"- {point}")


def render_visual_guide() -> None:
    """Sección principal para aprender los conceptos que aparecen en el Atlas."""
    render_section_heading(
        "04 · Antes de comparar",
        "Guía visual de conceptos",
        "Una introducción breve al vocabulario del Atlas. Consulta una idea, mira cómo "
        "funciona y vuelve al catálogo con una lectura más clara.",
        anchor="guia-visual",
    )

    group = st.segmented_control(
        "Tipo de concepto",
        options=["Fundamentos", "Parámetros orbitales"],
        default="Fundamentos",
        key="visual_guide_group",
        label_visibility="collapsed",
    ) if hasattr(st, "segmented_control") else st.radio(
        "Tipo de concepto",
        options=["Fundamentos", "Parámetros orbitales"],
        horizontal=True,
        key="visual_guide_group",
        label_visibility="collapsed",
    )

    visible = [concept for concept in CONCEPTS if concept["group"] == group]
    guide_key = (
        "visual_guide_concept_fundamentos"
        if group == "Fundamentos"
        else "visual_guide_concept_parametros"
    )
    selected_title = st.selectbox(
        "Concepto",
        options=[concept["title"] for concept in visible],
        key=guide_key,
        help="Selecciona un concepto para ver su animación y una explicación breve.",
    )

    concept = next(concept for concept in visible if concept["title"] == selected_title)
    with st.container(border=True):
        render_concept(concept)

    st.caption(
        "En Exploración orbital también encontrarás una guía contextual con los conceptos "
        "relacionados con los ejes que tengas activos."
    )


def render_contextual_orbital_guide(x_axis: str, y_axis: str) -> None:
    """Muestra solo los conceptos que ayudan a interpretar los ejes activos."""
    concept_ids = ["orbita"]
    for column in (x_axis, y_axis):
        concept_id = CONCEPT_BY_COLUMN.get(column)
        if concept_id and concept_id not in concept_ids:
            concept_ids.append(concept_id)

    concepts = [CONCEPT_BY_ID[concept_id] for concept_id in concept_ids]

    with st.expander("Guía visual · entender los parámetros de este gráfico", expanded=False):
        selected_title = st.selectbox(
            "Concepto relacionado",
            options=[concept["title"] for concept in concepts],
            key=f"context_concept_{x_axis}_{y_axis}",
            label_visibility="collapsed",
        )
        concept = next(concept for concept in concepts if concept["title"] == selected_title)
        render_concept(concept, compact=True)


def render_system_concept_guide() -> None:
    """Ayuda conceptual breve para la sección de sistemas destacados."""
    concepts = [CONCEPT_BY_ID["sistema-planetario"], CONCEPT_BY_ID["exoplaneta"]]
    with st.expander("Guía visual · sistema planetario y exoplaneta", expanded=False):
        selected_title = st.selectbox(
            "Concepto de sistema",
            options=[concept["title"] for concept in concepts],
            key="system_concept_guide",
            label_visibility="collapsed",
        )
        concept = next(concept for concept in concepts if concept["title"] == selected_title)
        render_concept(concept, compact=True)


def render_sidebar(df: pd.DataFrame, labels: dict[str, str]) -> tuple[list[str], tuple[int, int], list[str], str, bool, str, bool, str, str]:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <span>Mesa de observación</span>
                <strong>Configura tu mapa</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            "↺ Restablecer exploración",
            key="atlas_home_reset_sidebar",
            width="stretch",
            help="Volver al inicio y restaurar filtros, búsquedas y controles.",
            on_click=reset_atlas_state,
        )
        st.markdown("### Punto de partida")

        st.selectbox(
            "Relación sugerida",
            options=list(PRESETS.keys()),
            key="preset",
            on_change=lambda: set_preset_state(st.session_state["preset"]),
            help="Carga una combinación de ejes, color y escala lista para explorar.",
        )

        st.divider()
        st.markdown("### Filtros del catálogo")

        method_options = sorted(df["discoverymethod"].dropna().unique().tolist())

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
            st.caption(f"Se incluyen automáticamente los {len(method_options)} métodos disponibles.")
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
            key="planet_count_range",
        )

        st.divider()
        st.markdown("### Sistemas específicos")

        host_options = sorted(df["hostname"].dropna().unique().tolist())
        host_query = st.text_input(
            "Buscar estrella anfitriona",
            placeholder="Ej.: TRAPPIST, Kepler...",
            key="host_query",
        )

        matching_hosts = host_options
        if host_query:
            matching_hosts = [
                host for host in host_options
                if host_query.lower() in host.lower()
            ][:120]

        selected_hosts = st.multiselect(
            "Mostrar solo estos sistemas",
            options=matching_hosts,
            placeholder="Todos los sistemas",
            key="selected_hosts",
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
            "Representar con el color",
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
            "Representar con el tamaño",
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
    render_section_heading(
        "01 · Mapa comparativo",
        "Exploración orbital",
        "Compara propiedades planetarias y estelares. Ajusta los filtros en la mesa de "
        "observación y pasa el cursor por cada punto para conocer el mundo que representa.",
    )

    with st.container(border=True):
        st.markdown(
            '<p class="atlas-module-label">Visualización activa</p>',
            unsafe_allow_html=True,
        )
        st.subheader(
            f"{format_axis_label(y_axis, labels)} según {format_axis_label(x_axis, labels)}"
        )

        st.caption(
            f"La vista contiene **{format_count(len(filtered))} planetas** de "
            f"**{format_count(filtered['hostname'].nunique())} sistemas estelares**."
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

        st.plotly_chart(figure, width="stretch", config=PLOTLY_CONFIG)

    render_contextual_orbital_guide(x_axis, y_axis)


def render_top_systems(
    filtered: pd.DataFrame,
    labels: dict[str, str],
    theme_type: str,
) -> None:
    plot_style = PLOT_THEMES[theme_type]
    render_section_heading(
        "02 · Arquitecturas planetarias",
        "Sistemas destacados",
        "Observa qué estrellas reúnen más mundos, qué parámetros cuentan con mejores "
        "mediciones y cómo se distribuyen los planetas dentro de un sistema concreto.",
    )
    col1, col2 = st.columns([1.2, 1])

    with col1:
        with st.container(border=True):
            st.markdown(
                '<p class="atlas-module-label">Clasificación</p>',
                unsafe_allow_html=True,
            )
            st.subheader("Sistemas con más planetas")

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
                width="stretch",
                hide_index=True,
            )

    with col2:
        with st.container(border=True):
            st.markdown(
                '<p class="atlas-module-label">Calidad del catálogo</p>',
                unsafe_allow_html=True,
            )
            st.subheader("Cobertura de los parámetros")

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

            st.plotly_chart(bar, width="stretch", config=PLOTLY_CONFIG)

    st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<p class="atlas-module-label">Vista detallada</p>',
        unsafe_allow_html=True,
    )
    st.subheader("Explora un sistema concreto")
    render_system_concept_guide()

    if system_summary.empty:
        st.warning(
            "No hay sistemas disponibles con los filtros actuales. Amplía la selección "
            "desde la mesa de observación para recuperar esta vista."
        )
        return

    selected_top_system = st.selectbox(
        "Sistema que quieres observar",
        options=system_summary["hostname"].tolist(),
        help="Elige una estrella para ver las métricas y la distribución de sus planetas.",
        key="selected_top_system",
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
        m1.metric("Exoplanetas confirmados", len(sys_df))

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
            st.warning(
                "Este sistema no reúne suficientes valores positivos para construir "
                "el gráfico en escala logarítmica. La tabla inferior sigue disponible."
            )
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

            st.plotly_chart(sys_fig, width="stretch", config=PLOTLY_CONFIG)

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
            width="stretch",
            hide_index=True,
        )


def render_csv_data(filtered: pd.DataFrame) -> None:
    render_section_heading(
        "03 · Registro completo",
        "Catálogo de exoplanetas",
        "Revisa los registros que cumplen tus filtros. Puedes ordenar las columnas, ampliar "
        "la tabla o descargar exactamente la selección que estás viendo.",
    )

    with st.container(border=True):
        st.markdown(
            '<p class="atlas-module-label">Datos seleccionados</p>',
            unsafe_allow_html=True,
        )
        st.subheader(f"{format_count(len(filtered))} exoplanetas en esta vista")

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
            width="stretch",
            hide_index=True,
        )

        csv_bytes = catalog_display.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Descargar selección en CSV",
            data=csv_bytes,
            file_name="atlas_exoplanetas_filtrado.csv",
            mime="text/csv",
            width="stretch",
            help="Descarga las filas visibles y conserva los encabezados en español.",
        )

        st.caption(
            "Fuente: NASA Exoplanet Archive · el catálogo se actualiza cada día "
            "a partir de las 08:00 (hora de Chile)."
        )


def reset_atlas_state() -> None:
    """Restaura navegación, filtros y controles al estado inicial del Atlas."""
    keys_to_reset = [
        "preset",
        "x_axis",
        "y_axis",
        "color_mode",
        "log_x",
        "log_y",
        "size_mode",
        "show_all_methods",
        "methods",
        "planet_count_range",
        "host_query",
        "selected_hosts",
        "selected_top_system",
        "detection_method_view",
        "visual_guide_group",
        "visual_guide_concept_fundamentos",
        "visual_guide_concept_parametros",
        "system_concept_guide",
        "main_section",
    ]
    for key in keys_to_reset:
        st.session_state.pop(key, None)

    # Los selectores contextuales usan una clave que depende de los ejes activos.
    for key in list(st.session_state.keys()):
        if str(key).startswith("context_concept_"):
            st.session_state.pop(key, None)

    try:
        st.query_params.clear()
    except Exception:
        pass


def initialize_session_state() -> None:
    if "preset" not in st.session_state:
        st.session_state["preset"] = "Masa según el semieje mayor"

    if "x_axis" not in st.session_state:
        set_preset_state(st.session_state["preset"])

    if "size_mode" not in st.session_state:
        st.session_state["size_mode"] = "fixed"

    if "main_section" not in st.session_state:
        st.session_state["main_section"] = MAIN_SECTIONS[0]


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
        st.error(
            "El catálogo se cargó, pero le faltan campos indispensables para construir "
            "la experiencia. Revisa el detalle técnico antes de volver a intentarlo."
        )
        st.code(", ".join(missing_columns), language=None)
        st.stop()


def main() -> None:
    theme_type = get_active_theme()
    apply_theme(theme_type)
    initialize_session_state()
    apply_section_query_parameter()

    st.markdown(
        """
        <section class="hero">
            <div class="hero-copy">
                <div class="hero-kicker">Cartografía celeste · NASA Exoplanet Archive</div>
                <h1>Atlas de <span>Exoplanetas</span></h1>
                <p>
                    Explora miles de mundos más allá del Sistema Solar. Compara sus órbitas,
                    tamaños y masas; descubre cómo se organizan sus sistemas y qué señales
                    permitieron encontrarlos.
                </p>
                <div class="hero-meta">
                    <span>Fuente <strong>NASA</strong></span>
                    <span>Catálogo <strong>PS</strong></span>
                    <span>Actualización <strong>diaria · 08:00</strong></span>
                    <span>Datos <strong>confirmados</strong></span>
                </div>
            </div>
            <div class="hero-orbit" aria-hidden="true">
                <span class="orbit-ring"></span>
                <span class="orbit-ring"></span>
                <span class="orbit-ring"></span>
                <span class="orbit-planet one"></span>
                <span class="orbit-planet two"></span>
                <span class="orbit-coordinates">RA 17h 45m · DEC −29°</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = get_catalog(get_catalog_refresh_key())
    except Exception as error:
        st.error(
            "No pudimos cargar el catálogo en este momento. Comprueba la conexión o "
            "vuelve a intentarlo en unos minutos."
        )
        with st.expander("Ver detalle técnico"):
            st.exception(error)
        st.stop()

    validate_required_columns(df)

    labels = available_plot_columns(df)
    labels = {
        column: DEFAULT_COLUMN_LABELS.get(column, label)
        for column, label in labels.items()
    }

    if not labels:
        st.error(
            "El catálogo no contiene parámetros numéricos disponibles para construir los gráficos."
        )
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

    section = render_main_navigation()

    if section == "Métodos de detección":
        render_detection_methods(df)
        return

    if section == "Guía visual":
        render_visual_guide()
        return

    if filtered.empty:
        st.warning(
            "No encontramos exoplanetas que coincidan con esta combinación de filtros. "
            "Prueba ampliando el rango de planetas o incluyendo más métodos de detección."
        )
        return

    if section == "Exploración orbital":
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
    elif section == "Sistemas destacados":
        render_top_systems(filtered, labels, theme_type)
    else:
        render_csv_data(filtered)


if __name__ == "__main__":
    main()
