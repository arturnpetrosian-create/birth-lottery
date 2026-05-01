"""
Флаг страны по ISO 3166-1 alpha-3 (как в датасете WPP).
"""
from __future__ import annotations

# Территории, которых нет или иначе в pycountry
_FLAG_OVERRIDES_ALPHA3_TO_ALPHA2: dict[str, str] = {
    "XKX": "XK",
    "PSE": "PS",
    "TWN": "TW",
    "SWZ": "SZ",
}


def flag_emoji_alpha3(iso3: str) -> str:
    """Эмодзи флага или пустая строка, если кода нет."""
    iso3_u = iso3.strip().upper()
    if not iso3_u or len(iso3_u) != 3:
        return ""
    a2 = _FLAG_OVERRIDES_ALPHA3_TO_ALPHA2.get(iso3_u)
    if a2 is None:
        import pycountry

        c = pycountry.countries.get(alpha_3=iso3_u)
        if c is None or not getattr(c, "alpha_2", None):
            return ""
        a2 = c.alpha_2
    if len(a2) != 2 or not a2.isalpha():
        return ""
    a2 = a2.upper()
    return chr(0x1F1E6 + ord(a2[0]) - ord("A")) + chr(0x1F1E6 + ord(a2[1]) - ord("A"))


def country_title_ru(iso3: str, name_ru: str, *, flag_first: bool = True) -> str:
    """«🇷🇺 Россия» или без флага, если неизвестен код."""
    f = flag_emoji_alpha3(iso3)
    if not f:
        return name_ru
    return f"{f}\u00a0{name_ru}" if flag_first else f"{name_ru}\u00a0{f}"
