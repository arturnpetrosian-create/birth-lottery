"""
streamlit_app.py
в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
В«Р›РѕС‚РµСЂРµСЏ СЂРѕР¶РґРµРЅРёСЏВ» вЂ” РґРµРјРѕРіСЂР°С„РёС‡РµСЃРєРёР№ Р°С‚Р»Р°СЃ РєРѕРіРѕСЂС‚ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РїРѕ СЃС‚СЂР°РЅР°Рј,
1950вЂ“2024.

РСЃС‚РѕС‡РЅРёРє:
    United Nations, Department of Economic and Social Affairs,
    Population Division (2024). World Population Prospects 2024.
    Р›РёС†РµРЅР·РёСЏ CC BY 3.0 IGO.

Р—Р°РїСѓСЃРє Р»РѕРєР°Р»СЊРЅРѕ:
    streamlit run app/streamlit_app.py

Р”РµРїР»РѕР№:
    Streamlit Community Cloud в†’ main file path: app/streamlit_app.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================================
# РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ СЃС‚СЂР°РЅРёС†С‹
# ============================================================================
st.set_page_config(
    page_title="Р›РѕС‚РµСЂРµСЏ СЂРѕР¶РґРµРЅРёСЏ В· Р”РµРјРѕРіСЂР°С„РёС‡РµСЃРєРёР№ Р°С‚Р»Р°СЃ",
    page_icon="рџЊЌ",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": (
            "Р”РµРјРѕРіСЂР°С„РёС‡РµСЃРєРёР№ Р°С‚Р»Р°СЃ РєРѕРіРѕСЂС‚РЅС‹С… РІРµСЂРѕСЏС‚РЅРѕСЃС‚РµР№ СЂРѕР¶РґРµРЅРёСЏ "
            "РїРѕ РґР°РЅРЅС‹Рј UN World Population Prospects 2024."
        ),
    },
)

# ============================================================================
# РџР°Р»РёС‚СЂР° Рё С‚РёРїРѕРіСЂР°С„РёРєР° вЂ” СЃРёРЅС…СЂРѕРЅРёР·РёСЂРѕРІР°РЅС‹ СЃРѕ static/index.html
# ============================================================================
PALETTE = {
    "paper":        "#f4ecd8",
    "paper_dark":   "#ebdfc1",
    "paper_darker": "#d9c89e",
    "ink":          "#2a1810",
    "ink_soft":     "#4a3528",
    "ink_light":    "#7a5d48",
    "terracotta":   "#b8492f",
    "terracotta_d": "#8d3220",
    "terracotta_dd":"#6e1f10",
    "ochre":        "#c89832",
    "olive":        "#6b7a3a",
    "water":        "#e8e0c8",
}

# Р›РѕРіР°СЂРёС„РјРёС‡РµСЃРєР°СЏ С€РєР°Р»Р° В«РґРѕР»Рё РІ РјРёСЂРѕРІРѕР№ РєРѕРіРѕСЂС‚Рµ РЅРѕРІРѕСЂРѕР¶РґС‘РЅРЅС‹С…В»
COLOR_STOPS = [
    (0.0,   PALETTE["paper"]),
    (0.05,  "#ecdcb8"),
    (0.20,  "#e8b89c"),
    (1.0,   "#d97a5a"),
    (5.0,   PALETTE["terracotta"]),
    (15.0,  PALETTE["terracotta_d"]),
    (25.0,  PALETTE["terracotta_dd"]),
]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,300;9..144,400;9..144,500;9..144,600;9..144,700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"]  {{
        font-family: 'Fraunces', Georgia, serif;
        font-feature-settings: "ss01", "onum";
        color: {PALETTE['ink']};
    }}

    .stApp {{
        background: {PALETTE['paper']};
        background-image:
            radial-gradient(circle at 20% 30%, rgba(184,73,47,0.04) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(107,122,58,0.04) 0%, transparent 40%),
            repeating-linear-gradient(0deg, rgba(42,24,16,0.013) 0px, rgba(42,24,16,0.013) 1px, transparent 1px, transparent 3px);
    }}
    .block-container {{
        max-width: 1180px !important;
        padding-top: 2.4rem;
        padding-bottom: 5rem;
    }}

    /* в”Ђв”Ђ masthead в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    .masthead {{
        border-top: 4px double {PALETTE['ink']};
        border-bottom: 1px solid {PALETTE['ink']};
        padding: 14px 0;
        margin-bottom: 56px;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {PALETTE['ink_soft']};
    }}
    .masthead-left {{ font-weight: 700; }}
    .masthead-right {{ font-style: italic; text-transform: none; letter-spacing: 0.05em; }}

    /* в”Ђв”Ђ hero в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    .hero-eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: {PALETTE['terracotta']};
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .hero-eyebrow::before {{
        content: "";
        display: inline-block;
        width: 40px;
        height: 1px;
        background: {PALETTE['terracotta']};
    }}
    .hero-h1 {{
        font-family: 'Fraunces', serif;
        font-variation-settings: 'opsz' 144, 'wght' 400, 'SOFT' 0, 'WONK' 1;
        font-size: clamp(2.6rem, 5.6vw, 4.8rem);
        line-height: 0.98;
        letter-spacing: -0.025em;
        margin: 0 0 22px 0;
        font-weight: 400;
        color: {PALETTE['ink']};
    }}
    .hero-h1 em {{
        font-style: italic;
        color: {PALETTE['terracotta_d']};
    }}
    .hero-sub {{
        font-size: 1.1rem;
        color: {PALETTE['ink_soft']};
        max-width: 660px;
        font-style: italic;
        line-height: 1.55;
        margin-bottom: 36px;
    }}

    /* в”Ђв”Ђ eyebrows / section headings в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    .section-eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: {PALETTE['ink_light']};
        margin: 0 0 8px 0;
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .section-eyebrow::before {{
        content: "";
        width: 24px; height: 1px;
        background: {PALETTE['ink_light']};
    }}
    .section-title {{
        font-family: 'Fraunces', serif;
        font-variation-settings: 'opsz' 60, 'wght' 500, 'WONK' 1;
        font-size: 1.9rem;
        line-height: 1.15;
        margin: 0 0 22px 0;
        letter-spacing: -0.015em;
        color: {PALETTE['ink']};
    }}
    .section-title em {{ font-style: italic; color: {PALETTE['terracotta_d']}; }}
    .caption {{
        font-size: 0.95rem;
        color: {PALETTE['ink_soft']};
        font-style: italic;
        margin: 0 0 20px 0;
        max-width: 680px;
    }}

    /* в”Ђв”Ђ result block в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    .result-block {{
        text-align: center;
        border-top: 1px solid {PALETTE['ink']};
        border-bottom: 1px solid {PALETTE['ink']};
        padding: 44px 20px 52px;
        margin: 12px 0 56px 0;
        position: relative;
    }}
    .result-block::before, .result-block::after {{
        content: "вќ¦";
        position: absolute;
        font-size: 18px;
        color: {PALETTE['terracotta']};
        background: {PALETTE['paper']};
        padding: 0 14px;
        left: 50%;
        transform: translateX(-50%);
    }}
    .result-block::before {{ top: -10px; }}
    .result-block::after {{ bottom: -12px; }}
    .result-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: {PALETTE['ink_light']};
        margin-bottom: 18px;
    }}
    .result-big {{
        font-family: 'Fraunces', serif;
        font-variation-settings: 'opsz' 144, 'wght' 300, 'WONK' 1;
        font-size: clamp(3.2rem, 10vw, 7rem);
        line-height: 0.95;
        letter-spacing: -0.04em;
        font-variant-numeric: tabular-nums lining-nums;
        color: {PALETTE['ink']};
    }}
    .result-big .pct-sign {{
        color: {PALETTE['terracotta']};
        font-style: italic;
        font-size: 0.7em;
        vertical-align: 0.05em;
    }}
    .result-secondary {{
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 1.25rem;
        color: {PALETTE['ink_soft']};
        margin-top: 4px;
    }}
    .result-secondary strong {{
        font-weight: 600;
        color: {PALETTE['ink']};
        font-style: normal;
    }}

    /* в”Ђв”Ђ РєРѕРЅС‚СЂРѕР»С‹ (year + country) в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    div[data-testid="stSlider"] label,
    div[data-testid="stSelectbox"] label {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: {PALETTE['ink_light']} !important;
    }}
    div[data-testid="stSlider"] [role="slider"] {{
        background: {PALETTE['terracotta']} !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background: {PALETTE['paper']} !important;
        border: none !important;
        border-bottom: 2px solid {PALETTE['ink']} !important;
        border-radius: 0 !important;
        font-family: 'Fraunces', serif !important;
        font-size: 1.3rem !important;
        font-weight: 500 !important;
        color: {PALETTE['ink']} !important;
    }}

    /* в”Ђв”Ђ РјРµС‚СЂРёРєРё в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    div[data-testid="stMetric"] {{
        background: {PALETTE['paper']};
        padding: 24px 22px;
        border: 1px solid {PALETTE['ink']};
    }}
    div[data-testid="stMetricLabel"] {{
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-size: 10px !important;
        color: {PALETTE['ink_light']} !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'Fraunces', serif !important;
        font-variation-settings: 'opsz' 60, 'wght' 500, 'WONK' 1;
        font-size: 2.0rem !important;
        color: {PALETTE['ink']} !important;
        font-variant-numeric: tabular-nums;
    }}
    div[data-testid="stMetricDelta"] {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        color: {PALETTE['ink_soft']} !important;
    }}

    /* в”Ђв”Ђ horizontal rule в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    hr {{
        border: none;
        border-top: 1px solid {PALETTE['paper_darker']};
        margin: 36px 0;
    }}

    /* в”Ђв”Ђ footnotes в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    .footnotes {{
        border-top: 4px double {PALETTE['ink']};
        padding-top: 28px;
        margin-top: 64px;
        font-size: 0.92rem;
        color: {PALETTE['ink_soft']};
        font-style: italic;
        line-height: 1.65;
    }}
    .footnotes h3 {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: {PALETTE['terracotta']};
        margin-bottom: 12px;
        font-style: normal;
    }}
    .footnotes p {{ margin-bottom: 12px; }}
    .footnotes strong {{ color: {PALETTE['ink']}; font-weight: 600; }}

    /* в”Ђв”Ђ streamlit chrome cleanup в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{
        background: transparent;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# Р—Р°РіСЂСѓР·РєР° РґР°РЅРЅС‹С…
# ============================================================================
ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "births_compact.json"


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, Any]:
    if not DATA_PATH.exists():
        st.error(
            f"РќРµ РЅР°Р№РґРµРЅ РґР°С‚Р°СЃРµС‚: `{DATA_PATH}`.\n\n"
            "Р—Р°РїСѓСЃС‚РёС‚Рµ `python scripts/build_data.py`, С‡С‚РѕР±С‹ РїРѕСЃС‚СЂРѕРёС‚СЊ "
            "`births_compact.json` РёР· РёСЃС…РѕРґРЅРѕРіРѕ xlsx UN WPP 2024."
        )
        st.stop()
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


DATA = load_data()
META = DATA["metadata"]
COUNTRIES: dict[str, dict[str, Any]] = DATA["countries"]
YEAR_MIN: int = META["year_start"]
YEAR_MAX: int = META["year_end"]
WORLD: list[float] = META["world"]


def births_k(iso: str, year: int) -> float:
    """Р–РёРІРѕСЂРѕР¶РґРµРЅРёСЏ РІ СЃС‚СЂР°РЅРµ Р·Р° РіРѕРґ, С‚С‹СЃСЏС‡Рё."""
    return COUNTRIES[iso]["b"][year - YEAR_MIN]


def world_births_k(year: int) -> float:
    return WORLD[year - YEAR_MIN]


def share_pct(iso: str, year: int) -> float:
    w = world_births_k(year)
    return (births_k(iso, year) / w * 100) if w > 0 else 0.0


def fmt_int(n: float) -> str:
    """Р¤РѕСЂРјР°С‚РёСЂРѕРІР°РЅРёРµ С‡РёСЃР»Р° РІ СЃС‚РёР»Рµ В«1 234 567В»."""
    return f"{round(n):,}".replace(",", "\u00a0")


def fmt_pct(p: float) -> str:
    if p >= 1:
        return f"{p:.2f}"
    if p >= 0.1:
        return f"{p:.2f}"
    if p >= 0.01:
        return f"{p:.3f}"
    return f"{p:.4f}"


# ============================================================================
# MASTHEAD + HERO
# ============================================================================
st.markdown(
    f"""
    <header class="masthead">
        <div class="masthead-left">Р”РµРјРѕРіСЂР°С„РёС‡РµСЃРєРёР№ РђС‚Р»Р°СЃ в„– 1 вЂ» Р’С‹РїСѓСЃРє 2026</div>
        <div class="masthead-right">РїРѕ РґР°РЅРЅС‹Рј United Nations В· World Population Prospects 2024</div>
    </header>

    <section>
        <div class="hero-eyebrow">РљРѕРіРѕСЂС‚РЅС‹Рµ РІРµСЂРѕСЏС‚РЅРѕСЃС‚Рё СЂРѕР¶РґРµРЅРёСЏ</div>
        <h1 class="hero-h1">РљР°РєРѕРІР° Р±С‹Р»Р° РІРµСЂРѕСЏС‚РЅРѕСЃС‚СЊ<br><em>СЂРѕРґРёС‚СЊСЃСЏ</em> РёРјРµРЅРЅРѕ Р·РґРµСЃСЊ<br>РёРјРµРЅРЅРѕ С‚РѕРіРґР°?</h1>
        <p class="hero-sub">
            РљР°Р¶РґС‹Р№ РіРѕРґ Р—РµРјР»СЏ РїСЂРёРЅРёРјР°РµС‚ РѕРєРѕР»Рѕ 130&nbsp;РјРёР»Р»РёРѕРЅРѕРІ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№. Р­С‚РѕС‚ Р°С‚Р»Р°СЃ СЂР°СЃРєР»Р°РґС‹РІР°РµС‚
            РјРёСЂРѕРІСѓСЋ РєРѕРіРѕСЂС‚Сѓ РЅРѕРІРѕСЂРѕР¶РґС‘РЅРЅС‹С… РЅР° СЃС‚СЂР°РЅС‹ Рё РіРѕРґС‹ Рё РїРѕРєР°Р·С‹РІР°РµС‚ СѓРґРµР»СЊРЅС‹Р№ РІРµСЃ РєР°Р¶РґРѕР№ СЏС‡РµР№РєРё вЂ”
            С‚Рѕ РµСЃС‚СЊ Р°РїСЂРёРѕСЂРЅСѓСЋ РІРµСЂРѕСЏС‚РЅРѕСЃС‚СЊ С‚РѕРіРѕ, С‡С‚Рѕ СЃР»СѓС‡Р°Р№РЅРѕ РІС‹Р±СЂР°РЅРЅС‹Р№ РјР»Р°РґРµРЅРµС† СЂРѕРґРёР»СЃСЏ РёРјРµРЅРЅРѕ
            РІ&nbsp;РІС‹Р±СЂР°РЅРЅРѕР№ СЃС‚СЂР°РЅРµ РІ&nbsp;РІС‹Р±СЂР°РЅРЅРѕРј РіРѕРґСѓ.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# РљРћРќРўР РћР›Р« вЂ” РіРѕРґ Рё СЃС‚СЂР°РЅР°
