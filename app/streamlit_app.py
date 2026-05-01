"""
streamlit_app.py
────────────────
Атлас долей живорождений по странам и годам (1950–2024), UN WPP 2024.

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

import html
import json
import math
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

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# Частичные деплои / старый country_flag на Cloud: не падаем, если нет новых имён.
try:
    from domain import country_flag as _country_flag_mod  # noqa: E402
except ImportError:  # pragma: no cover
    _country_flag_mod = None


def _fallback_country_label_plain(iso3: str, name_ru: str) -> str:
    return f"{name_ru} ({iso3.strip().upper()})"


def _fallback_country_heading_html(iso3: str, name_ru: str) -> str:
    _ = iso3
    return html.escape(name_ru)


if _country_flag_mod is not None:
    country_label_plain = getattr(
        _country_flag_mod,
        "country_label_plain",
        _fallback_country_label_plain,
    )
    country_heading_html = getattr(
        _country_flag_mod,
        "country_heading_html",
        _fallback_country_heading_html,
    )
    country_label_compact_flag = getattr(
        _country_flag_mod,
        "country_label_compact_flag",
        lambda iso3, name_ru: country_label_plain(iso3, name_ru),
    )
else:  # pragma: no cover
    country_label_plain = _fallback_country_label_plain
    country_heading_html = _fallback_country_heading_html
    country_label_compact_flag = _fallback_country_label_plain

from domain.country_ru_cases import in_country_where  # noqa: E402
from domain.nl_birth_query import parse_birth_description  # noqa: E402
from domain.prb_ever_lived import (  # noqa: E402
    EVER_LIVED_PRB_2022,
    PRB_ARTICLE_URL,
    share_of_prb_total,
)

# Форматтеры с отдельным модулем: при рассинхроне Cloud не падаем, если в старом
# prb_ever_lived нет этих имён — они живут в prb_ui_uncertain.py.
try:
    from domain.prb_ui_uncertain import (  # noqa: E402
        format_one_in_uncertain,
        format_uncertain_small_percent,
        round_to_n_significant,
    )
except ImportError:  # pragma: no cover — страховка для частичных деплоев
    try:
        from domain.prb_ever_lived import (  # type: ignore[no-redef]
            format_one_in_uncertain,
            format_uncertain_small_percent,
            round_to_n_significant,
        )
    except ImportError:

        def round_to_n_significant(x: float, n: int = 2) -> float:
            if x == 0 or not math.isfinite(x):
                return x
            log = math.floor(math.log10(abs(x)))
            factor = 10.0 ** (log - n + 1)
            return round(x / factor) * factor

        def format_uncertain_small_percent(share: float) -> str:
            if share <= 0:
                return "0"
            pct = share * 100.0
            body = f"{pct:.2g}".replace(".", ",")
            return f"~{body}"

        def _fmt_int_nbsp_local(n: float) -> str:
            return f"{int(round(n)):,}".replace(",", "\u00a0")

        def format_one_in_uncertain(recip: float) -> str:
            if recip <= 0 or not math.isfinite(recip):
                return "—"
            r = round_to_n_significant(recip, 2)
            if r >= 1_000_000_000:
                b = r / 1_000_000_000
                b = round_to_n_significant(b, 2)
                return f"порядка 1 из {_fmt_int_nbsp_local(b)}\u00a0млрд"
            if r >= 1_000_000:
                m = r / 1_000_000
                m = round_to_n_significant(m, 2)
                return f"примерно 1 из {_fmt_int_nbsp_local(m)}\u00a0млн"
            if r >= 10_000:
                k = r / 1000
                k = round_to_n_significant(k, 2)
                return f"примерно 1 из {_fmt_int_nbsp_local(k)}\u00a0тыс."
            return f"примерно 1 из {_fmt_int_nbsp_local(r)}"

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

# ============================================================================
# Конфигурация страницы
# ============================================================================
st.set_page_config(
    page_title="«Вероятность» родиться в своей стране · WPP 2024",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": (
            "Интерактивные доли живорождений по странам "
            "(UN World Population Prospects 2024)."
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
    # Две линии на графике сравнения — контрастные, не из одной гаммы
    "cmp_a":        "#1d4ed8",
    "cmp_b":        "#c2410c",
    "share_line":   "#1e3a8a",
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
    /* Без fonts.googleapis.com — в части сетей РФ/КНР блокируется и вешает страницу */
    html, body, [class*="css"]  {{
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans", "Liberation Sans", sans-serif;
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
        font-family: ui-monospace, "Cascadia Code", "Segoe UI Mono", monospace;
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {PALETTE['ink_soft']};
    }}
    .masthead-left {{ font-weight: 600; }}
    .masthead-right {{ font-style: normal; text-transform: none; letter-spacing: 0.04em; }}

    /* ── hero ────────────────────────────────────────────────────────── */
    .hero-eyebrow {{
        font-family: Consolas, ui-monospace, monospace;
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
        font-family: system-ui, sans-serif;
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
    span.flag-emoji {{
        font-family: "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", emoji;
        font-size: 1.15em;
        vertical-align: -0.06em;
        margin-right: 2px;
    }}
    .hero-sub {{
        font-size: 1.05rem;
        color: {PALETTE['ink_soft']};
        max-width: 680px;
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 36px;
    }}

    /* ── NL assist (видимая плашка, без expander) ─────────────────────── */
    .nl-assist-kicker {{
        font-family: Consolas, ui-monospace, monospace;
        font-size: 10px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: {PALETTE['terracotta']};
        margin: 0 0 8px 0;
    }}
    .nl-assist-title {{
        font-family: system-ui, sans-serif;
        font-size: 1.08rem;
        font-weight: 600;
        color: {PALETTE['ink']};
        margin: 0 0 10px 0;
        line-height: 1.35;
    }}
    .nl-assist-lead {{
        font-size: 0.92rem;
        color: {PALETTE['ink_soft']};
        line-height: 1.55;
        margin: 0 0 16px 0;
        max-width: 720px;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 14px !important;
        border: 1px solid {PALETTE['paper_darker']} !important;
        background: linear-gradient(165deg, {PALETTE['paper_dark']} 0%, {PALETTE['paper']} 100%) !important;
        box-shadow: 0 4px 24px rgba(28, 28, 28, 0.06) !important;
        padding: 6px 8px 12px !important;
        margin-bottom: 1.75rem !important;
    }}

    /* ── eyebrows / section headings ────────────────────────────────── */
    .section-eyebrow {{
        font-family: Consolas, ui-monospace, monospace;
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
        font-family: system-ui, sans-serif;
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
        font-family: Consolas, ui-monospace, monospace;
        font-size: 10px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: {PALETTE['ink_light']};
        margin-bottom: 18px;
    }}
    .result-main {{
        font-family: system-ui, sans-serif;
        font-size: clamp(1.2rem, 3.2vw, 1.85rem);
        line-height: 1.35;
        font-weight: 500;
        color: {PALETTE['ink']};
        font-variant-numeric: tabular-nums;
    }}
    .result-big {{
        font-family: system-ui, sans-serif;
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
        font-family: system-ui, sans-serif;
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
        font-family: Consolas, ui-monospace, monospace !important;
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
        font-family: system-ui, sans-serif !important;
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
        font-family: Consolas, ui-monospace, monospace !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 10px !important;
        color: {PALETTE['ink_light']} !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: system-ui, sans-serif !important;
        font-size: 1.85rem !important;
        font-weight: 600 !important;
        color: {PALETTE['ink']} !important;
        font-variant-numeric: tabular-nums;
    }}
    div[data-testid="stMetricDelta"] {{
        font-family: Consolas, ui-monospace, monospace !important;
        font-size: 11px !important;
        color: {PALETTE['ink_soft']} !important;
    }}

    /* ── metric tile grid (§03) ───────────────────────────────────────── */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-bottom: 8px;
    }}
    @media (max-width: 900px) {{
        .metric-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .metric-tile {{
        background: {PALETTE['paper']};
        border: 1px solid {PALETTE['ink_light']};
        padding: 22px 18px 18px;
        min-height: 158px;
        display: flex;
        flex-direction: column;
    }}
    .metric-tile-label {{
        font-family: Consolas, ui-monospace, monospace;
        font-size: 10px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {PALETTE['ink_light']};
        margin-bottom: 14px;
        line-height: 1.35;
    }}
    .metric-tile-value {{
        font-family: system-ui, sans-serif;
        font-size: 1.85rem;
        font-weight: 600;
        color: {PALETTE['ink']};
        font-variant-numeric: tabular-nums;
        margin-bottom: auto;
        padding-bottom: 12px;
    }}
    .metric-tile-foot {{
        font-size: 0.88rem;
        color: {PALETTE['ink_soft']};
        line-height: 1.45;
        margin-top: 4px;
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
        font-family: Consolas, ui-monospace, monospace;
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


REGION_RU = {
    "Africa": "Африка",
    "Asia": "Азия",
    "Europe": "Европа",
    "Americas": "Америка",
    "Oceania": "Океания",
}


def fmt_pct(p: float) -> str:
    """Проценты из WPP: запятая как десятичный разделитель."""
    if p >= 1:
        txt = f"{p:.2f}"
    elif p >= 0.1:
        txt = f"{p:.2f}"
    elif p >= 0.01:
        txt = f"{p:.3f}"
    else:
        txt = f"{p:.4f}"
    return txt.replace(".", ",")


def fmt_pct_chart(p: float) -> str:
    """Подписи на осях и столбцах: без лишних нулей (15, а не 15,00)."""
    if not math.isfinite(p):
        return "—"
    if abs(p) < 1e-12:
        return "0"
    if abs(p - round(p)) < 1e-6:
        return str(int(round(p)))
    if p >= 1.0:
        s = f"{p:.1f}".replace(".", ",").rstrip("0").rstrip(",")
        return s if s else "0"
    if p >= 0.1:
        s = f"{p:.2f}".replace(".", ",").rstrip("0").rstrip(",")
        return s if s else "0"
    if p >= 0.01:
        s = f"{p:.3f}".replace(".", ",").rstrip("0").rstrip(",")
        return s if s else "0"
    s = f"{p:.4f}".replace(".", ",").rstrip("0").rstrip(",")
    return s if s else "0"


def fmt_one_in_wpp(recip: float) -> str:
    """Округлённые «1 из N» для рядов ООН (наглядность без ложной точности)."""
    if not math.isfinite(recip) or recip <= 0:
        return "—"
    r = int(round(round_to_n_significant(recip, 2)))
    return fmt_int(float(r))


def humanize_birth_interval_seconds(c_births_year: float) -> str:
    """Интервал между рождениями при равномерном распределении в течение года."""
    if c_births_year <= 0:
        return "—"
    sec = (365.25 * 86400.0) / c_births_year
    if sec < 90:
        s = max(1, int(round(sec)))
        return f"примерно одно рождение каждые {s} секунд"
    if sec < 3600:
        m = sec / 60.0
        m_r = round_to_n_significant(m, 2)
        m_txt = f"{m_r:.1f}".replace(".", ",")
        return f"примерно одно рождение каждые {m_txt} минут"
    h = sec / 3600.0
    h_r = round_to_n_significant(h, 2)
    h_txt = f"{h_r:.1f}".replace(".", ",")
    return f"примерно одно рождение каждые {h_txt} часов"


def fmt_share_among_all(p: float) -> str:
    """Доля 0…1 среди всех родившихся — в процентах, до 3 значащих цифр."""
    x = p * 100.0
    return f"{x:.3g}".replace(".", ",")


# ============================================================================
# MASTHEAD + HERO
# ============================================================================
st.markdown(
    f"""
    <section>
        <div class="hero-eyebrow">ООН WPP 2024 · {YEAR_MIN}–{YEAR_MAX}</div>
        <h1 class="hero-h1">Какова &laquo;вероятность&raquo; родиться<br><em>в стране моего рождения?</em></h1>
        <p class="hero-sub">
            В узком статистическом смысле для уже родившегося человека такой «вероятности» нет — зато есть
            прозрачный численный аналог: <strong>какую долю всех младенцев в мире за выбранный год</strong>
            составили бы живорождения именно этой страны — по оценкам <strong>World Population Prospects 2024</strong>.
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


