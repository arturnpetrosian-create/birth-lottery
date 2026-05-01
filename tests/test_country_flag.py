"""Флаги и подписи стран."""
from __future__ import annotations


def test_country_title_rus_has_name() -> None:
    from domain.country_flag import country_title_ru

    t = country_title_ru("RUS", "Россия")
    assert "Россия" in t


def test_fmt_pct_chart_strips_trailing_zeros() -> None:
    # Логика дублируется в streamlit_app; проверяем эквивалент локально
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
