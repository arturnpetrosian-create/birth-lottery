"""
streamlit_app.py
────────────────
«Лотерея рождения» — демографический атлас когорт живорождений по странам,
1950–2024.

Источник:
    United Nations, Department of Economic and Social Affairs,
    Population Division (2024). World Population Prospects 2024.
    Лицензия CC BY 3.0 IGO.

Запуск локально:
    streamlit run app/streamlit_app.py

Деплой:
    Streamlit Community Cloud → main file path: app/streamlit_app.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================================
# Конфигурация страницы
# ============================================================================
st.set_page_config(
    page_title="Лотерея рождения · Демографический атлас",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": (
            "Демографический атлас когортных вероятностей рождения "
            "по данным UN World Population Prospects 2024."
        ),
    },
)

# ============================================================================
# Палитра и типографика — синхронизированы со static/index.html
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

# Логарифмическая шкала «доли в мировой когорте новорождённых»
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

    /* ── masthead ────────────────────────────────────────────────────── */
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

    /* ── hero ────────────────────────────────────────────────────────── */
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

    /* ── eyebrows / section headings ────────────────────────────────── */
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

    /* ── result block ───────────────────────────────────────────────── */
    .result-block {{
        text-align: center;
        border-top: 1px solid {PALETTE['ink']};
        border-bottom: 1px solid {PALETTE['ink']};
        padding: 44px 20px 52px;
        margin: 12px 0 56px 0;
        position: relative;
    }}
    .result-block::before, .result-block::after {{
        content: "❦";
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

    /* ── контролы (year + country) ──────────────────────────────────── */
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

    /* ── метрики ─────────────────────────────────────────────────────── */
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

    /* ── horizontal rule ─────────────────────────────────────────────── */
    hr {{
        border: none;
        border-top: 1px solid {PALETTE['paper_darker']};
        margin: 36px 0;
    }}

    /* ── footnotes ───────────────────────────────────────────────────── */
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

    /* ── streamlit chrome cleanup ───────────────────────────────────── */
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
# Загрузка данных
# ============================================================================
ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "births_compact.json"


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, Any]:
    if not DATA_PATH.exists():
        st.error(
            f"Не найден датасет: `{DATA_PATH}`.\n\n"
            "Запустите `python scripts/build_data.py`, чтобы построить "
            "`births_compact.json` из исходного xlsx UN WPP 2024."
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
    """Живорождения в стране за год, тысячи."""
    return COUNTRIES[iso]["b"][year - YEAR_MIN]


def world_births_k(year: int) -> float:
    return WORLD[year - YEAR_MIN]


def share_pct(iso: str, year: int) -> float:
    w = world_births_k(year)
    return (births_k(iso, year) / w * 100) if w > 0 else 0.0


def fmt_int(n: float) -> str:
    """Форматирование числа в стиле «1 234 567»."""
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
    """
    <header class="masthead">
        <div class="masthead-left">Демографический Атлас № 1 ※ Выпуск 2026</div>
        <div class="masthead-right">по данным United Nations · World Population Prospects 2024</div>
    </header>

    <section>
        <div class="hero-eyebrow">Когортные вероятности рождения</div>
        <h1 class="hero-h1">Какова была вероятность<br><em>родиться</em> именно здесь<br>именно тогда?</h1>
        <p class="hero-sub">
            Каждый год Земля принимает около 130&nbsp;миллионов живорождений. Этот атлас раскладывает
            мировую когорту новорождённых на страны и годы и показывает удельный вес каждой ячейки —
            то есть априорную вероятность того, что случайно выбранный младенец родился именно
            в&nbsp;выбранной стране в&nbsp;выбранном году.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# КОНТРОЛЫ — год и страна
# ============================================================================
sorted_countries = sorted(COUNTRIES.items(), key=lambda kv: kv[1]["r"])
ISO_OPTIONS = [iso for iso, _ in sorted_countries]
LABEL_FOR = {iso: c["r"] for iso, c in sorted_countries}
ISO_TO_REGION = {iso: c["g"] for iso, c in COUNTRIES.items()}
REGIONS = sorted({c["g"] for c in COUNTRIES.values()})