# ============================================================================
sorted_countries = sorted(COUNTRIES.items(), key=lambda kv: kv[1]["r"])
ISO_OPTIONS = [iso for iso, _ in sorted_countries]
LABEL_FOR = {iso: c["r"] for iso, c in sorted_countries}
ISO_TO_REGION = {iso: c["g"] for iso, c in COUNTRIES.items()}
REGIONS = sorted({c["g"] for c in COUNTRIES.values()})

col_yr, col_co = st.columns([1, 1], gap="large")
with col_yr:
    year = st.slider(
        "Р“РћР” Р РћР–Р”Р•РќРРЇ (РљРђР›Р•РќР”РђР РќРђРЇ РљРћР“РћР РўРђ)",
        min_value=YEAR_MIN,
        max_value=YEAR_MAX,
        value=1992,
        step=1,
        help=(
            "РљР°Р»РµРЅРґР°СЂРЅС‹Р№ РіРѕРґ, РїРѕ РєРѕС‚РѕСЂРѕРјСѓ СЃС‡РёС‚Р°РµС‚СЃСЏ РґРѕР»СЏ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РІ "
            "РіР»РѕР±Р°Р»СЊРЅРѕР№ РєРѕРіРѕСЂС‚Рµ РЅРѕРІРѕСЂРѕР¶РґС‘РЅРЅС‹С…."
        ),
    )
