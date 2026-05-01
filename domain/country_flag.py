"""
Подписи и флаги стран (ISO 3166-1 alpha-3, как в WPP).

Заголовки: встроенный PNG (data URI из data/flags_b64.json), без внешних CDN —
Streamlit режет внешние img/эмодзи в HTML; flagcdn из РФ часто не открывается.

Виджеты и Plotly: эмодзи + локальный iso3→alpha2.
"""
from __future__ import annotations

import html
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Final

_FLAG_OVERRIDES_ALPHA3_TO_ALPHA2: Final[dict[str, str]] = {
    "XKX": "XK",
    "PSE": "PS",
    "TWN": "TW",
    "SWZ": "SZ",
}

_B64_SAFE = re.compile(r"^[A-Za-z0-9+/=]+$")


@lru_cache(maxsize=1)
def _static_alpha2_map() -> dict[str, str]:
    path = Path(__file__).resolve().parent.parent / "data" / "iso3_alpha2.json"
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {str(k).upper(): str(v).upper() for k, v in raw.items()}


@lru_cache(maxsize=1)
def _flags_b64_map() -> dict[str, str]:
    path = Path(__file__).resolve().parent.parent / "data" / "flags_b64.json"
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {str(k).upper(): str(v) for k, v in raw.items()}


def iso3166_alpha2(iso3: str) -> str | None:
    """Alpha-2 по alpha-3."""
    iso3_u = iso3.strip().upper()
    if not iso3_u or len(iso3_u) != 3:
        return None
    m = _static_alpha2_map()
    if iso3_u in m:
        return m[iso3_u]
    a2 = _FLAG_OVERRIDES_ALPHA3_TO_ALPHA2.get(iso3_u)
    if a2 is not None:
        return a2.upper()
    try:
        import pycountry

        c = pycountry.countries.get(alpha_3=iso3_u)
        if c is None or not getattr(c, "alpha_2", None):
            return None
        a2 = str(c.alpha_2)
    except ImportError:
        return None
    if len(a2) != 2 or not a2.isalpha():
        return None
    return a2.upper()


def flag_emoji_alpha3(iso3: str) -> str:
    """Региональные индикаторы Юникода (в виджетах и Plotly)."""
    a2 = iso3166_alpha2(iso3)
    if a2 is None:
        return ""
    return chr(0x1F1E6 + ord(a2[0]) - ord("A")) + chr(0x1F1E6 + ord(a2[1]) - ord("A"))


def country_label_plain(iso3: str, name_ru: str) -> str:
    """Подпись без HTML: запасной вариант с ISO3 в скобках."""
    return f"{name_ru} ({iso3.strip().upper()})"


def country_label_compact_flag(iso3: str, name_ru: str) -> str:
    """Подпись для Plotly и виджетов: эмодзи-флаг + название (без «(RUS)»), иначе plain."""
    e = flag_emoji_alpha3(iso3)
    if e:
        return f"{e}\u00a0{name_ru}"
    return country_label_plain(iso3, name_ru)


def country_heading_html(iso3: str, name_ru: str) -> str:
    """Флаг в заголовках: сначала data URI из репозитория, иначе HTTPS (на случай старого деплоя)."""
    safe_name = html.escape(name_ru)
    a2 = iso3166_alpha2(iso3)
    if a2 is None:
        return safe_name
    b64 = _flags_b64_map().get(a2)
    if b64 and _B64_SAFE.match(b64):
        src = f"data:image/png;base64,{b64}"
        src_attr = src
    else:
        src_url = f"https://flagcdn.com/w40/{a2.lower()}.png"
        src_attr = html.escape(src_url)
    return (
        f'<img src="{src_attr}" width="24" height="18" alt="" decoding="async" '
        'style="vertical-align:-4px;margin-right:8px;border-radius:2px;'
        'box-shadow:0 0 0 1px rgba(0,0,0,0.07);object-fit:cover;" />'
        f"{safe_name}"
    )


def country_title_ru(iso3: str, name_ru: str, *, flag_first: bool = True) -> str:
    """Совместимость со старым кодом: то же, что country_label_compact_flag."""
    _ = flag_first
    return country_label_compact_flag(iso3, name_ru)
