"""
streamlit_app.py
────────────────
«Лотерея рождения» — атлас долей рождений по странам и годам,
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
import sys
from pathlib import Path
from typing import Any


def _ensure_repo_root_on_path() -> None:
    """Streamlit Cloud запускает `app/streamlit_app.py`; пакет `domain` лежит в корне репозитория."""
    here = Path(__file__).resolve()
    candidates = (
        here.parent.parent,
        here.parent,
        Path.cwd(),
    )
    for c in candidates:
        try:
            if (c / "domain" / "prb_ever_lived.py").is_file():
                root = str(c.resolve())
                if root not in sys.path:
                    sys.path.insert(0, root)
                return
        except OSError:
            continue
    sys.path.insert(0, str(here.parent.parent))


_ensure_repo_root_on_path()

import pandas as pd  # noqa: E402
from domain.prb_ever_lived import (  # noqa: E402
    EVER_LIVED_PRB_2022,
    PRB_ARTICLE_URL,
    format_tiny_percent,
    one_in_reciprocal,
    share_of_prb_total,
)

# Ссылки для раздела § VI — в streamlit-приложении, чтобы деплой не зависел от рассинхрона кэша `domain` на Cloud.
PRB_READINGS_RU: tuple[tuple[str, str], ...] = (
    (
        "Kaneda & Haub (PRB, 2022): сколько людей когда-либо родилось",
        PRB_ARTICLE_URL,
    ),
    (
        "Our World in Data: рождаемость и численность (данные и графики)",
        "https://ourworldindata.org/births",
    ),
    (
        "ООН, World Population Prospects: методология оценок",
        "https://population.un.org/wpp/Methodology/",
    ),
    (
        "BBC Future (English): how many people have ever lived",
        "https://www.bbc.com/future/article/20190311-how-many-people-have-ever-lived-on-earth",
    ),
)

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

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
            "Атлас долей рождений по странам по данным "
            "UN World Population Prospects 2024."
        ),
    },
)

# ============================================================================
# Палитра и типографика — синхронизированы со static/index.html
# ============================================================================
PALETTE = {
    "paper":        "#f4f4f2",
    "paper_dark":   "#e8e8e5",
    "paper_darker": "#d4d4cf",
    "ink":          "#1c1c1c",
    "ink_soft":     "#5a5a57",
    "ink_light":    "#666663",
    "terracotta":   "#3d5a6c",
    "terracotta_d": "#2c4250",
    "terracotta_dd": "#1e2f3a",
    "ochre":        "#6b7d85",
    "olive":        "#5a7268",
    "water":        "#e2e4e6",
}

# Логарифмическая шкала доли страны в мировом объёме рождений за год
COLOR_STOPS = [
    (0.0,   PALETTE["paper"]),
    (0.05,  "#e4e8ea"),
    (0.20,  "#c5d0d6"),
    (1.0,   "#89a7b5"),
    (5.0,   PALETTE["terracotta"]),
    (15.0,  PALETTE["terracotta_d"]),
    (25.0,  PALETTE["terracotta_dd"]),
]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"]  {{
        font-family: 'IBM Plex Sans', system-ui, sans-serif;
        color: {PALETTE['ink']};
    }}

    .stApp {{
        background: {PALETTE['paper']};
    }}
    .block-container {{
        max-width: 1180px !important;
        padding-top: 2.4rem;
        padding-bottom: 5rem;
    }}

    /* ── masthead ────────────────────────────────────────────────────── */
    .masthead {{
        border-top: 1px solid {PALETTE['ink']};
        border-bottom: 1px solid {PALETTE['ink']};
        padding: 14px 0;
        margin-bottom: 48px;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {PALETTE['ink_soft']};
    }}
    .masthead-left {{ font-weight: 600; }}
    .masthead-right {{ font-style: normal; text-transform: none; letter-spacing: 0.04em; }}

    /* ── hero ────────────────────────────────────────────────────────── */
    .hero-eyebrow {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.18em;
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
        font-family: 'IBM Plex Sans', system-ui, sans-serif;
        font-size: clamp(2.1rem, 5.2vw, 4.2rem);
        line-height: 1.05;
        letter-spacing: -0.03em;
        margin: 0 0 22px 0;
        font-weight: 500;
        color: {PALETTE['ink']};
    }}
    .hero-h1 em {{
        font-style: normal;
        font-weight: 600;
        color: {PALETTE['terracotta_d']};
    }}
    .hero-sub {{
        font-size: 1.05rem;
        color: {PALETTE['ink_soft']};
        max-width: 640px;
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 36px;
    }}

    /* ── eyebrows / section headings ────────────────────────────────── */
    .section-eyebrow {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.2em;
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
        font-family: 'IBM Plex Sans', system-ui, sans-serif;
        font-size: 1.75rem;
        line-height: 1.18;
        margin: 0 0 22px 0;
        letter-spacing: -0.02em;
        font-weight: 500;
        color: {PALETTE['ink']};
    }}
    .section-title em {{ font-style: normal; font-weight: 600; color: {PALETTE['terracotta_d']}; }}
    .caption {{
        font-size: 0.95rem;
        color: {PALETTE['ink_soft']};
        font-weight: 400;
        margin: 0 0 20px 0;
        max-width: 680px;
        line-height: 1.55;
    }}

    /* ── result block ───────────────────────────────────────────────── */
    .result-block {{
        text-align: center;
        border-top: 1px solid {PALETTE['ink']};
        border-bottom: 1px solid {PALETTE['ink']};
        padding: 40px 20px 48px;
        margin: 12px 0 56px 0;
        position: relative;
    }}
    .result-label {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: {PALETTE['ink_light']};
        margin-bottom: 18px;
    }}
    .result-main {{
        font-family: 'IBM Plex Sans', system-ui, sans-serif;
        font-size: clamp(1.2rem, 3.2vw, 1.85rem);
        line-height: 1.35;
        font-weight: 500;
        color: {PALETTE['ink']};
        font-variant-numeric: tabular-nums;
    }}
    .result-big {{
        font-family: 'IBM Plex Sans', system-ui, sans-serif;
        font-size: clamp(3rem, 10vw, 6.5rem);
        line-height: 0.95;
        letter-spacing: -0.04em;
        font-weight: 300;
        font-variant-numeric: tabular-nums lining-nums;
        color: {PALETTE['ink']};
    }}
    .result-big .pct-sign {{
        color: {PALETTE['terracotta']};
        font-weight: 500;
        font-size: 0.7em;
        vertical-align: 0.05em;
    }}
    .result-secondary {{
        font-family: 'IBM Plex Sans', system-ui, sans-serif;
        font-size: 1.15rem;
        color: {PALETTE['ink_soft']};
        margin-top: 4px;
    }}
    .result-secondary strong {{
        font-weight: 600;
        color: {PALETTE['ink']};
    }}

    /* ── контролы (year + country) ──────────────────────────────────── */
    div[data-testid="stSlider"] label,
    div[data-testid="stSelectbox"] label {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.15em;
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
        font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        color: {PALETTE['ink']} !important;
    }}

    /* ── метрики ─────────────────────────────────────────────────────── */
    div[data-testid="stMetric"] {{
        background: {PALETTE['paper']};
        padding: 24px 22px;
        border: 1px solid {PALETTE['ink_light']};
    }}
    div[data-testid="stMetricLabel"] {{
        font-family: 'IBM Plex Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 10px !important;
        color: {PALETTE['ink_light']} !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
        font-size: 1.85rem !important;
        font-weight: 600 !important;
        color: {PALETTE['ink']} !important;
        font-variant-numeric: tabular-nums;
    }}
    div[data-testid="stMetricDelta"] {{
        font-family: 'IBM Plex Mono', monospace !important;
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
        border-top: 1px solid {PALETTE['ink']};
        padding-top: 28px;
        margin-top: 64px;
        font-size: 0.9rem;
        color: {PALETTE['ink_soft']};
        font-weight: 400;
        line-height: 1.65;
    }}
    .footnotes h3 {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: {PALETTE['terracotta']};
        margin-bottom: 12px;
    }}
    .footnotes p {{ margin-bottom: 12px; }}
    .footnotes strong {{ color: {PALETTE['ink']}; font-weight: 600; }}

    /* ── streamlit chrome cleanup ───────────────────────────────────── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    div[data-testid="stToolbar"] {{
        display: none !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# Загрузка данных
# ============================================================================
ROOT = Path(__file__).resolve().parent.parent
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
HISTORICAL: dict[str, Any] | None = DATA.get("historical_ever_born")
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


def fmt_share_among_all(p: float) -> str:
    """Доля 0…1 среди всех родившихся — в процентах, до 3 значащих цифр."""
    x = p * 100.0
    return f"{x:.3g}".replace(".", ",")


# ============================================================================
# MASTHEAD + HERO
# ============================================================================
st.markdown(
    """
    <section>
        <div class="hero-eyebrow">Условные вероятности по стране и году</div>
        <h1 class="hero-h1">Насколько вероятно было<br><em>родиться здесь</em><br>в выбранный год?</h1>
        <p class="hero-sub">
            Источник — <strong>ООН, World Population Prospects&nbsp;2024</strong>: для каждой страны и года
            дана оценка числа рождений (в таблице это <em>Births</em> / live births: дети с признаками жизни;
            мёртворождённые не включаются). Мировой итог от года к году заметно меняется: в окне 1950–2024
            обычно ~92–143&nbsp;млн рождений в год (в 2020‑е — порядка 130&nbsp;млн). Ниже для пары
            «страна + календарный год» показана <strong>доля рождений на территории этой страны в мировом
            итоге за тот же год</strong>. «Лотерея» — образ: мы не считаем «равные шансы родиться в любой
            стране», а задаём <strong>мысленный эксперимент</strong> — равновероятно выбрать одного
            новорождённого из мировой когорты этого года; тогда доля совпадает с
            <em>P</em>(страна&nbsp;|&nbsp;год), а не с ответом на «какова была моя личная вероятность
            родиться», что для уже живущего человека формулируется иначе.
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
        "ГОД РОЖДЕНИЯ",
        min_value=YEAR_MIN,
        max_value=YEAR_MAX,
        value=1992,
        step=1,
        help=(
            "Календарный год: доля рождений в стране в сумме рождений по миру за тот же год."
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
            "Оценки WPP строят как согласованные ряды по странам с 1950 г.; "
            "подробности территориальной базы см. в docs/METHODOLOGY.md."
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
        <div class="result-label">Доля страны в мировом итоге рождений · {year}</div>
        <div class="result-big">{fmt_pct(pct)}<span class="pct-sign">%</span></div>
        <div class="result-secondary">примерно <strong>1 из {fmt_int(one_in)}</strong> рождённых в мире в этом году</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# § I · КАРТА МИРА
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">01 · Карта</div>
    <h2 class="section-title">Распределение рождений по странам в&nbsp;<em>{year}</em>&nbsp;году</h2>
    <p class="caption">
        Насыщенность заливки — доля рождений на территории страны в мировом итоге за этот год (логарифмическая шкала по доле).
        Темнее — большая доля. Светлый фон — очень малые значения (ниже ~0,01%) либо нет данных в наборе.
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
            [0.05, "#e4e8ea"],
            [0.20, "#c5d0d6"],
            [0.45, "#89a7b5"],
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
                text="доля от мира, %",
                font=dict(family="IBM Plex Mono", size=10, color=PALETTE["ink_soft"]),
            ),
            tickfont=dict(family="IBM Plex Mono", size=10, color=PALETTE["ink_soft"]),
            thickness=10,
            len=0.55,
            outlinewidth=0,
            ticksuffix="%",
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "доля в мире: %{z:.3f}%<br>"
            "рождений: %{customdata[1]:,.0f}"
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
    lataxis_gridcolor="rgba(28,28,28,0.08)",
    lonaxis_gridcolor="rgba(28,28,28,0.08)",
    lataxis_gridwidth=0.4,
    lonaxis_gridwidth=0.4,
)
fig_map.update_layout(
    paper_bgcolor=PALETTE["paper"],
    plot_bgcolor=PALETTE["paper"],
    margin=dict(l=0, r=0, t=0, b=0),
    height=520,
    font=dict(family="IBM Plex Sans", color=PALETTE["ink"]),
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
    <div class="section-eyebrow">02 · Изотип</div>
    <h2 class="section-title">Тысяча «билетов» из мировой когорты года:<br>
    <em>сколько из них соответствует выбранной стране</em></h2>
    """,
    unsafe_allow_html=True,
)

dots_to_fill = round(pct * 10)  # 1000 точек = 100% × 10
if dots_to_fill == 0:
    isotype_caption = (
        f"Доля настолько мала, что в сетке из 1000 условных позиций закрашивать нечего; по числу это "
        f"порядка {fmt_int(pct * 1000)} на 100&nbsp;000 рождений в мире за {year} год (оценка WPP)."
    )
elif dots_to_fill > 800:
    isotype_caption = (
        f"Из тысячи условных позиций {dots_to_fill} отнесены к выбранной стране — это очень большая доля "
        f"в мировом итоге рождений за {year} год."
    )
else:
    isotype_caption = (
        f"Как читать: мы сконструировали 1000 равновероятных исходов «кто родился в мире в {year} году». "
        f"Каждая точка — один такой исход; закрашены те, что по данным ООН приходятся на выбранную страну."
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
    margin=dict(l=32, r=32, t=28, b=28),
    height=260,
    xaxis=dict(visible=False, range=[-1, COLS], scaleanchor="y", scaleratio=1),
    yaxis=dict(visible=False, range=[ROWS, -1]),
    showlegend=False,
)
st.plotly_chart(fig_iso, width="stretch", config={"displayModeBar": False})

# Лёгкая легенда
st.markdown(
    f"""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
        text-transform:uppercase;letter-spacing:0.08em;color:{PALETTE['ink_soft']};
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
    <div class="section-eyebrow">03 · Контекст</div>
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
        help="Ранг по абсолютному числу рождений за год среди всех стран датасета.",
    )