col_yr, col_co = st.columns([1, 1], gap="large")
with col_yr:
    year = st.slider(
        "ГОД РОЖДЕНИЯ (КАЛЕНДАРНАЯ КОГОРТА)",
        min_value=YEAR_MIN,
        max_value=YEAR_MAX,
        value=1992,
        step=1,
        help=(
            "Календарный год, по которому считается доля живорождений в "
            "глобальной когорте новорождённых."
        ),
    )
with col_co:
    default_iso = "RUS" if "RUS" in ISO_OPTIONS else ISO_OPTIONS[0]
    iso = st.selectbox(
        "СТРАНА (СОВРЕМЕННЫЕ ГРАНИЦЫ ООН)",
        options=ISO_OPTIONS,
        index=ISO_OPTIONS.index(default_iso),
        format_func=lambda x: LABEL_FOR[x],
        help=(
            "ООН WPP 2024 ретроспективно применяет современные границы: "
            "«Россия в 1950» означает территорию РСФСР, не СССР."
        ),
    )


# ============================================================================
# Главный результат
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
        <div class="result-label">Доля в мировой когорте новорождённых · {year}</div>
        <div class="result-big">{fmt_pct(pct)}<span class="pct-sign">%</span></div>
        <div class="result-secondary">примерно <strong>1 из {fmt_int(one_in)}</strong> новорождённых того года</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# § I · КАРТА МИРА
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">§ I · Пространственное распределение когорты</div>
    <h2 class="section-title">Где рождались люди в&nbsp;<em>{year}</em>&nbsp;году</h2>
    <p class="caption">
        Цвет показывает удельный вес страны в мировой когорте живорождений по логарифмической шкале.
        Темнее — выше доля. Под тёплыми оттенками скрыты крупнейшие центры воспроизводства;
        бледный фон — страны с малым числом рождений или, реже, отсутствующие в датасете.
    </p>
    """,
    unsafe_allow_html=True,
)


def color_for_pct(p: float) -> str:
    """Логарифмическая интерполяция между опорными цветами."""
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

fig_map = go.Figure()

# Базовый слой — все страны через choropleth с custom-палитрой
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
                text="доля когорты, %",
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
            "доля в мире: %{z:.3f}%<br>"
            "живорождений: %{customdata[1]:,.0f}"
            "<extra></extra>"
        ),
    )
)

# Подсветка выбранной страны
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
# § II · ИЗОТИП — 1000 ТОЧЕК
# ============================================================================
st.markdown(
    """
    <div class="section-eyebrow">§ II · Изотип когорты</div>
    <h2 class="section-title">Из <em>1000</em> младенцев мира того года —<br>столько родились здесь</h2>
    """,
    unsafe_allow_html=True,
)

dots_to_fill = round(pct * 10)  # 1000 точек = 100% × 10
if dots_to_fill == 0:
    isotype_caption = (
        f"Меньше одного младенца из тысячи — точнее, "
        f"{fmt_int(pct * 1000)} из 100 000 новорождённых мира."
    )
elif dots_to_fill > 800:
    isotype_caption = (
        f"{dots_to_fill} из 1000 младенцев мира в {year} году родились в этой стране — "
        "это была демографическая сверхдержава."
    )
else:
    isotype_caption = (
        f"Каждая точка соответствует одному младенцу из тысячи случайно выбранных по миру в {year} году. "
        "Закрашены родившиеся в выбранной стране."
    )
st.markdown(f"<p class='caption'>{isotype_caption}</p>", unsafe_allow_html=True)

ROWS, COLS = 20, 50  # 1000 точек, прямоугольник
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

# Лёгкая легенда
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
            margin-right:8px;vertical-align:-1px;"></span>остальной мир</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# § III · ДЕМОГРАФИЧЕСКИЙ КОНТЕКСТ
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

# Доля в регионе
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
    """
    <div class="section-eyebrow">§ III · Демографический контекст</div>
    <h2 class="section-title">Что означают эти числа</h2>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4, gap="small")