with col_co:
    default_iso = "RUS" if "RUS" in ISO_OPTIONS else ISO_OPTIONS[0]
    iso = st.selectbox(
        "РЎРўР РђРќРђ (РЎРћР’Р Р•РњР•РќРќР«Р• Р“Р РђРќРР¦Р« РћРћРќ)",
        options=ISO_OPTIONS,
        index=ISO_OPTIONS.index(default_iso),
        format_func=lambda x: LABEL_FOR[x],
        help=(
            "РћРћРќ WPP 2024 СЂРµС‚СЂРѕСЃРїРµРєС‚РёРІРЅРѕ РїСЂРёРјРµРЅСЏРµС‚ СЃРѕРІСЂРµРјРµРЅРЅС‹Рµ РіСЂР°РЅРёС†С‹: "
            "В«Р РѕСЃСЃРёСЏ РІ 1950В» РѕР·РЅР°С‡Р°РµС‚ С‚РµСЂСЂРёС‚РѕСЂРёСЋ Р РЎР¤РЎР , РЅРµ РЎРЎРЎР ."
        ),
    )


# ============================================================================
# Р“Р»Р°РІРЅС‹Р№ СЂРµР·СѓР»СЊС‚Р°С‚
# ============================================================================
country = COUNTRIES[iso]
c_thousands = births_k(iso, year)
w_thousands = world_births_k(year)
c_births = c_thousands * 1000
w_births = w_thousands * 1000
pct = share_pct(iso, year)
one_in = (w_births / c_births) if c_births > 0 else float("inf")

st.markdown(
    f"""
    <div class="result-block">
        <div class="result-label">Р”РѕР»СЏ РІ РјРёСЂРѕРІРѕР№ РєРѕРіРѕСЂС‚Рµ РЅРѕРІРѕСЂРѕР¶РґС‘РЅРЅС‹С… В· {year}</div>
        <div class="result-big">{fmt_pct(pct)}<span class="pct-sign">%</span></div>
        <div class="result-secondary">РїСЂРёРјРµСЂРЅРѕ <strong>1 РёР· {fmt_int(one_in)}</strong> РЅРѕРІРѕСЂРѕР¶РґС‘РЅРЅС‹С… С‚РѕРіРѕ РіРѕРґР°</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# В§ I В· РљРђР РўРђ РњРР Рђ
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">В§ I В· РџСЂРѕСЃС‚СЂР°РЅСЃС‚РІРµРЅРЅРѕРµ СЂР°СЃРїСЂРµРґРµР»РµРЅРёРµ РєРѕРіРѕСЂС‚С‹</div>
    <h2 class="section-title">Р“РґРµ СЂРѕР¶РґР°Р»РёСЃСЊ Р»СЋРґРё РІ&nbsp;<em>{year}</em>&nbsp;РіРѕРґСѓ</h2>
    <p class="caption">
        Р¦РІРµС‚ РїРѕРєР°Р·С‹РІР°РµС‚ СѓРґРµР»СЊРЅС‹Р№ РІРµСЃ СЃС‚СЂР°РЅС‹ РІ РјРёСЂРѕРІРѕР№ РєРѕРіРѕСЂС‚Рµ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РїРѕ Р»РѕРіР°СЂРёС„РјРёС‡РµСЃРєРѕР№ С€РєР°Р»Рµ.
        РўРµРјРЅРµРµ вЂ” РІС‹С€Рµ РґРѕР»СЏ. РџРѕРґ С‚С‘РїР»С‹РјРё РѕС‚С‚РµРЅРєР°РјРё СЃРєСЂС‹С‚С‹ РєСЂСѓРїРЅРµР№С€РёРµ С†РµРЅС‚СЂС‹ РІРѕСЃРїСЂРѕРёР·РІРѕРґСЃС‚РІР°;
        Р±Р»РµРґРЅС‹Р№ С„РѕРЅ вЂ” СЃС‚СЂР°РЅС‹ СЃ РјР°Р»С‹Рј С‡РёСЃР»РѕРј СЂРѕР¶РґРµРЅРёР№ РёР»Рё, СЂРµР¶Рµ, РѕС‚СЃСѓС‚СЃС‚РІСѓСЋС‰РёРµ РІ РґР°С‚Р°СЃРµС‚Рµ.
    </p>
    """,
    unsafe_allow_html=True,
)


