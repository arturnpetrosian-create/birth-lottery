"""
Оценка Population Reference Bureau: совокупное (~историческое) число рождений H. sapiens.

Используется только для сопоставлений в духе Kaneda & Haub (PRB, 2022), не путать с
«числом всех когда-либо существовавших одновременно».
"""
from __future__ import annotations

import math

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
    """До 3 значащих цифр; десятичная запятая (принято для русскоязычного UI)."""
    if share <= 0:
        return "0"
    pct = share * 100.0
    if pct >= 10:
        text = f"{pct:.2f}"
    elif pct >= 1:
        text = f"{pct:.2f}"
    else:
        text = f"{pct:.3g}"
    return text.replace(".", ",")


def round_to_n_significant(x: float, n: int = 2) -> float:
    """Округление до n значащих цифр (для величин с большой относительной погрешностью)."""
    if x == 0 or not math.isfinite(x):
        return x
    log = math.floor(math.log10(abs(x)))
    factor = 10.0 ** (log - n + 1)
    return round(x / factor) * factor


def format_uncertain_small_percent(share: float) -> str:
    """Доля 0…1 в процентах: ~2 значащие цифры, запятая — для оценок с погрешностью ±20–30 %."""
    if share <= 0:
        return "0"
    pct = share * 100.0
    body = f"{pct:.2g}".replace(".", ",")
    return f"~{body}"


def format_int_nbsp(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", "\u00a0")


def format_one_in_uncertain(recip: float) -> str:
    """Текст «примерно 1 из …» с округлением порядка величины."""
    if recip <= 0 or not math.isfinite(recip):
        return "—"
    r = round_to_n_significant(recip, 2)
    if r >= 1_000_000_000:
        b = r / 1_000_000_000
        b = round_to_n_significant(b, 2)
        return f"порядка 1 из {format_int_nbsp(b)}\u00a0млрд"
    if r >= 1_000_000:
        m = r / 1_000_000
        m = round_to_n_significant(m, 2)
        return f"примерно 1 из {format_int_nbsp(m)}\u00a0млн"
    if r >= 10_000:
        k = r / 1000
        k = round_to_n_significant(k, 2)
        return f"примерно 1 из {format_int_nbsp(k)}\u00a0тыс."
    return f"примерно 1 из {format_int_nbsp(r)}"


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