with m4:
    st.metric(
        f"Доля в регионе ({region})",
        f"{share_in_region:.1f}%",
        delta=f"{fmt_int(region_total_k * 1000)} рожд. в регионе",
        delta_color="off",
        help=(
            "Удельный вес страны в рождениях своего макрорегиона (UN geoscheme: "
            "Africa / Asia / Europe / Americas / Oceania)."
        ),
    )

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# § IV · ТОП СТРАН (ГОРИЗОНТАЛЬНАЯ ГИСТОГРАММА)
# ============================================================================
st.markdown(
    """
    <div class="section-eyebrow">04 · Рейтинг стран</div>
    <h2 class="section-title">Страны с наибольшим числом рождений<br>в выбранный год</h2>
    <p class="caption">
        Двенадцать стран с максимальным объёмом рождений и выбранная вами, если её нет в списке.
        Подпись у столбца — процент мирового итога за этот год; слева — место в рейтинге и страна.
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
        textfont=dict(family="IBM Plex Mono", color=PALETTE["ink_soft"], size=11),
        hovertemplate=(
            "<b>%{y}</b><br>%{x:.3f}% мирового итога года"
            "<br>%{customdata:,.0f} рожд.<extra></extra>"
        ),
        customdata=bar_df["births"],
        cliponaxis=False,
    )
)
fig_bar.update_layout(
    paper_bgcolor=PALETTE["paper"],
    plot_bgcolor=PALETTE["paper"],
    height=max(360, 38 * len(bar_df)),
    margin=dict(l=12, r=104, t=20, b=28),
    yaxis=dict(
        autorange="reversed",
        automargin=True,
        tickfont=dict(family="IBM Plex Sans", color=PALETTE["ink"], size=13),
        showgrid=False,
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="IBM Plex Mono", color=PALETTE["ink_light"], size=10),
        ticksuffix="%",
        zeroline=False,
    ),
    font=dict(family="IBM Plex Sans"),
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
    <div class="section-eyebrow">05 · Динамика</div>
    <h2 class="section-title">
        Число рождений в&nbsp;<em>{country['r']}</em>,<br>
        <em>{YEAR_MIN}</em>—<em>{YEAR_MAX}</em>
    </h2>
    <p class="caption">
        Абсолютные значения по годам. Маркер — выбранный год. Пунктир — сглаженный ряд (окно 5 лет).
        На кривых типичны послевоенные пики в индустриальных странах и более поздний пик рождаемости
        в странах с поздним демографическим переходом.
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
        fillcolor="rgba(61,90,108,0.18)",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} рождений<extra></extra>",
        name="годовой ряд (рожд.)",
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
        textfont=dict(family="IBM Plex Sans", color=PALETTE["ink"], size=14),
        showlegend=False,
        hovertemplate=f"<b>{year}</b><br>{fmt_int(c_births)} рождений<extra></extra>",
    )
)
fig_line.update_layout(
    paper_bgcolor=PALETTE["paper"],
    plot_bgcolor=PALETTE["paper"],
    height=340,
    margin=dict(l=56, r=28, t=56, b=34),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family="IBM Plex Mono", color=PALETTE["ink_light"], size=11),
        showline=True,
        linecolor=PALETTE["ink"],
        linewidth=1,
        dtick=10,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="IBM Plex Mono", color=PALETTE["ink_light"], size=10),
        title=dict(
            text="число рождений в год",
            font=dict(family="IBM Plex Mono", size=10, color=PALETTE["ink_light"]),
        ),
        rangemode="tozero",
        tickformat=",",
    ),
    legend=dict(
        orientation="h",
        x=0,
        y=1.12,
        font=dict(family="IBM Plex Mono", size=10, color=PALETTE["ink_soft"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)
st.plotly_chart(fig_line, width="stretch", config={"displayModeBar": False})


# ============================================================================
# Сравнение двух стран
# ============================================================================
st.markdown(
    """
    <div class="section-eyebrow">06 · Сравнение</div>
    <h2 class="section-title">Две страны на одной временной шкале</h2>
    <p class="caption">
        Сопоставление годовых объёмов рождений: фазы демографического перехода,
        кризисы, восстановительные всплески рождаемости.
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
    margin=dict(l=56, r=28, t=56, b=34),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family="IBM Plex Mono", color=PALETTE["ink_light"], size=11),
        showline=True,
        linecolor=PALETTE["ink"],
        linewidth=1,
        dtick=10,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="IBM Plex Mono", color=PALETTE["ink_light"], size=10),
        title=dict(
            text="число рождений в год",
            font=dict(family="IBM Plex Mono", size=10, color=PALETTE["ink_light"]),
        ),
        rangemode="tozero",
        tickformat=",",
    ),
    legend=dict(
        orientation="h",
        x=0,
        y=1.12,
        font=dict(family="IBM Plex Sans", size=12, color=PALETTE["ink"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)
st.plotly_chart(fig_cmp, width="stretch", config={"displayModeBar": False})


# ============================================================================
# § VI · PRB ~117 млрд — ваша доля среди всех когда-либо родившихся (оценка)
# ============================================================================
_pop_k = float(META.get("world_population_july_2024_thousands", 8120.0 * 1000.0))
_alive_share = (_pop_k * 1000.0) / float(EVER_LIVED_PRB_2022)
_sum_world_births_cohort = float(
    META.get("world_births_sum_1950_2024_persons", sum(WORLD) * 1000.0),
)
_share_wpp_window_in_prb = _sum_world_births_cohort / float(EVER_LIVED_PRB_2022)
_births_c_country_window = sum(float(x) for x in country["b"]) * 1000.0
_share_country_in_prb = _births_c_country_window / float(EVER_LIVED_PRB_2022)
_p_you_prb = share_of_prb_total(float(c_births))
_recip_prb = one_in_reciprocal(_p_you_prb)
_share_year_world_in_prb = float(w_births) / float(EVER_LIVED_PRB_2022)

st.markdown(
    """
    <div class="section-eyebrow">§ VI · Среди всех, кто когда-либо рождался</div>
    <h2 class="section-title">Оценка PRB: с появления <em>Homo sapiens</em> родилось порядка
    117&nbsp;млрд человек</h2>
    <p class="caption">
        Здесь другой масштаб, чем в блоках выше: не доля страны в <em>мировом</em> годе, а доля
        <strong>числа рождений в выбранной стране и календарном годе</strong> (оценка ООН WPP)
        в совокупной модели всех рождений за историю по PRB (Kaneda&nbsp;&amp;&nbsp;Haub, 2022).
        Это модельный счётчик с большой неопределённостью (у PRB — порядка ±20–30&nbsp;%);
        117&nbsp;млрд — именно <strong>рождения</strong>, а не «все, кто жил одновременно».
    </p>
    """,
    unsafe_allow_html=True,
)
_recip_line = (
    fmt_int(int(round(_recip_prb)))
    if 0 < _recip_prb < float("inf")
    else "—"
)
st.markdown(
    f"""
    <div class="result-block">
        <div class="result-label">Оценка PRB (~117 млрд рождений) · {country['r']}, {year}</div>
        <div class="result-main">
            Около <strong>{format_tiny_percent(_p_you_prb)}&nbsp;%</strong> от совокупного числа рождений
            в этой реконструкции.
        </div>
        <div class="result-secondary" style="margin-top:10px;font-size:0.95rem;">
            Иначе говоря, при <em>мысленном</em> равновероятном выборе одного рождения из пула PRB
            масштаб «один к
            <strong>{_recip_line}</strong>» по порядку величины совпадает с этой долей
            (речь не о личной «судьбе», а об удобной интерпретации очень малой вероятности).
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(
        f"Все рожд. в {year} ({country['r']})",
        f"{format_tiny_percent(_p_you_prb)}%",
        help="births(C,Y)·1000 / 117e9",
    )
    st.caption("доля от 117 млрд (PRB)")
with c2:
    st.metric(
        f"Сумма рожд. {country['r']}, 1950–2024",
        f"{format_tiny_percent(_share_country_in_prb)}%",
        help="Сумма yearly births в датасете ×1000 / 117e9",
    )
    st.caption("только окно ООН WPP в приложении")
with c3:
    st.metric(
        "Живущие сейчас (оценка WPP 2024)",
        f"{_alive_share*100:.1f}%",
        help="Оценка численности «World» 1 июля 2024 из метаданных JSON (если есть) / 117e9",
    )
    st.caption(f"~{_pop_k*1000/1e9:.2f} млрд чел.; для сравнения PRB в статье ~8 млрд / 117 млрд ≈ 6,8–7%")

st.caption(
    f"Пулы для контекста: сумма годовых рождений по миру за 1950–2024 в этом приложении ≈ "
    f"{_share_wpp_window_in_prb*100:.1f}% от 117 млрд (PRB); "
    f"год {year} (мир) ≈ {_share_year_world_in_prb*100:.2f}% от 117 млрд (PRB)."
)
_readings_html = "".join(
    f'<li style="margin:0.35em 0;"><a href="{url}" rel="noopener noreferrer">{title}</a></li>'
    for title, url in PRB_READINGS_RU
)
st.markdown(
    f"""
    <p class="caption" style="font-size:0.88rem;margin-top:20px;">
        <strong>Источник оценки 117 млрд:</strong>
        <a href="{PRB_ARTICLE_URL}" rel="noopener noreferrer">Toshiko Kaneda &amp; Carl Haub,
        «How Many People Have Ever Lived on Earth?»</a>, Population Reference Bureau, 2022.
        Погрешность порядка ±20–30&nbsp;% по самой PRB; модель 190&nbsp;000 г. до н.э. — сер. 2022.
    </p>
    <p class="caption" style="font-size:0.88rem;margin-top:12px;">
        <strong>Читать по теме</strong> (оценки населения и рождаемости, условные вероятности):
    </p>
    <ul style="font-size:0.88rem;color:{PALETTE["ink_soft"]};margin:0.2em 0 0 1.2em;padding:0;">
        {_readings_html}
    </ul>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# Доля года среди всех когда-либо родившихся
# ============================================================================
if HISTORICAL is None:
    st.info(
        "Блок «доля года среди всех родившихся» появится после пересборки датасета: "
        "`python scripts/build_data.py` в каталоге проекта."
    )
else:
    pct_blocks = HISTORICAL["pct_year"]
    p_lo = pct_blocks["low"]
    p_mid = pct_blocks["central"]
    p_hi = pct_blocks["high"]
    yi = year - YEAR_MIN
    tot = HISTORICAL["total_ever_born_persons"]
    share_un = float(HISTORICAL["share_of_all_births_un_years_in_central"])
    st.markdown(
        """
        <div class="section-eyebrow">07 · Год во всей истории рождений</div>
        <h2 class="section-title">Доля выбранного года среди <em>всех</em> когда-либо родившихся</h2>
        <p class="caption">
            Другое сравнение с разделами 01–06: год здесь не зафиксирован, а попадает в полную оценку массы рождений.
            Для календарных годов 1950–2024 берётся отношение мировых рождений ООН к выбранной оценке числа
            всех родившихся за историю (<em>N</em>). Три значения <em>N</em> задают грубый интервал неопределённости;
            это не доверительный интервал в статистическом смысле.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="result-block">
            <div class="result-label">P(год {year} | среди всех родившихся)</div>
            <div class="result-main">
                от&nbsp;<strong>{fmt_share_among_all(p_lo[yi])}</strong>%
                &nbsp;…&nbsp;
                <strong>{fmt_share_among_all(p_mid[yi])}</strong>%
                &nbsp;…&nbsp;до&nbsp;<strong>{fmt_share_among_all(p_hi[yi])}</strong>%
            </div>
            <div class="result-secondary" style="margin-top:12px;font-size:0.92rem;">
                Сценарии <em>N</em>: ~{tot['low']/1e9:.0f}&nbsp;— {tot['central']/1e9:.0f}&nbsp;— {tot['high']/1e9:.0f}
                млрд человек.
                Доля всех лет 1950–2024 в центральном сценарии: ≈&nbsp;{share_un*100:.1f}% суммарных рождений
                (остальное — до&nbsp;1950 и иллюстративная реконструкция).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    y_mid_pct = [p * 100.0 for p in p_mid]
    y_lo_pct = [p * 100.0 for p in p_lo]
    y_hi_pct = [p * 100.0 for p in p_hi]
    fig_hist = go.Figure()
    fig_hist.add_trace(
        go.Scatter(
            x=years_full,
            y=y_hi_pct,
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig_hist.add_trace(
        go.Scatter(
            x=years_full,
            y=y_lo_pct,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(61, 90, 108, 0.18)",
            name="интервал по N",
            hovertemplate=(
                "Нижняя граница (большое N): %{y:.5f}%<extra></extra>"
            ),
        )
    )
    fig_hist.add_trace(
        go.Scatter(
            x=years_full,
            y=y_mid_pct,
            mode="lines",
            name="центральный сценарий",
            line=dict(color=PALETTE["terracotta_d"], width=2.2),
            hovertemplate="%{x}: %{y:.5f}% всех рожд.<extra></extra>",
        )
    )
    fig_hist.add_vline(
        x=year,
        line=dict(color=PALETTE["ink"], width=1, dash="dot"),
        opacity=0.5,
    )
    fig_hist.update_layout(
        paper_bgcolor=PALETTE["paper"],
        plot_bgcolor=PALETTE["paper"],
        height=340,
        margin=dict(l=24, r=24, t=52, b=32),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(family="IBM Plex Mono", color=PALETTE["ink_light"], size=11),
            showline=True,
            linecolor=PALETTE["ink"],
            linewidth=1,
            dtick=10,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=PALETTE["paper_darker"],
            tickfont=dict(family="IBM Plex Mono", color=PALETTE["ink_light"], size=10),
            title=dict(
                text="доля всех рожд., %",
                font=dict(family="IBM Plex Mono", size=10, color=PALETTE["ink_light"]),
            ),
            rangemode="tozero",
        ),
        legend=dict(
            orientation="h",
            x=0,
            y=1.12,
            font=dict(family="IBM Plex Mono", size=10, color=PALETTE["ink_soft"]),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    st.plotly_chart(fig_hist, width="stretch", config={"displayModeBar": False})
    with st.expander("Пояснения к модели (из датасета)", expanded=False):
        st.markdown(HISTORICAL.get("description_ru", ""))
        st.caption(HISTORICAL.get("caution_ru", ""))


# ============================================================================
# Источники и методология
# ============================================================================
st.markdown(
    """
    <footer class="footnotes">
        <h3>Источники и краткая методология</h3>
        <p>
            <strong>Данные.</strong> United Nations, Department of Economic and Social Affairs,
            Population Division (2024). <em>World Population Prospects 2024.</em> Лицензия CC&nbsp;BY&nbsp;3.0&nbsp;IGO.
            Берётся оценка <em>Births (thousands)</em> — число рождений за год по стране
            (Estimates 1950–2023 и medium-сценарий для 2024).
        </p>
        <p>
            <strong>Что именно сейчас считается.</strong> Для года <em>Y</em> и страны <em>C</em>:
            <em>births(C,&nbsp;Y)&nbsp;/&nbsp;births(мир,&nbsp;Y)</em> — доля рождений на
            территории <em>C</em> в суммарном числе рождений по планете за этот календарный год.
            Удобная содержательная интерпретация мысленного эксперимента «равновероятно выбрать одного
            новорождённого среди всех родившихся в мире в год <em>Y</em>»: найденная величина —
            условная вероятность страны при фиксированном годе. Это <em>не</em> ответ на вопрос
            «с какой вероятностью родиться в таком-то году»: см. блок <strong>§&nbsp;VI</strong> (PRB)
            и <strong>07</strong> (доля календарного года при нескольких сценариях <em>N</em>).
        </p>
        <p>
            <strong>Границы территорий.</strong> В WPP&nbsp;2024 используют современные границы,
            перенесённые на прошлое: «Россия в 1950» — нынешняя РФ в границах того времени (≈&nbsp;РСФСР),
            не СССР целиком; «Бангладеш в 1960» — нынешняя Бангладеш; «Германия» — ФРГ+ГДР как
            единое поле оценки.
        </p>
        <p>
            <strong>Качество оценок.</strong> ООН объединяет регистрацию актов гражданского состояния,
            переписи и обследования (в&nbsp;том числе DHS/MICS), для отдельных стран — косвенные методы;
            модели в духе когортно‑компонентных прогнозов дают сглаженные ряды. Очень грубо по группам:
            развитые страны с полной регистрацией — порядка ±1–2&nbsp;%; большинство прочих — ±5–10&nbsp;%;
            зоны длительных кризисов — до ±15–20&nbsp;%.
        </p>
        <p>
            <strong>Ограничения модели.</strong> Не учитываются младенческая и детская смертность,
            миграция в первые годы жизни, смена политических границ при жизни того же человека — показатель
            относится к месту и моменту рождения, а не к «где вы выросли».
        </p>
        <p>
            <strong>Покрытие и мелкие территории.</strong> 211 стран и территорий, 1950–2024,
            около 15&nbsp;800 пар «страна‑год». Микроэнклавы с пиком рождений &lt;&nbsp;1000 в год
            отброшены как шум (Ватикан, Токелау, Питкерн и аналоги).
        </p>
        <p>
            <strong>Как расширять назад во времени.</strong> До 1950 в WPP единой глобальной сетки нет;
            возможная склейка — исторические ряды численности (в&nbsp;том числе Maddison Project),
            обобщённые оценки рождаемости по регионам и для части стран —
            <em>Human Fertility Database</em> (точные когортные таблицы по рождаемости для ограниченного
            набора государств), плюс национальная историческая демография; неопределённость резко растёт.
        </p>
    </footer>
    """,
    unsafe_allow_html=True,
)