def color_for_pct(p: float) -> str:
    """Р›РѕРіР°СЂРёС„РјРёС‡РµСЃРєР°СЏ РёРЅС‚РµСЂРїРѕР»СЏС†РёСЏ РјРµР¶РґСѓ РѕРїРѕСЂРЅС‹РјРё С†РІРµС‚Р°РјРё."""
    import math
    if p < 0.005:
        return PALETTE["water"]
    for i in range(len(COLOR_STOPS) - 1):
        v0, c0 = COLOR_STOPS[i]
        v1, c1 = COLOR_STOPS[i + 1]
        if p <= v1:
            t = (math.log(p + 0.01) - math.log(v0 + 0.01)) / (
                math.log(v1 + 0.01) - math.log(v0 + 0.01)
            )
            t = max(0.0, min(1.0, t))
            r0, g0, b0 = int(c0[1:3], 16), int(c0[3:5], 16), int(c0[5:7], 16)
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            return (
                f"rgb({int(r0 + (r1 - r0) * t)},"
                f"{int(g0 + (g1 - g0) * t)},"
                f"{int(b0 + (b1 - b0) * t)})"
            )
    return COLOR_STOPS[-1][1]


map_rows = []
for code, c in COUNTRIES.items():
    b_k = c["b"][year - YEAR_MIN]
    if b_k <= 0:
        continue
    p = b_k / w_thousands * 100 if w_thousands > 0 else 0
    map_rows.append(
        {
            "iso": code,
            "name": c["r"],
            "births": b_k * 1000,
            "pct": p,
            "color": color_for_pct(p),
        }
    )
map_df = pd.DataFrame(map_rows)

# Р”РёСЃРєСЂРµС‚РЅР°СЏ С‡РёСЃР»РѕРІР°СЏ С€РєР°Р»Р° РґР»СЏ colorbar (Р»РѕРіР°СЂРёС„РјРёС‡РµСЃРєРёРµ Р±РёРЅС‹)
TICK_VALS = [0.01, 0.05, 0.2, 1, 5, 15, 25]
TICK_LBLS = ["0.01%", "0.05%", "0.2%", "1%", "5%", "15%", "25%"]

fig_map = go.Figure()

# Р‘Р°Р·РѕРІС‹Р№ СЃР»РѕР№ вЂ” РІСЃРµ СЃС‚СЂР°РЅС‹ С‡РµСЂРµР· choropleth СЃ custom-РїР°Р»РёС‚СЂРѕР№
fig_map.add_trace(
    go.Choropleth(
        locations=map_df["iso"],
        z=map_df["pct"],
        locationmode="ISO-3",
        customdata=map_df[["name", "births"]].values,
        colorscale=[
            [0.00, PALETTE["paper"]],
            [0.05, "#ecdcb8"],
            [0.20, "#e8b89c"],
            [0.45, "#d97a5a"],
            [0.65, PALETTE["terracotta"]],
            [0.85, PALETTE["terracotta_d"]],
            [1.00, PALETTE["terracotta_dd"]],
        ],
        zmin=0.0,
        zmax=max(map_df["pct"].max(), 1.0),
        marker_line_color=PALETTE["ink"],
        marker_line_width=0.35,
        colorbar=dict(
            title=dict(
                text="РґРѕР»СЏ РєРѕРіРѕСЂС‚С‹, %",
                font=dict(family="JetBrains Mono", size=10, color=PALETTE["ink_soft"]),
            ),
            tickfont=dict(family="JetBrains Mono", size=10, color=PALETTE["ink_soft"]),
            thickness=10,
            len=0.55,
            outlinewidth=0,
            ticksuffix="%",
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "РґРѕР»СЏ РІ РјРёСЂРµ: %{z:.3f}%<br>"
            "Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№: %{customdata[1]:,.0f}"
            "<extra></extra>"
        ),
    )
)

# РџРѕРґСЃРІРµС‚РєР° РІС‹Р±СЂР°РЅРЅРѕР№ СЃС‚СЂР°РЅС‹
if iso in map_df["iso"].values:
    fig_map.add_trace(
        go.Choropleth(
            locations=[iso],
            z=[1],
            locationmode="ISO-3",
            showscale=False,
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            marker_line_color=PALETTE["terracotta_d"],
            marker_line_width=2.5,
            hoverinfo="skip",
        )
    )

