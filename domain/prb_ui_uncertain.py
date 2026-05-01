"""
Округление и подписи для блока PRB с большой относительной погрешностью.

Вынесено в отдельный модуль, чтобы приложение не зависело от полной синхронизации
`prb_ever_lived.py` на Streamlit Cloud при частичных обновлениях репозитория.
"""
from __future__ import annotations

import math


def round_to_n_significant(x: float, n: int = 2) -> float:
    """Округление до n значащих цифр."""
    if x == 0 or not math.isfinite(x):
        return x
    log = math.floor(math.log10(abs(x)))
    factor = 10.0 ** (log - n + 1)
    return round(x / factor) * factor


def format_int_nbsp(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", "\u00a0")


def format_uncertain_small_percent(share: float) -> str:
    """Доля 0…1 в процентах: ~2 значащие цифры, запятая."""
    if share <= 0:
        return "0"
    pct = share * 100.0
    body = f"{pct:.2g}".replace(".", ",")
    return f"~{body}"


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