def _country_opt(iso_code: str) -> str:
    return country_label_compact_flag(iso_code, LABEL_FOR[iso_code])
ISO_TO_REGION = {iso: c["g"] for iso, c in COUNTRIES.items()}
REGIONS = sorted({c["g"] for c in COUNTRIES.values()})

default_iso0 = "RUS" if "RUS" in ISO_OPTIONS else ISO_OPTIONS[0]
if "bl_year" not in st.session_state:
    st.session_state.bl_year = 1992
if "bl_iso" not in st.session_state:
    st.session_state.bl_iso = default_iso0
if st.session_state.bl_iso not in ISO_OPTIONS:
    st.session_state.bl_iso = default_iso0

st.markdown("### Год и страна")
with st.container(border=True):
    st.markdown(
        """
        <p class="nl-assist-kicker">Запрос текстом</p>
        <p class="nl-assist-title">Опишите страну и год — как одним сообщением ассистенту</p>
        <p class="nl-assist-lead">Поддерживается русский и английский. После ответа обновятся поля
        <strong>Год</strong> и <strong>Страна</strong> ниже; их можно править вручную.</p>
        """,
        unsafe_allow_html=True,
    )
    nl_txt = st.text_area(
        "Запрос по стране и году",
        placeholder=(
            "Пример: Россия, 1992 · родился в Бразилии в 2001 · Ukraine 1999 · Tokyo, Japan, 1975"
        ),
        height=100,
        label_visibility="collapsed",
        key="nl_free_text",
    )
    nl_go = st.button(
        "Подставить в поля ниже",
        type="primary",
        use_container_width=True,
        key="nl_submit",
    )
    if nl_go:
        _p = parse_birth_description(nl_txt, COUNTRIES, YEAR_MIN, YEAR_MAX)
        if _p.ok and _p.iso and _p.year:
            st.session_state.bl_year = int(_p.year)
            st.session_state.bl_iso = _p.iso
            st.session_state.nl_ok_hint = _p.message_ru
            st.session_state.nl_err = None
            st.rerun()
        else:
            st.session_state.nl_ok_hint = None
            st.session_state.nl_err = _p.message_ru
    if st.session_state.get("nl_ok_hint"):
        st.success(st.session_state.nl_ok_hint)
    if st.session_state.get("nl_err"):
        st.warning(st.session_state.nl_err)