fig_map.update_geos(
    projection_type="equal earth",
    showcoastlines=True,
    coastlinecolor=PALETTE["ink"],
    coastlinewidth=0.4,
    showland=True,
    landcolor=PALETTE["paper_darker"],
    showocean=True,
    oceancolor=PALETTE["water"],
    showframe=False,
    bgcolor=PALETTE["paper"],
    showcountries=True,
    countrycolor=PALETTE["ink"],
    countrywidth=0.25,
    showlakes=False,
    lataxis_showgrid=True,
    lonaxis_showgrid=True,
    lataxis_gridcolor="rgba(42,24,16,0.10)",
    lonaxis_gridcolor="rgba(42,24,16,0.10)",
    lataxis_gridwidth=0.4,
    lonaxis_gridwidth=0.4,
)
fig_map.update_layout(
    paper_bgcolor=PALETTE["paper"],
    plot_bgcolor=PALETTE["paper"],
    margin=dict(l=0, r=0, t=0, b=0),
    height=520,
    font=dict(family="Fraunces", color=PALETTE["ink"]),
    dragmode=False,
)
st.plotly_chart(
    fig_map,
    width="stretch",
    config={
        "displayModeBar": False,
        "scrollZoom": False,
    },
)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# В§ II В· РР—РћРўРРџ вЂ” 1000 РўРћР§Р•Рљ
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">В§ II В· РР·РѕС‚РёРї РєРѕРіРѕСЂС‚С‹</div>
    <h2 class="section-title">РР· <em>1000</em> РјР»Р°РґРµРЅС†РµРІ РјРёСЂР° С‚РѕРіРѕ РіРѕРґР° вЂ”<br>СЃС‚РѕР»СЊРєРѕ СЂРѕРґРёР»РёСЃСЊ Р·РґРµСЃСЊ</h2>
    """,
    unsafe_allow_html=True,
)

dots_to_fill = round(pct * 10)  # 1000 С‚РѕС‡РµРє = 100% Г— 10
if dots_to_fill == 0:
    isotype_caption = (
        f"РњРµРЅСЊС€Рµ РѕРґРЅРѕРіРѕ РјР»Р°РґРµРЅС†Р° РёР· С‚С‹СЃСЏС‡Рё вЂ” С‚РѕС‡РЅРµРµ, "
        f"{fmt_int(pct * 1000)} РёР· 100 000 РЅРѕРІРѕСЂРѕР¶РґС‘РЅРЅС‹С… РјРёСЂР°."
    )
elif dots_to_fill > 800:
    isotype_caption = (
        f"{dots_to_fill} РёР· 1000 РјР»Р°РґРµРЅС†РµРІ РјРёСЂР° РІ {year} РіРѕРґСѓ СЂРѕРґРёР»РёСЃСЊ РІ СЌС‚РѕР№ СЃС‚СЂР°РЅРµ вЂ” "
        "СЌС‚Рѕ Р±С‹Р»Р° РґРµРјРѕРіСЂР°С„РёС‡РµСЃРєР°СЏ СЃРІРµСЂС…РґРµСЂР¶Р°РІР°."
    )
else:
    isotype_caption = (
        f"РљР°Р¶РґР°СЏ С‚РѕС‡РєР° СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓРµС‚ РѕРґРЅРѕРјСѓ РјР»Р°РґРµРЅС†Сѓ РёР· С‚С‹СЃСЏС‡Рё СЃР»СѓС‡Р°Р№РЅРѕ РІС‹Р±СЂР°РЅРЅС‹С… РїРѕ РјРёСЂСѓ РІ {year} РіРѕРґСѓ. "
        "Р—Р°РєСЂР°С€РµРЅС‹ СЂРѕРґРёРІС€РёРµСЃСЏ РІ РІС‹Р±СЂР°РЅРЅРѕР№ СЃС‚СЂР°РЅРµ."
    )
st.markdown(f"<p class='caption'>{isotype_caption}</p>", unsafe_allow_html=True)

ROWS, COLS = 20, 50  # 1000 С‚РѕС‡РµРє, РїСЂСЏРјРѕСѓРіРѕР»СЊРЅРёРє
xs = [c for r in range(ROWS) for c in range(COLS)]
ys = [r for r in range(ROWS) for c in range(COLS)]
colors = [
    PALETTE["terracotta"] if (r * COLS + c) < dots_to_fill else PALETTE["paper"]
    for r in range(ROWS) for c in range(COLS)
]
borders = [
    PALETTE["terracotta_d"] if (r * COLS + c) < dots_to_fill else PALETTE["ink_light"]
    for r in range(ROWS) for c in range(COLS)
]

fig_iso = go.Figure(
    go.Scatter(
        x=xs,
        y=ys,
        mode="markers",
        marker=dict(
            size=10,
            color=colors,
            line=dict(color=borders, width=1),
            symbol="circle",
        ),
        hoverinfo="skip",
    )
)
fig_iso.update_layout(
    paper_bgcolor=PALETTE["paper_dark"],
    plot_bgcolor=PALETTE["paper_dark"],
    margin=dict(l=24, r=24, t=20, b=20),
    height=260,
    xaxis=dict(visible=False, range=[-1, COLS], scaleanchor="y", scaleratio=1),
    yaxis=dict(visible=False, range=[ROWS, -1]),
    showlegend=False,
)
st.plotly_chart(fig_iso, width="stretch", config={"displayModeBar": False})

# Р›С‘РіРєР°СЏ Р»РµРіРµРЅРґР°
st.markdown(
    f"""
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
        text-transform:uppercase;letter-spacing:0.1em;color:{PALETTE['ink_soft']};
        margin-top:8px;display:flex;gap:24px;flex-wrap:wrap;">
        <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;
            background:{PALETTE['terracotta']};border:1px solid {PALETTE['terracotta_d']};
            margin-right:8px;vertical-align:-1px;"></span>{country['r']}</span>
        <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;
            background:{PALETTE['paper']};border:1px solid {PALETTE['ink_light']};
            margin-right:8px;vertical-align:-1px;"></span>РѕСЃС‚Р°Р»СЊРЅРѕР№ РјРёСЂ</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# В§ III В· Р”Р•РњРћР“Р РђР¤РР§Р•РЎРљРР™ РљРћРќРўР•РљРЎРў
# ============================================================================
ranking = sorted(
    [
        (code, c["b"][year - YEAR_MIN])
        for code, c in COUNTRIES.items()
        if c["b"][year - YEAR_MIN] > 0
    ],
    key=lambda x: -x[1],
)
rank_position = next(
    (i + 1 for i, (code, _) in enumerate(ranking) if code == iso),
    None,
)
rank_total = len(ranking)

# Р”РѕР»СЏ РІ СЂРµРіРёРѕРЅРµ
region = ISO_TO_REGION[iso]
region_total_k = sum(
    COUNTRIES[c]["b"][year - YEAR_MIN]
    for c in COUNTRIES
    if ISO_TO_REGION[c] == region
)
share_in_region = (
    c_thousands / region_total_k * 100 if region_total_k > 0 else 0
)

st.markdown(
    f"""
    <div class="section-eyebrow">В§ III В· Р”РµРјРѕРіСЂР°С„РёС‡РµСЃРєРёР№ РєРѕРЅС‚РµРєСЃС‚</div>
    <h2 class="section-title">Р§С‚Рѕ РѕР·РЅР°С‡Р°СЋС‚ СЌС‚Рё С‡РёСЃР»Р°</h2>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4, gap="small")
with m1:
    st.metric(
        "Р–РёРІРѕСЂРѕР¶РґРµРЅРёР№ В· Р’РЎР•Р“Рћ",
        fmt_int(c_births),
        help=f"{country['r']}, {year}. РСЃС‚РѕС‡РЅРёРє: UN WPP 2024 (Births, thousands).",
    )
with m2:
    per_day = c_births / 365.25
    st.metric(
        "Р’ СЃСѓС‚РєРё",
        fmt_int(per_day),
        delta=f"в‰€ {per_day / 86400:.2f} СЂРѕР¶Рґ./СЃРµРє.",
        delta_color="off",
        help="РЎСЂРµРґРЅРµСЃСѓС‚РѕС‡РЅС‹Р№ С‚РµРјРї РІРѕСЃРїСЂРѕРёР·РІРѕРґСЃС‚РІР° Р·Р° РІС‹Р±СЂР°РЅРЅС‹Р№ РіРѕРґ.",
    )
with m3:
    rank_desc = (
        "РІС…РѕРґРёС‚ РІ РїСЏС‚С‘СЂРєСѓ"
        if rank_position <= 5
        else "РІ РїРµСЂРІРѕР№ РґРµСЃСЏС‚РєРµ"
        if rank_position <= 10
        else "РІ РїРµСЂРІРѕР№ С‡РµС‚РІРµСЂС‚Рё"
        if rank_position <= rank_total // 4
        else "РІС‹С€Рµ РјРµРґРёР°РЅС‹"
        if rank_position <= rank_total // 2
        else "РЅРёР¶Рµ РјРµРґРёР°РЅС‹"
    )
    st.metric(
        "РњРµСЃС‚Рѕ РІ РјРёСЂРµ",
        f"{rank_position} РёР· {rank_total}",
        delta=rank_desc,
        delta_color="off",
        help="Р Р°РЅРі СЃС‚СЂР°РЅС‹ РїРѕ Р°Р±СЃРѕР»СЋС‚РЅРѕРјСѓ С‡РёСЃР»Сѓ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ СЃСЂРµРґРё РІСЃРµС… СЃС‚СЂР°РЅ РґР°С‚Р°СЃРµС‚Р°.",
    )
with m4:
    st.metric(
        f"Р”РѕР»СЏ РІ СЂРµРіРёРѕРЅРµ ({region})",
        f"{share_in_region:.1f}%",
        delta=f"{fmt_int(region_total_k * 1000)} СЂРѕР¶Рґ. РІ СЂРµРіРёРѕРЅРµ",
        delta_color="off",
        help=(
            "РЈРґРµР»СЊРЅС‹Р№ РІРµСЃ СЃС‚СЂР°РЅС‹ РІ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёСЏС… СЃРІРѕРµРіРѕ РјР°РєСЂРѕСЂРµРіРёРѕРЅР° (UN geoscheme: "
            "Africa / Asia / Europe / Americas / Oceania)."
        ),
    )

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# В§ IV В· РўРћРџ РЎРўР РђРќ (Р“РћР РР—РћРќРўРђР›Р¬РќРђРЇ Р“РРЎРўРћР“Р РђРњРњРђ)
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">В§ IV В· РЎС‚СЂСѓРєС‚СѓСЂР° РјРёСЂРѕРІРѕР№ РєРѕРіРѕСЂС‚С‹</div>
    <h2 class="section-title">Р“РґРµ СЂРѕР¶РґР°Р»РѕСЃСЊ <em>Р±РѕР»СЊС€Рµ РІСЃРµРіРѕ</em> Р»СЋРґРµР№<br>РІ РІС‹Р±СЂР°РЅРЅС‹Р№ РіРѕРґ</h2>
    <p class="caption">
        РўРѕРї-12 СЃС‚СЂР°РЅ РїРѕ Р°Р±СЃРѕР»СЋС‚РЅРѕРјСѓ С‡РёСЃР»Сѓ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РїР»СЋСЃ РІС‹Р±СЂР°РЅРЅР°СЏ СЃС‚СЂР°РЅР°
        (РµСЃР»Рё РѕРЅР° РІРЅРµ С‚РѕРїР°). РќР° СЃС‚РѕР»СЊРєРѕ РїСЂРѕС†РµРЅС‚РѕРІ РјРёСЂРѕРІРѕР№ РєРѕРіРѕСЂС‚С‹ РїСЂРёС…РѕРґРёС‚СЃСЏ
        РЅР° РєР°Р¶РґСѓСЋ С‚РµСЂСЂРёС‚РѕСЂРёСЋ.
    </p>
    """,
    unsafe_allow_html=True,
)

