"""
Оценка Population Reference Bureau: совокупное (~историческое) число рождений H. sapiens.

Используется только для сопоставлений в духе Kaneda & Haub (PRB, 2022), не путать с
«числом всех когда-либо существовавших одновременно».
"""
from __future__ import annotations

#: Совокупное число рождений с ~190 000 г. до н.э. до середины 2022 г. по PRB.
#: См. Kaneda & Haub, «How Many People Have Ever Lived on Earth?», PRB, 2022.
EVER_LIVED_PRB_2022: int = 117_000_000_000

PRB_ARTICLE_TITLE_RU = (
    "How Many People Have Ever Lived on Earth? (Population Reference Bureau, 2022)"
)
PRB_ARTICLE_URL: str = "https://www.prb.org/articles/how-many-people-have-ever-lived-on-earth/"

#: Ориентир доли ныне живущих среди всех когда-либо родившихся (PRB используют ~8 млрд / 117 млрд).
#: В интерфейсе приоритетно брать численность из метаданных WPP (метка 2024), если есть.
PRB_ROUGH_POPULATION_FOR_SHARE_2022: int = 8_000_000_000


def share_of_prb_total(births_persons: float, *, total: int = EVER_LIVED_PRB_2022) -> float:
    if total <= 0:
        raise ValueError("total must be positive")
    return births_persons / float(total)


def one_in_reciprocal(share: float) -> float:
    if share <= 0:
        return float("inf")
    return 1.0 / share


def format_tiny_percent(share: float) -> str:
    pct = share * 100.0
    if pct >= 0.01:
        return f"{pct:.6f}"
    if pct >= 0.001:
        return f"{pct:.7f}"
    return f"{pct:.8f}"


def humanize_one_in(recip: float) -> str:
    """Текст вида «~1 из 4,5 млн» / «~1 из 1,2 млрд» для очень больших N."""
    if recip <= 0 or recip == float("inf"):
        return "—"
    if recip < 1_000:
        return f"≈\u00a01\u00a0из\u00a0{recip:.0f}".replace(",", "\u00a0")
    if recip < 1_000_000:
        return f"≈\u00a01\u00a0из\u00a0{recip:,.0f}".replace(",", "\u00a0")
    if recip < 1_000_000_000:
        m = recip / 1_000_000
        return f"≈\u00a01\u00a0из\u00a0{m:.2f}\u00a0млн".replace(",", "\u00a0")
    b = recip / 1_000_000_000
    return f"≈\u00a01\u00a0из\u00a0{b:.2f}\u00a0млрд".replace(",", "\u00a0")