col_yr, col_co = st.columns([1, 1], gap="large")
with col_yr:
    year = st.slider(
        "Год",
        min_value=YEAR_MIN,
        max_value=YEAR_MAX,
        step=1,
        key="bl_year",
        help="Календарный год Y: births(страна, Y) / births(мир, Y).",
    )
with col_co:
    iso = st.selectbox(
        "Страна",
        options=ISO_OPTIONS,
        key="bl_iso",
        format_func=_country_opt,
        help="Границы — как в WPP 2024 (современные государства, ретроспективно).",
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
_where = in_country_where(iso, country["r"])
_one_line = (
    f"Один из {fmt_one_in_wpp(one_in)} младенцев, родившихся в мире в {year} году, родился {_where}."
    if c_births > 0 and math.isfinite(one_in)
    else "В этом ряду WPP для выбранной пары «страна — год» нет положительного числа живорождений."
)
_head_main = country_heading_html(iso, country["r"])

st.markdown(
    f"""
    <div class="result-block">
        <div class="result-label">{_head_main} · {year} · доля в мировом итоге живорождений</div>
        <div class="result-big">{fmt_pct(pct)}<span class="pct-sign">%</span></div>
        <div class="result-secondary">{_one_line}</div>
        <div class="result-secondary" style="margin-top:10px;font-size:0.95rem;text-align:left;max-width:640px;margin-left:auto;margin-right:auto;">
            Строго говоря, <strong>это не вероятность «родиться именно там»</strong>: для уже случившегося
            рождения так не формулируют без модели до зачатия.
            Здесь — <strong>доля живорождений страны в мировом итоге за {year} год</strong>; при мысленном
            равном шансе между всеми новорождёнными мира в этом году получается то же число.
            Настоящий ex&nbsp;ante расчёт требовал бы данных о родителях и демографии до вашего рождения —
            такой микроуровень недоступен; остаётся понятный межстрановой срез ООН.
        </div>
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
    <h2 class="section-title">Мир в&nbsp;<em>{year}</em>: доля каждой страны в живорождениях</h2>
    <p class="caption">
        Цвет — доля в мировом итоге за год, шкала логарифмическая (иначе крупные и мелкие страны не различить).
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
            "name_disp": country_label_compact_flag(code, c["r"]),
            "births": b_k * 1000,
            "pct": p,
            "color": color_for_pct(p),
        }
    )
map_df = pd.DataFrame(map_rows)
_eps_map = 0.005
if map_df.empty:
    st.warning("Нет данных карты для выбранного года.")
else:
    pct_arr = map_df["pct"].to_numpy(dtype=float)
    z_log = np.log10(np.maximum(pct_arr, 1e-8) + _eps_map)
    map_df = map_df.assign(
        z_log=z_log,
        pct_lbl=[f"{fmt_pct_chart(float(x))}%" for x in map_df["pct"].values],
    )
    zmax_pct = float(map_df["pct"].max())
    nice_ticks = [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 15.0, 25.0, 50.0]
    tick_pcts_use = [p for p in nice_ticks if p <= zmax_pct * 1.15 + 1e-9]
    if not tick_pcts_use:
        tick_pcts_use = [0.01, min(0.1, zmax_pct)]
    if zmax_pct > tick_pcts_use[-1] * 1.02:
        tick_pcts_use = tick_pcts_use + [round(zmax_pct, 2)]
    tickvals = [math.log10(p + _eps_map) for p in tick_pcts_use]
    ticktext = [f"{fmt_pct_chart(p)}%" for p in tick_pcts_use]
    zmin_l = float(np.min(map_df["z_log"]))
    zmax_l = float(np.max(map_df["z_log"]))

    fig_map = go.Figure()
    fig_map.add_trace(
        go.Choropleth(
            locations=map_df["iso"],
            z=map_df["z_log"],
            locationmode="ISO-3",
            customdata=np.stack(
                [map_df["name_disp"].values, map_df["births"].values, map_df["pct_lbl"].values],
                axis=-1,
            ),
            colorscale=[
                [0.00, PALETTE["paper"]],
                [0.05, "#e4e8ea"],
                [0.20, "#c5d0d6"],
                [0.45, "#89a7b5"],
                [0.65, PALETTE["terracotta"]],
                [0.85, PALETTE["terracotta_d"]],
                [1.00, PALETTE["terracotta_dd"]],
            ],
            zmin=zmin_l,
            zmax=zmax_l,
            marker_line_color=PALETTE["ink"],
            marker_line_width=0.35,
            colorbar=dict(
                title=dict(
                    text=(
                        "доля в мировом итоге, %"
                        "<br><sup>логарифмическая шкала</sup>"
                    ),
                    font=dict(family="Consolas", size=10, color=PALETTE["ink_soft"]),
                ),
                tickvals=tickvals,
                ticktext=ticktext,
                tickfont=dict(family="Consolas", size=10, color=PALETTE["ink_soft"]),
                thickness=10,
                len=0.55,
                outlinewidth=0,
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "доля в мировом итоге: %{customdata[2]}<br>"
                "живорождений: %{customdata[1]:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    if iso in map_df["iso"].values:
        fig_map.add_trace(
            go.Choropleth(
                locations=[iso],
                z=[zmax_l],
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
        lataxis_range=[-60, 88],
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
        font=dict(family="Segoe UI", color=PALETTE["ink"]),
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
    <h2 class="section-title">Тысяча клеток — доля страны в мировом годе</h2>
    """,
    unsafe_allow_html=True,
)

dots_to_fill = int(max(0, min(1000, round(pct * 10))))
if pct > 0 and pct < 0.1 and dots_to_fill == 0:
    isotype_caption = (
        "Доля &lt; 0,1&nbsp;%: в сетке из 1000 клеток не набирается даже одна закрашенная "
        f"(по WPP за {year} год число живорождений всё же положительное)."
    )
elif dots_to_fill == 0:
    isotype_caption = f"Нет доли для закраски (ноль или пропуск в ряду WPP за {year} год)."
elif dots_to_fill > 800:
    isotype_caption = (
        f"{dots_to_fill} из 1000 клеток — выбранная страна; это очень большая доля мирового итога за {year} год."
    )
else:
    isotype_caption = (
        f"Год {year}: закрашено {dots_to_fill} из 1000 — столько «долей» у страны в суммарных живорождениях мира."
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
    <div style="font-family:Consolas,monospace;font-size:11px;
        text-transform:uppercase;letter-spacing:0.08em;color:{PALETTE['ink_soft']};
        margin-top:8px;display:flex;gap:24px;flex-wrap:wrap;">
            <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;
            background:{PALETTE['terracotta']};border:1px solid {PALETTE['terracotta_d']};
            margin-right:8px;vertical-align:-1px;"></span>{country_heading_html(iso, country['r'])}</span>
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
    <h2 class="section-title">Сводка по выбранной стране и году</h2>
    """,
    unsafe_allow_html=True,
)

per_day = c_births / 365.25
rank_share = (rank_position / rank_total) if rank_total and rank_position else 1.0
if rank_share <= 0.05:
    rank_tier_ru = "верхние 5%"
elif rank_share <= 0.10:
    rank_tier_ru = "верхние 10%"
elif rank_share <= 0.25:
    rank_tier_ru = "верхняя четверть"
elif rank_share <= 0.50:
    rank_tier_ru = "выше медианы"
else:
    rank_tier_ru = "ниже медианы"
region_ru = REGION_RU.get(region, region)
_share_reg_txt = f"{share_in_region:.1f}".replace(".", ",")

st.markdown(
    f"""
    <div class="metric-grid">
        <div class="metric-tile" title="Источник: UN WPP 2024, Births (thousands).">
            <div class="metric-tile-label">Живорождений</div>
            <div class="metric-tile-value">{fmt_int(c_births)}</div>
            <div class="metric-tile-foot">{country_heading_html(iso, country["r"])}, {year}</div>
        </div>
        <div class="metric-tile">
            <div class="metric-tile-label">В сутки</div>
            <div class="metric-tile-value">{fmt_int(per_day)}</div>
            <div class="metric-tile-foot">{humanize_birth_interval_seconds(c_births)}</div>
        </div>
        <div class="metric-tile">
            <div class="metric-tile-label">Место в мире</div>
            <div class="metric-tile-value">{rank_position} из {rank_total}</div>
            <div class="metric-tile-foot">{rank_tier_ru} по числу рождений в датасете</div>
        </div>
        <div class="metric-tile">
            <div class="metric-tile-label">Доля в регионе</div>
            <div class="metric-tile-value">{_share_reg_txt}%</div>
            <div class="metric-tile-foot">из {fmt_int(region_total_k * 1000)} живорождений в «{region_ru}»</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# § IV · ТОП СТРАН (ГОРИЗОНТАЛЬНАЯ ГИСТОГРАММА)
# ============================================================================
st.markdown(
    f"""
    <div class="section-eyebrow">04 · Рейтинг стран</div>
    <h2 class="section-title">Топ по числу живорождений в&nbsp;<em>{year}</em></h2>
    <p class="caption">
        12 стран с наибольшим объёмом; ваша добавляется, если её нет в списке. У столбца — доля в мировом итоге.
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
            "label": f"{real_rank:02d}  {country_label_compact_flag(code, COUNTRIES[code]['r'])}",
            "pct": b_k * 1000 / w_births * 100,
            "births": b_k * 1000,
            "is_user": code == iso,
        }
    )
bar_df = pd.DataFrame(bar_rows)
bar_df["pct_lbl"] = [fmt_pct_chart(float(p)) for p in bar_df["pct"]]

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
        text=[f"{p}%" for p in bar_df["pct_lbl"]],
        textposition="outside",
        textfont=dict(family="Consolas", color=PALETTE["ink_soft"], size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{customdata[0]}% от мира за год<br>"
            "%{customdata[1]:,.0f} живорождений<extra></extra>"
        ),
        customdata=np.stack([bar_df["pct_lbl"].values, bar_df["births"].values], axis=-1),
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
        tickfont=dict(family="Segoe UI", color=PALETTE["ink"], size=13),
        showgrid=False,
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="Consolas", color=PALETTE["ink_light"], size=10),
        ticksuffix="%",
        zeroline=False,
    ),
    font=dict(family="Segoe UI"),
    showlegend=False,
)
_xmax_bar = float(bar_df["pct"].max()) if len(bar_df) else 1.0
_fbar = ".0f" if _xmax_bar >= 2.5 else ".1f"
fig_bar.update_xaxes(tickformat=_fbar)
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
    <h2 class="section-title">Динамика: {country_heading_html(iso, country['r'])}</h2>
    <p class="caption">
        Слева — живорождения в год (WPP). Справа — доля этой же страны в мировом итоге за каждый год.
        Заливка и пунктир относятся только к абсолютному ряду; линия доли — синяя, правая ось.
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
trend_df["share_pct"] = [share_pct(iso, int(y)) for y in trend_df["year"]]

# 5-летнее скользящее среднее — только для абсолютного ряда
trend_df["smooth"] = trend_df["births"].rolling(window=5, center=True, min_periods=1).mean()

_share_hover = [[fmt_pct_chart(float(v))] for v in trend_df["share_pct"]]

fig_line = go.Figure()
fig_line.add_trace(
    go.Scatter(
        x=trend_df["year"],
        y=trend_df["births"],
        mode="lines",
        line=dict(color=PALETTE["terracotta_d"], width=1.6),
        fill="tozeroy",
        fillcolor="rgba(61,90,108,0.18)",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} живорождений<extra></extra>",
        name="живорождения в год",
    )
)
fig_line.add_trace(
    go.Scatter(
        x=trend_df["year"],
        y=trend_df["smooth"],
        mode="lines",
        line=dict(color=PALETTE["ink"], width=1.0, dash="dot"),
        hoverinfo="skip",
        name="сглаживание (5 лет)",
    )
)
fig_line.add_trace(
    go.Scatter(
        x=trend_df["year"],
        y=trend_df["share_pct"],
        yaxis="y2",
        mode="lines",
        line=dict(color=PALETTE["share_line"], width=2.2),
        name="доля в мире, %",
        customdata=_share_hover,
        hovertemplate="<b>%{x}</b><br>%{customdata[0]}% мирового итога<extra></extra>",
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
        textfont=dict(family="Segoe UI", color=PALETTE["ink"], size=14),
        showlegend=False,
        hovertemplate=f"<b>{year}</b><br>{fmt_int(c_births)} живорождений<extra></extra>",
    )
)
fig_line.update_layout(
    paper_bgcolor=PALETTE["paper"],
    plot_bgcolor=PALETTE["paper"],
    height=340,
    margin=dict(l=56, r=58, t=56, b=34),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family="Consolas", color=PALETTE["ink_light"], size=11),
        showline=True,
        linecolor=PALETTE["ink"],
        linewidth=1,
        dtick=10,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="Consolas", color=PALETTE["ink_light"], size=10),
        title=dict(
            text="живорождений в год",
            font=dict(family="Consolas", size=10, color=PALETTE["ink_light"]),
        ),
        rangemode="tozero",
        tickformat=",",
    ),
    yaxis2=dict(
        overlaying="y",
        side="right",
        showgrid=False,
        rangemode="tozero",
        tickfont=dict(family="Consolas", color=PALETTE["share_line"], size=10),
        title=dict(
            text="доля в мире, %",
            font=dict(family="Consolas", size=10, color=PALETTE["share_line"]),
        ),
    ),
    legend=dict(
        orientation="h",
        x=0,
        y=1.12,
        font=dict(family="Consolas", size=10, color=PALETTE["ink_soft"]),
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
    <h2 class="section-title">Две страны: число живорождений по годам</h2>
    <p class="caption">
        Только абсолютные объёмы WPP; долю в мире смотрите в разделе 05 для одной выбранной страны.
    </p>
    """,
    unsafe_allow_html=True,
)

_cmp_candidates = [c for c in ("USA", "DEU", "CHN", "GBR", "IND", "FRA") if c in ISO_OPTIONS and c != iso]
cmp_default = _cmp_candidates[0] if _cmp_candidates else next(
    (c for c in ISO_OPTIONS if c != iso),
    ISO_OPTIONS[0],
)
iso_b = st.selectbox(
    "Вторая страна",
    options=ISO_OPTIONS,
    index=ISO_OPTIONS.index(cmp_default),
    format_func=_country_opt,
    key="bl_cmp_iso",
)
country_b = COUNTRIES[iso_b]
years_full = list(range(YEAR_MIN, YEAR_MAX + 1))
_nm_cmp_a = country_label_compact_flag(iso, country["r"])
_nm_cmp_b = country_label_compact_flag(iso_b, country_b["r"])

fig_cmp = go.Figure()
fig_cmp.add_trace(
    go.Scatter(
        x=years_full,
        y=[v * 1000 for v in country["b"]],
        mode="lines",
        name=_nm_cmp_a,
        line=dict(color=PALETTE["cmp_a"], width=2.6),
        hovertemplate="<b>%{x}</b><br>"
        + _nm_cmp_a
        + "<br>%{y:,.0f} живорождений<extra></extra>",
    )
)
fig_cmp.add_trace(
    go.Scatter(
        x=years_full,
        y=[v * 1000 for v in country_b["b"]],
        mode="lines",
        name=_nm_cmp_b,
        line=dict(color=PALETTE["cmp_b"], width=2.6, dash="solid"),
        hovertemplate="<b>%{x}</b><br>"
        + _nm_cmp_b
        + "<br>%{y:,.0f} живорождений<extra></extra>",
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
        tickfont=dict(family="Consolas", color=PALETTE["ink_light"], size=11),
        showline=True,
        linecolor=PALETTE["ink"],
        linewidth=1,
        dtick=10,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=PALETTE["paper_darker"],
        tickfont=dict(family="Consolas", color=PALETTE["ink_light"], size=10),
        title=dict(
            text="живорождений в год",
            font=dict(family="Consolas", size=10, color=PALETTE["ink_light"]),
        ),
        rangemode="tozero",
        tickformat=",",
    ),
    legend=dict(
        orientation="h",
        x=0,
        y=1.12,
        font=dict(family="Segoe UI", size=12, color=PALETTE["ink"]),
        bgcolor="rgba(0,0,0,0)",
    ),
)
st.plotly_chart(fig_cmp, width="stretch", config={"displayModeBar": False})


# ============================================================================
# § VI · PRB — масштаб «все когда-либо родившиеся»
# ============================================================================
_pop_k = float(META.get("world_population_july_2024_thousands", 8120.0 * 1000.0))
_alive_share = (_pop_k * 1000.0) / float(EVER_LIVED_PRB_2022)
_p_you_prb = share_of_prb_total(float(c_births)) if c_births > 0 else 0.0
_recip_prb = (1.0 / _p_you_prb) if _p_you_prb > 0 else float("inf")

st.markdown(
    """
    <div class="section-eyebrow">07 · Среди всех людей в истории</div>
    <h2 class="section-title">PRB: ~117 млрд рождений «за всю историю»</h2>
    <p class="caption">
        Оценка Population Reference Bureau (2022): сумма модельных рождений с глубокой древности.
        Это не «сколько людей живёт одновременно»; порядок величины и интерпретация — отдельно от рядов ООН выше.
    </p>
    """,
    unsafe_allow_html=True,
)
_prb_pct = format_uncertain_small_percent(_p_you_prb)
_prb_one = format_one_in_uncertain(_recip_prb)
_alt_line = ""
if _p_you_prb > 0 and _p_you_prb <= 1e-5:
    _alt_line = " Упрощённо: <strong>порядка одного на миллион</strong> в этом масштабе."
_alive_pct_lbl = format_uncertain_small_percent(_alive_share)
st.markdown(
    f"""
    <div class="result-block">
        <div class="result-label">{country_heading_html(iso, country['r'])} · {year} · доля в оценке PRB (~117 млрд рождений)</div>
        <div class="result-big">{_prb_pct}<span class="pct-sign">%</span></div>
        <div class="result-secondary" style="margin-top:6px;">
            Модель PRB (Kaneda &amp; Haub, 2022): показаны <strong>порядки</strong> — сама оценка ~117 млрд
            неопределена примерно на ±20–30%.
        </div>
        <div class="result-main" style="margin-top:18px;">
            В пересчёте «один из <em>N</em>»: <strong>{_prb_one}</strong>{_alt_line}
        </div>
        <div class="result-secondary" style="margin-top:16px;">
            Для сравнения: ныне живущие — около <strong>{_alive_pct_lbl}&nbsp;%</strong> того же знаменателя PRB
            (оценка численности «World» на 2024 по WPP / те же ~117 млрд — ориентир, не прогноз).
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <p class="caption" style="font-size:0.85rem;margin-top:16px;">
        <a href="{PRB_ARTICLE_URL}" rel="noopener noreferrer">Kaneda &amp; Haub (PRB, 2022)</a>.
        Не смешивайте с годовыми долями ООН в разделах 01–06.
    </p>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# Доля года среди всех когда-либо родившихся
# ============================================================================
if HISTORICAL is not None:
    pct_blocks = HISTORICAL["pct_year"]
    p_lo = pct_blocks["low"]
    p_mid = pct_blocks["central"]
    p_hi = pct_blocks["high"]
    yi = year - YEAR_MIN
    tot = HISTORICAL["total_ever_born_persons"]
    share_un = float(HISTORICAL["share_of_all_births_un_years_in_central"])
    st.markdown(
        """
        <div class="section-eyebrow">08 · Год во всей истории рождений</div>
        <h2 class="section-title">Доля одного года среди всех когда-либо родившихся (сценарии <em>N</em>)</h2>
        <p class="caption">
            Число рождений в мире за год из WPP отнесено к трём порядковым оценкам «всех рождений за историю».
            Полоса на графике — не классический доверительный интервал.
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
                Доля всех лет 1950–2024 в центральном сценарии: ≈&nbsp;{fmt_pct_chart(share_un * 100.0)}% суммарных рождений
                (остальное — до&nbsp;1950 и иллюстративная реконструкция).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    y_mid_pct = [p * 100.0 for p in p_mid]
    y_lo_pct = [p * 100.0 for p in p_lo]
    y_hi_pct = [p * 100.0 for p in p_hi]
    _band_lbl = [
        f"от {fmt_pct_chart(lo)}% до {fmt_pct_chart(hi)}% (по N)"
        for lo, hi in zip(y_lo_pct, y_hi_pct)
    ]
    _mid_lbl = [fmt_pct_chart(v) for v in y_mid_pct]
    _y_top = max(float(np.max(y_hi_pct)), float(np.max(y_mid_pct))) if y_mid_pct else 0.0
    _y_ticks = np.linspace(0.0, _y_top, 7) if _y_top > 0 else np.array([0.0])
    _y_ticktext = [f"{fmt_pct_chart(float(t))}%" for t in _y_ticks]
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
            customdata=[[s] for s in _band_lbl],
            hovertemplate="%{x}: %{customdata[0]}<extra></extra>",
        )
    )
    fig_hist.add_trace(
        go.Scatter(
            x=years_full,
            y=y_mid_pct,
            mode="lines",
            name="центральный сценарий",
            line=dict(color=PALETTE["terracotta_d"], width=2.2),
            customdata=[[s] for s in _mid_lbl],
            hovertemplate="%{x}: %{customdata[0]}% всех живорождений<extra></extra>",
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
            tickfont=dict(family="Consolas", color=PALETTE["ink_light"], size=11),
            showline=True,
            linecolor=PALETTE["ink"],
            linewidth=1,
            dtick=10,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=PALETTE["paper_darker"],
            tickmode="array",
            tickvals=_y_ticks.tolist(),
            ticktext=_y_ticktext,
            tickfont=dict(family="Consolas", color=PALETTE["ink_light"], size=10),
            title=dict(
                text="доля всех живорождений, %",
                font=dict(family="Consolas", size=10, color=PALETTE["ink_light"]),
            ),
            rangemode="tozero",
        ),
        legend=dict(
            orientation="h",
            x=0,
            y=1.12,
            font=dict(family="Consolas", size=10, color=PALETTE["ink_soft"]),
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
with st.expander("О данных и методе", expanded=False):
    st.markdown(
        """
        <div class="footnotes" style="border-top:none;padding-top:0;margin-top:0;">
        <h3>Источники и краткая методология</h3>
        <p>
            <strong>Данные.</strong> United Nations, Department of Economic and Social Affairs,
            Population Division (2024). <em>World Population Prospects 2024.</em> Лицензия CC&nbsp;BY&nbsp;3.0&nbsp;IGO.
            Берётся оценка <em>Births (thousands)</em> — число живорождений за год&nbsp;по стране
            (Estimates 1950–2023 и medium-сценарий для 2024).
        </p>
        <p>
            <strong>Что именно считается.</strong> Для года <em>Y</em> и страны <em>C</em>:
            <em>births(C,&nbsp;Y)&nbsp;/&nbsp;births(мир,&nbsp;Y)</em> — доля живорождений на
            территории <em>C</em> в суммарном числе живорождений по планете за календарный год.
            Мысленный эксперимент «равновероятно выбрать одного новорождённого среди всех родившихся в мире
            в год <em>Y</em>» даёт условную вероятность страны при фиксированном годе. Это <em>не</em> ответ
            на «с какой вероятностью родиться в таком-то году»: см. разделы <strong>07</strong> (PRB) и
            <strong>08</strong> (год среди сценариев <em>N</em>).
        </p>
        <p>
            <strong>Границы территорий.</strong> В WPP&nbsp;2024 используют современные границы,
            перенесённые на прошлое: «Россия в 1950» — нынешняя РФ в границах того времени (≈&nbsp;РСФСР),
            не СССР целиком; «Бангладеш в 1960» — нынешняя Бангладеш; «Германия» — ФРГ+ГДР как
            единое поле оценки.
        </p>
        <p>
            <strong>Качество оценок.</strong> ООН объединяет регистрацию актов гражданского состояния,
            переписи и обследования (в том числе DHS/MICS), для отдельных стран — косвенные методы;
            модели в духе когортно-компонентных прогнозов дают сглаженные ряды. Очень грубо по группам:
            развитые страны с полной регистрацией — порядка ±1–2&nbsp;%; большинство прочих — ±5–10&nbsp;%;
            зоны длительных кризисов — до ±15–20&nbsp;%.
        </p>
        <p>
            <strong>Ограничения модели.</strong> Не учитываются младенческая и детская смертность,
            миграция в первые годы жизни, смена политических границ при жизни того же человека — показатель
            относится к месту и моменту рождения, а не к «где вы выросли».
        </p>
        <p>
            <strong>Покрытие.</strong> 211 стран и территорий, 1950–2024,
            около 15&nbsp;800 пар «страна‑год». Микроэнклавы с пиком живорождений &lt;&nbsp;1000 в год
            отброшены как шум (Ватикан, Токелау, Питкерн и аналоги).
        </p>
        <p>
            <strong>Как расширять назад во времени.</strong> До 1950 в WPP единой глобальной сетки нет;
            возможная склейка — исторические ряды численности (в том числе Maddison Project),
            обобщённые оценки рождаемости по регионам и <em>Human Fertility Database</em>;
            неопределённость резко растёт.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