TOP_N = 12
top = ranking[:TOP_N]
in_top = any(code == iso for code, _ in top)
display_list = top if in_top else top + [(iso, c_thousands)]

bar_rows = []
for code, b_k in display_list:
    real_rank = next(i + 1 for i, (c, _) in enumerate(ranking) if c == code)
    bar_rows.append(
        {
            "rank": real_rank,
            "country": COUNTRIES[code]["r"],
            "label": f"{real_rank:02d}  {COUNTRIES[code]['r']}",
            "pct": b_k * 1000 / w_births * 100,
            "births": b_k * 1000,
            "is_user": code == iso,
        }
    )
bar_df = pd.DataFrame(bar_rows)

fig_bar = go.Figure(
    go.Bar(
        x=bar_df["pct"],
        y=bar_df["label"],
        orientation="h",
        marker=dict(
            color=[
                PALETTE["terracotta"] if u else PALETTE["ink"]
                for u in bar_df["is_user"]
            ],
            line=dict(color=PALETTE["paper"], width=0),
        ),
        text=[f"{p:.2f}%" for p in bar_df["pct"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", color=PALETTE["ink_soft"], size=11),
        hovertemplate=(
            "<b>%{y}</b><br>%{x:.3f}% РјРёСЂРѕРІРѕР№ РєРѕРіРѕСЂС‚С‹"
            "<br>%{customdata:,.0f} Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№<extra></extra>"
        ),
        customdata=bar_df["births"],
        cliponaxis=False,
    )
)
fig_bar.update_layout(
    paper_bgcolor=PALETTE["paper"],
    plot_bgcolor=PALETTE["paper"],
    height=max(360, 38 * len(bar_df)),
    margin=dict(l=0, r=80, t=10, b=20),
    yaxis=dict(
        autorange="reversed",
        tickfont=dict(family="Fraunces", color=PALETTE["ink"], size=13),
        showgrid=False,
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="JetBrains Mono", color=PALETTE["ink_light"], size=10),
        ticksuffix="%",
        zeroline=False,
    ),
    font=dict(family="Fraunces"),
    showlegend=False,
)
st.plotly_chart(
    fig_bar,
    width="stretch",
    config={"displayModeBar": False},
)


# ============================================================================
# В§ V В· Р”РРќРђРњРРљРђ (TIMELINE)
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">В§ V В· РљРѕРіРѕСЂС‚РЅР°СЏ РґРёРЅР°РјРёРєР°</div>
    <h2 class="section-title">
        РљСЂРёРІР°СЏ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РІ&nbsp;<em>{country['r']}</em>,<br>
        РѕС‚ <em>{YEAR_MIN}</em> РґРѕ <em>{YEAR_MAX}</em>
    </h2>
    <p class="caption">
        РђР±СЃРѕР»СЋС‚РЅРѕРµ С‡РёСЃР»Рѕ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РїРѕ РіРѕРґР°Рј. РўРѕС‡РєР° вЂ” РІС‹Р±СЂР°РЅРЅС‹Р№ РІР°РјРё РіРѕРґ.
        Р’ СЂР°Р·РІРёС‚С‹С… СЌРєРѕРЅРѕРјРёРєР°С… С…РѕСЂРѕС€Рѕ РІРёРґРЅС‹ РїРµСЂРІР°СЏ (1950вЂ“60-Рµ) Рё РІС‚РѕСЂР°СЏ (1980-Рµ, СЌС…Рѕ)
        РїРѕСЃР»РµРІРѕРµРЅРЅС‹Рµ РґРµРјРѕРіСЂР°С„РёС‡РµСЃРєРёРµ РІРѕР»РЅС‹; РІ СЂР°Р·РІРёРІР°СЋС‰РёС…СЃСЏ вЂ” РїРѕР·РґРЅРёР№ РґРµРјРѕРіСЂР°С„РёС‡РµСЃРєРёР№ РїРµСЂРµС…РѕРґ
        СЃ РїРёРєРѕРј СЂРѕР¶РґР°РµРјРѕСЃС‚Рё РІ 1980вЂ“2000-С….
    </p>
    """,
    unsafe_allow_html=True,
)

trend_df = pd.DataFrame(
    {
        "year": list(range(YEAR_MIN, YEAR_MAX + 1)),
        "births": [b * 1000 for b in country["b"]],
    }
)

# 5-Р»РµС‚РЅРµРµ СЃРєРѕР»СЊР·СЏС‰РµРµ СЃСЂРµРґРЅРµРµ РєР°Рє В«С‚СЂРµРЅРґВ»
trend_df["smooth"] = trend_df["births"].rolling(window=5, center=True, min_periods=1).mean()

fig_line = go.Figure()
fig_line.add_trace(
    go.Scatter(
        x=trend_df["year"],
        y=trend_df["births"],
        mode="lines",
        line=dict(color=PALETTE["terracotta_d"], width=1.6),
        fill="tozeroy",
        fillcolor="rgba(184,73,47,0.15)",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№<extra></extra>",
        name="Р¶РёРІРѕСЂРѕР¶РґРµРЅРёСЏ",
    )
)
fig_line.add_trace(
    go.Scatter(
        x=trend_df["year"],
        y=trend_df["smooth"],
        mode="lines",
        line=dict(color=PALETTE["ink"], width=1.0, dash="dot"),
        hoverinfo="skip",
        name="5-Р»РµС‚РЅРµРµ СЃРіР»Р°Р¶РёРІР°РЅРёРµ",
    )
)
fig_line.add_trace(
    go.Scatter(
        x=[year],
        y=[c_births],
        mode="markers+text",
        marker=dict(
            size=14,
            color=PALETTE["terracotta_d"],
            line=dict(color=PALETTE["paper"], width=3),
        ),
        text=[f"{year}"],
        textposition="top center",
        textfont=dict(family="Fraunces", color=PALETTE["ink"], size=14),
        showlegend=False,
        hovertemplate=f"<b>{year}</b><br>{fmt_int(c_births)} Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№<extra></extra>",
    )
)
fig_line.update_layout(
    paper_bgcolor=PALETTE["paper"],
    plot_bgcolor=PALETTE["paper"],
    height=340,
    margin=dict(l=20, r=20, t=20, b=30),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family="JetBrains Mono", color=PALETTE["ink_light"], size=11),
        showline=True,
        linecolor=PALETTE["ink"],
        linewidth=1,
        dtick=10,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="JetBrains Mono", color=PALETTE["ink_light"], size=10),
        title=dict(
            text="Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РІ РіРѕРґ",
            font=dict(family="JetBrains Mono", size=10, color=PALETTE["ink_light"]),
        ),
        rangemode="tozero",
        tickformat=",",
    ),
    legend=dict(
        orientation="h",
        x=0,
        y=1.12,
        font=dict(family="JetBrains Mono", size=10, color=PALETTE["ink_soft"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)
st.plotly_chart(fig_line, width="stretch", config={"displayModeBar": False})


# ============================================================================
# В§ VI В· РЎР РђР’РќР•РќРР• РљРћР“РћР Рў
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">В§ VI В· РЎСЂР°РІРЅРµРЅРёРµ РєРѕРіРѕСЂС‚</div>
    <h2 class="section-title">РЎРѕРїРѕСЃС‚Р°РІР»РµРЅРёРµ РґРІСѓС… С‚СЂР°РµРєС‚РѕСЂРёР№</h2>
    <p class="caption">
        Р”РµРјРѕРіСЂР°С„РёС‡РµСЃРєР°СЏ РєРѕРјРїР°СЂР°С‚РёРІРёСЃС‚РёРєР°: РїРѕР»РѕР¶РёС‚Рµ РґРІРµ СЃС‚СЂР°РЅРѕРІС‹Рµ С‚СЂР°РµРєС‚РѕСЂРёРё Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№
        РЅР° РѕРґРЅСѓ РѕСЃСЊ вЂ” Рё Р·Р° РїР°СЂСѓ СЃРµРєСѓРЅРґ С‡РёС‚Р°СЋС‚СЃСЏ СЌРїРѕС…Рё РґРµРјРѕРіСЂР°С„РёС‡РµСЃРєРёС… РїРµСЂРµС…РѕРґРѕРІ,
        РІРѕР№РЅС‹, Р±СЌР±Рё-Р±СѓРјС‹, РїРѕСЃС‚-СЃРѕРІРµС‚СЃРєРёРµ В«РїСЂРѕРІР°Р»С‹В» Рё В«СЌС…Рѕ-РІРѕР»РЅС‹В».
    </p>
    """,
    unsafe_allow_html=True,
)

