"""
Подписи и флаги стран (ISO 3166-1 alpha-3, как в WPP).

Флаги в виде эмодзи на части систем (Windows) дают «двухбуквенный» вид;
в интерфейсе для заголовков используем изображения (flagcdn).
"""
from __future__ import annotations

import html
from typing import Final

_FLAG_OVERRIDES_ALPHA3_TO_ALPHA2: Final[dict[str, str]] = {
    "XKX": "XK",
    "PSE": "PS",
    "TWN": "TW",
    "SWZ": "SZ",
}


def iso3166_alpha2(iso3: str) -> str | None:
    """Alpha-2 по alpha-3; для URL флагов и эмодзи."""
    iso3_u = iso3.strip().upper()
    if not iso3_u or len(iso3_u) != 3:
        return None
    a2 = _FLAG_OVERRIDES_ALPHA3_TO_ALPHA2.get(iso3_u)
    if a2 is None:
        import pycountry

        c = pycountry.countries.get(alpha_3=iso3_u)
        if c is None or not getattr(c, "alpha_2", None):
            return None
        a2 = str(c.alpha_2)
    if len(a2) != 2 or not a2.isalpha():
        return None
    return a2.upper()


def flag_emoji_alpha3(iso3: str) -> str:
    """Региональные индикаторы Юникода (на части ОС выглядят как буквенные коды)."""
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
    """Заголовок с флагом-картинкой для st.markdown(..., unsafe_allow_html=True)."""
    a2 = iso3166_alpha2(iso3)
    safe_name = html.escape(name_ru)
    if a2 is None:
        return safe_name
    src = f"https://flagcdn.com/w40/{a2.lower()}.png"
    return (
        f'<img src="{html.escape(src)}" width="26" height="20" alt="" loading="lazy" '
        'referrerpolicy="no-referrer-when-downgrade" '
        'style="vertical-align:-4px;margin-right:8px;border-radius:2px;'
        'box-shadow:0 0 0 1px rgba(0,0,0,0.07);object-fit:cover;" />'
        f"{safe_name}"
    )


def country_title_ru(iso3: str, name_ru: str, *, flag_first: bool = True) -> str:
    """Совместимость со старым кодом: то же, что country_label_compact_flag."""
    _ = flag_first
    return country_label_compact_flag(iso3, name_ru)
