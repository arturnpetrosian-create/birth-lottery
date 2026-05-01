"""Флаги и подписи стран."""
from __future__ import annotations


def test_country_label_plain_uses_alpha3_suffix() -> None:
    from domain.country_flag import country_label_plain

    t = country_label_plain("RUS", "Россия")
    assert t == "Россия (RUS)"


def test_iso3166_alpha2_known() -> None:
    from domain.country_flag import iso3166_alpha2

    assert iso3166_alpha2("RUS") == "RU"
    assert iso3166_alpha2("USA") == "US"


def test_country_heading_html_uses_no_external_cdn() -> None:
    from domain.country_flag import country_heading_html

    h = country_heading_html("DEU", "Германия")
    assert "Германия" in h
    assert "flagcdn" not in h.lower()
    assert "http" not in h.lower()


def test_country_title_ru_matches_compact_flag() -> None:
    from domain.country_flag import country_label_compact_flag, country_title_ru

    assert country_title_ru("FRA", "Франция") == country_label_compact_flag("FRA", "Франция")


def test_country_label_compact_flag_includes_name() -> None:
    from domain.country_flag import country_label_compact_flag

    t = country_label_compact_flag("RUS", "Россия")
    assert "Россия" in t
    assert len(t) >= len("Россия")


def test_fmt_pct_chart_strips_trailing_zeros() -> None:
    import math

    def fmt_pct_chart(p: float) -> str:
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

    assert fmt_pct_chart(15.0) == "15"
    assert fmt_pct_chart(15.5) == "15,5"
    assert fmt_pct_chart(0.12) == "0,12"