cmp_default = "USA" if "USA" in ISO_OPTIONS and iso != "USA" else (
    "DEU" if "DEU" in ISO_OPTIONS else ISO_OPTIONS[0]
)
iso_b = st.selectbox(
    "РЎРўР РђРќРђ Р”Р›РЇ РЎР РђР’РќР•РќРРЇ",
    options=ISO_OPTIONS,
    index=ISO_OPTIONS.index(cmp_default),
    format_func=lambda x: LABEL_FOR[x],
)
country_b = COUNTRIES[iso_b]
years_full = list(range(YEAR_MIN, YEAR_MAX + 1))

fig_cmp = go.Figure()
fig_cmp.add_trace(
    go.Scatter(
        x=years_full,
        y=[v * 1000 for v in country["b"]],
        mode="lines",
        name=country["r"],
        line=dict(color=PALETTE["terracotta_d"], width=2.2),
        hovertemplate=f"<b>{country['r']}</b> %{{x}}<br>%{{y:,.0f}} СЂРѕР¶Рґ.<extra></extra>",
    )
)
fig_cmp.add_trace(
    go.Scatter(
        x=years_full,
        y=[v * 1000 for v in country_b["b"]],
        mode="lines",
        name=country_b["r"],
        line=dict(color=PALETTE["olive"], width=2.2, dash="solid"),
        hovertemplate=f"<b>{country_b['r']}</b> %{{x}}<br>%{{y:,.0f}} СЂРѕР¶Рґ.<extra></extra>",
    )
)
fig_cmp.add_vline(
    x=year,
    line=dict(color=PALETTE["ink"], width=1, dash="dot"),
    opacity=0.45,
)
fig_cmp.update_layout(
    paper_bgcolor=PALETTE["paper"],
    plot_bgcolor=PALETTE["paper"],
    height=340,
    margin=dict(l=20, r=20, t=20, b=30),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family="JetBrains Mono", color=PALETTE["ink_light"], size=11),
        showline=True,
        linecolor=PALETTE["ink"],
        linewidth=1,
        dtick=10,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="JetBrains Mono", color=PALETTE["ink_light"], size=10),
        title=dict(
            text="Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РІ РіРѕРґ",
            font=dict(family="JetBrains Mono", size=10, color=PALETTE["ink_light"]),
        ),
        rangemode="tozero",
        tickformat=",",
    ),
    legend=dict(
        orientation="h",
        x=0,
        y=1.12,
        font=dict(family="Fraunces", size=12, color=PALETTE["ink"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)
st.plotly_chart(fig_cmp, width="stretch", config={"displayModeBar": False})


# ============================================================================
# РСЃС‚РѕС‡РЅРёРєРё Рё РјРµС‚РѕРґРѕР»РѕРіРёСЏ
# ============================================================================
st.markdown(
    """
    <footer class="footnotes">
        <h3>РСЃС‚РѕС‡РЅРёРєРё Рё РјРµС‚РѕРґРѕР»РѕРіРёСЏ</h3>
        <p>
            <strong>РСЃС‚РѕС‡РЅРёРє.</strong> United Nations, Department of Economic and Social Affairs,
            Population Division (2024). <em>World Population Prospects 2024.</em> Р›РёС†РµРЅР·РёСЏ CC&nbsp;BY&nbsp;3.0&nbsp;IGO.
            РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ РїРѕРєР°Р·Р°С‚РµР»СЊ <em>Births&nbsp;(thousands)</em> вЂ” РѕС†РµРЅРѕС‡РЅРѕРµ С‡РёСЃР»Рѕ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№
            РІ&nbsp;РіРѕРґ РїРѕ&nbsp;РєР°Р¶РґРѕР№ СЃС‚СЂР°РЅРµ (Estimates 1950вЂ“2023 + Medium variant 2024).
        </p>
        <p>
            <strong>РњРµС‚РѕРґ.</strong> РљРѕРіРѕСЂС‚РЅР°СЏ РІРµСЂРѕСЏС‚РЅРѕСЃС‚СЊ РјРµСЃС‚Р° СЂРѕР¶РґРµРЅРёСЏ РІС‹С‡РёСЃР»СЏРµС‚СЃСЏ РєР°Рє
            <em>P(C&nbsp;|&nbsp;Y)&nbsp;=&nbsp;births(C,&nbsp;Y)&nbsp;Г·&nbsp;world_births(Y)</em>:
            РґРѕР»СЏ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РІ СЃС‚СЂР°РЅРµ&nbsp;C СЃСЂРµРґРё РІСЃРµС… Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РјРёСЂР° Р·Р° С‚РѕС‚ Р¶Рµ РіРѕРґ&nbsp;Y.
            Р­С‚Рѕ Р°РїСЂРёРѕСЂРЅР°СЏ РІРµСЂРѕСЏС‚РЅРѕСЃС‚СЊ С‚РѕРіРѕ, С‡С‚Рѕ СЃР»СѓС‡Р°Р№РЅРѕ РІС‹Р±СЂР°РЅРЅС‹Р№ РјР»Р°РґРµРЅРµС† РёР· РіР»РѕР±Р°Р»СЊРЅРѕР№ РєРѕРіРѕСЂС‚С‹
            СЂРѕРґРёР»СЃСЏ РёРјРµРЅРЅРѕ РІ&nbsp;C.
        </p>
        <p>
            <strong>Р“СЂР°РЅРёС†С‹ вЂ” СЃРѕРІСЂРµРјРµРЅРЅС‹Рµ.</strong> РћРћРќ РІ WPP&nbsp;2024 СЂРµС‚СЂРѕСЃРїРµРєС‚РёРІРЅРѕ РїСЂРёРјРµРЅСЏРµС‚
            СЃРѕРІСЂРµРјРµРЅРЅС‹Рµ РіСЂР°РЅРёС†С‹ СЃС‚СЂР°РЅ. РўРѕ&nbsp;РµСЃС‚СЊ В«Р РѕСЃСЃРёСЏ РІ&nbsp;1950В» РѕР·РЅР°С‡Р°РµС‚ С‚РµСЂСЂРёС‚РѕСЂРёСЋ
            СЃРѕРІСЂРµРјРµРЅРЅРѕР№ Р Р¤ (Р РЎР¤РЎР ), Р° РЅРµ РЎРЎРЎР ; В«Р‘Р°РЅРіР»Р°РґРµС€ РІ&nbsp;1960В» вЂ” С‚РµСЂСЂРёС‚РѕСЂРёСЋ СЃРѕРІСЂРµРјРµРЅРЅРѕР№
            Р‘Р°РЅРіР»Р°РґРµС€ (Р’РѕСЃС‚РѕС‡РЅС‹Р№ РџР°РєРёСЃС‚Р°РЅ); В«Р“РµСЂРјР°РЅРёСЏВ» вЂ” РѕР±СЉРµРґРёРЅС‘РЅРЅСѓСЋ С‚РµСЂСЂРёС‚РѕСЂРёСЋ Р¤Р Р“&nbsp;+&nbsp;Р“Р”Р .
        </p>
        <p>
            <strong>РўРѕС‡РЅРѕСЃС‚СЊ.</strong> РћС†РµРЅРєРё РћРћРќ СЃС‚СЂРѕСЏС‚СЃСЏ РјРµС‚РѕРґР°РјРё <em>cohort-component projection</em>
            РЅР° Р±Р°Р·Рµ vital&nbsp;registration, РїРµСЂРµРїРёСЃРµР№ Рё&nbsp;DHS/MICS. Р Р°Р·РІРёС‚С‹Рµ СЃС‚СЂР°РЅС‹: В±1вЂ“2%;
            Р±РѕР»СЊС€РёРЅСЃС‚РІРѕ СЂР°Р·РІРёРІР°СЋС‰РёС…СЃСЏ: В±5вЂ“10%; СЃС‚СЂР°РЅС‹ Р·Р°С‚СЏР¶РЅРѕРіРѕ РєСЂРёР·РёСЃР° (РђС„РіР°РЅРёСЃС‚Р°РЅ, РЎРѕРјР°Р»Рё, Р”Р Рљ): В±15вЂ“20%.
        </p>
        <p>
            <strong>Р§С‚Рѕ РЅРµ СѓС‡С‚РµРЅРѕ.</strong> РњР»Р°РґРµРЅС‡РµСЃРєР°СЏ Рё&nbsp;РґРµС‚СЃРєР°СЏ СЃРјРµСЂС‚РЅРѕСЃС‚СЊ (U5MR), РјРёРіСЂР°С†РёСЏ РІ&nbsp;РїРµСЂРІС‹Рµ
            РіРѕРґС‹ Р¶РёР·РЅРё, РёР·РјРµРЅРµРЅРёРµ РіРѕСЃСѓРґР°СЂСЃС‚РІРµРЅРЅС‹С… РіСЂР°РЅРёС†. Р­С‚Рѕ С‡РёСЃС‚Р°СЏ В«Р»РѕС‚РµСЂРµСЏ РјРµСЃС‚Р° СЂРѕР¶РґРµРЅРёСЏВ»
            РЅР°&nbsp;РјРѕРјРµРЅС‚ Р¶РёРІРѕСЂРѕР¶РґРµРЅРёСЏ, Р±РµР· РїРѕРїСЂР°РІРєРё РЅР° РґР°Р»СЊРЅРµР№С€СѓСЋ РІС‹Р¶РёРІР°РµРјРѕСЃС‚СЊ.
        </p>
        <p>
            <strong>РџРѕРєСЂС‹С‚РёРµ.</strong> 211&nbsp;СЃС‚СЂР°РЅ Рё С‚РµСЂСЂРёС‚РѕСЂРёР№, 75&nbsp;Р»РµС‚ (1950вЂ“2024),
            в‰€&nbsp;15&nbsp;800&nbsp;С‚РѕС‡РµРє РґР°РЅРЅС‹С…. РњР°Р»С‹Рµ С‚РµСЂСЂРёС‚РѕСЂРёРё СЃ&nbsp;РїРёРєРѕРІС‹РјРё
            &lt;&nbsp;1&nbsp;000&nbsp;Р¶РёРІРѕСЂРѕР¶РґРµРЅРёР№ РІ&nbsp;РіРѕРґ (Р’Р°С‚РёРєР°РЅ, РўРѕРєРµР»Р°Сѓ, РџРёС‚РєСЌСЂРЅ)
            РёСЃРєР»СЋС‡РµРЅС‹ РєР°Рє СЃС‚Р°С‚РёСЃС‚РёС‡РµСЃРєРё С€СѓРјРЅС‹Рµ.
        </p>
    </footer>
    """,
    unsafe_allow_html=True,
)