with m1:
    st.metric(
        "Живорождений · ВСЕГО",
        fmt_int(c_births),
        help=f"{country['r']}, {year}. Источник: UN WPP 2024 (Births, thousands).",
    )
with m2:
    per_day = c_births / 365.25
    st.metric(
        "В сутки",
        fmt_int(per_day),
        delta=f"≈ {per_day / 86400:.2f} рожд./сек.",
        delta_color="off",
        help="Среднесуточный темп воспроизводства за выбранный год.",
    )
with m3:
    rank_desc = (
        "входит в пятёрку"
        if rank_position <= 5
        else "в первой десятке"
        if rank_position <= 10
        else "в первой четверти"
        if rank_position <= rank_total // 4
        else "выше медианы"
        if rank_position <= rank_total // 2
        else "ниже медианы"
    )
    st.metric(
        "Место в мире",
        f"{rank_position} из {rank_total}",
        delta=rank_desc,
        delta_color="off",
        help="Ранг страны по абсолютному числу живорождений среди всех стран датасета.",
    )
with m4:
    st.metric(
        f"Доля в регионе ({region})",
        f"{share_in_region:.1f}%",
        delta=f"{fmt_int(region_total_k * 1000)} рожд. в регионе",
        delta_color="off",
        help=(
            "Удельный вес страны в живорождениях своего макрорегиона (UN geoscheme: "
            "Africa / Asia / Europe / Americas / Oceania)."
        ),
    )

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# § IV · ТОП СТРАН (ГОРИЗОНТАЛЬНАЯ ГИСТОГРАММА)
# ============================================================================
st.markdown(
    """
    <div class="section-eyebrow">§ IV · Структура мировой когорты</div>
    <h2 class="section-title">Где рождалось <em>больше всего</em> людей<br>в выбранный год</h2>
    <p class="caption">
        Топ-12 стран по абсолютному числу живорождений плюс выбранная страна
        (если она вне топа). На столько процентов мировой когорты приходится
        на каждую территорию.
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
            "<b>%{y}</b><br>%{x:.3f}% мировой когорты"
            "<br>%{customdata:,.0f} живорождений<extra></extra>"
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
# § V · ДИНАМИКА (TIMELINE)
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">§ V · Когортная динамика</div>
    <h2 class="section-title">
        Кривая живорождений в&nbsp;<em>{country['r']}</em>,<br>
        от <em>{YEAR_MIN}</em> до <em>{YEAR_MAX}</em>
    </h2>
    <p class="caption">
        Абсолютное число живорождений по годам. Точка — выбранный вами год.
        В развитых экономиках хорошо видны первая (1950–60-е) и вторая (1980-е, эхо)
        послевоенные демографические волны; в развивающихся — поздний демографический переход
        с пиком рождаемости в 1980–2000-х.
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

# 5-летнее скользящее среднее как «тренд»
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
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} живорождений<extra></extra>",
        name="живорождения",
    )
)
fig_line.add_trace(
    go.Scatter(
        x=trend_df["year"],
        y=trend_df["smooth"],
        mode="lines",
        line=dict(color=PALETTE["ink"], width=1.0, dash="dot"),
        hoverinfo="skip",
        name="5-летнее сглаживание",
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
        hovertemplate=f"<b>{year}</b><br>{fmt_int(c_births)} живорождений<extra></extra>",
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
            text="живорождений в год",
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
# § VI · СРАВНЕНИЕ КОГОРТ
# ============================================================================
st.markdown(
    """
    <div class="section-eyebrow">§ VI · Сравнение когорт</div>
    <h2 class="section-title">Сопоставление двух траекторий</h2>
    <p class="caption">
        Демографическая компаративистика: положите две страновые траектории живорождений
        на одну ось — и за пару секунд читаются эпохи демографических переходов,
        войны, бэби-бумы, пост-советские «провалы» и «эхо-волны».
    </p>
    """,
    unsafe_allow_html=True,
)

cmp_default = "USA" if "USA" in ISO_OPTIONS and iso != "USA" else (
    "DEU" if "DEU" in ISO_OPTIONS else ISO_OPTIONS[0]
)
iso_b = st.selectbox(
    "СТРАНА ДЛЯ СРАВНЕНИЯ",
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
        hovertemplate=f"<b>{country['r']}</b> %{{x}}<br>%{{y:,.0f}} рожд.<extra></extra>",
    )
)
fig_cmp.add_trace(
    go.Scatter(
        x=years_full,
        y=[v * 1000 for v in country_b["b"]],
        mode="lines",
        name=country_b["r"],
        line=dict(color=PALETTE["olive"], width=2.2, dash="solid"),
        hovertemplate=f"<b>{country_b['r']}</b> %{{x}}<br>%{{y:,.0f}} рожд.<extra></extra>",
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
            text="живорождений в год",
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
# Источники и методология
# ============================================================================
st.markdown(
    """
    <footer class="footnotes">
        <h3>Источники и методология</h3>
        <p>
            <strong>Источник.</strong> United Nations, Department of Economic and Social Affairs,
            Population Division (2024). <em>World Population Prospects 2024.</em> Лицензия CC&nbsp;BY&nbsp;3.0&nbsp;IGO.
            Используется показатель <em>Births&nbsp;(thousands)</em> — оценочное число живорождений
            в&nbsp;год по&nbsp;каждой стране (Estimates 1950–2023 + Medium variant 2024).
        </p>
        <p>
            <strong>Метод.</strong> Когортная вероятность места рождения вычисляется как
            <em>P(C&nbsp;|&nbsp;Y)&nbsp;=&nbsp;births(C,&nbsp;Y)&nbsp;÷&nbsp;world_births(Y)</em>:
            доля живорождений в стране&nbsp;C среди всех живорождений мира за тот же год&nbsp;Y.
            Это априорная вероятность того, что случайно выбранный младенец из глобальной когорты
            родился именно в&nbsp;C.
        </p>
        <p>
            <strong>Границы — современные.</strong> ООН в WPP&nbsp;2024 ретроспективно применяет
            современные границы стран. То&nbsp;есть «Россия в&nbsp;1950» означает территорию
            современной РФ (РСФСР), а не СССР; «Бангладеш в&nbsp;1960» — территорию современной
            Бангладеш (Восточный Пакистан); «Германия» — объединённую территорию ФРГ&nbsp;+&nbsp;ГДР.
        </p>
        <p>
            <strong>Точность.</strong> Оценки ООН строятся методами <em>cohort-component projection</em>
            на базе vital&nbsp;registration, переписей и&nbsp;DHS/MICS. Развитые страны: ±1–2%;
            большинство развивающихся: ±5–10%; страны затяжного кризиса (Афганистан, Сомали, ДРК): ±15–20%.
        </p>
        <p>
            <strong>Что не учтено.</strong> Младенческая и&nbsp;детская смертность (U5MR), миграция в&nbsp;первые
            годы жизни, изменение государственных границ. Это чистая «лотерея места рождения»
            на&nbsp;момент живорождения, без поправки на дальнейшую выживаемость.
        </p>
        <p>
            <strong>Покрытие.</strong> 211&nbsp;стран и территорий, 75&nbsp;лет (1950–2024),
            ≈&nbsp;15&nbsp;800&nbsp;точек данных. Малые территории с&nbsp;пиковыми
            &lt;&nbsp;1&nbsp;000&nbsp;живорождений в&nbsp;год (Ватикан, Токелау, Питкэрн)
            исключены как статистически шумные.
        </p>
    </footer>
    """,
    unsafe_allow_html=True,
)
