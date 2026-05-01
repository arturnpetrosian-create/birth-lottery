"""
«Вероятность года» среди всех когда-либо родившихся.

Для года Y из диапазона ООН WPP (здесь 1950–2024) при оценке общего числа всех
родившихся за историю N:

    P(Y) ≈ B_world(Y) / N,

где B_world — мировые живорождения за год (человек). Это согласовано с полным
распределением, если остальные годы получают оставшуюся массу (N − Σ B_world).

Интервал задаётся тремя сценариями N (консервативный / центральный / верхний)
по порядку величины из обзоров PRB и смежных публикаций (часто цитируют ~117 млрд).

Гладкая кривая до 1950 (для калибровки и будущих расширений) документирована
в build_historical_calibration().
"""
from __future__ import annotations

from typing import Any

_TOTAL_EVER_LOW = 96.0e9
_TOTAL_EVER_CENTRAL = 117.0e9
_TOTAL_EVER_HIGH = 127.0e9

_DEFAULT_ANCHORS: list[tuple[int, float]] = [
    (1, 5.5),
    (500, 6.5),
    (1000, 8.0),
    (1500, 11.0),
    (1700, 17.0),
    (1750, 21.0),
    (1800, 28.0),
    (1850, 36.0),
    (1900, 52.0),
    (1920, 61.0),
    (1935, 71.0),
    (1949, 87.0),
]


def _interp_millions_per_year(year: int, nodes: list[tuple[int, float]]) -> float:
    if year <= nodes[0][0]:
        return float(nodes[0][1])
    if year >= nodes[-1][0]:
        return float(nodes[-1][1])
    for i in range(len(nodes) - 1):
        y0, v0 = nodes[i]
        y1, v1 = nodes[i + 1]
        if y0 <= year <= y1 and y1 != y0:
            t = (year - y0) / (y1 - y0)
            return float(v0 + t * (v1 - v0))
    return float(nodes[-1][1])


def build_historical_calibration(
    world_thousands: list[float],
    year_start: int = 1950,
    anchors: list[tuple[int, float]] | None = None,
) -> dict[str, Any]:
    """Калибровка модели до 1950: масштаб s к фиксированному N (центральный сценарий)."""
    nodes = anchors if anchors is not None else list(_DEFAULT_ANCHORS)
    sum_un = sum(world_thousands) * 1000.0
    raw_pre = [
        _interp_millions_per_year(y, nodes) * 1.0e6 for y in range(1, year_start)
    ]
    sum_pre_raw = sum(raw_pre)
    tot = _TOTAL_EVER_CENTRAL
    scale = (tot - sum_un) / sum_pre_raw if sum_pre_raw > 0 else 0.0
    sum_pre_fitted = scale * sum_pre_raw
    share_un = sum_un / tot
    share_pre = sum_pre_fitted / tot
    return {
        "year_start_un": year_start,
        "sum_un_persons": sum_un,
        "sum_pre_1950_model_persons": sum_pre_fitted,
        "scale_pre_1950": scale,
        "total_central_persons": tot,
        "share_un_in_total": share_un,
        "share_pre_1950_in_total": share_pre,
    }


def pct_year_among_ever_born(
    world_thousands: list[float],
) -> dict[str, Any]:
    """
    Доли каждого года UN-диапазона среди всех родившихся (три сценария N).
    Индекс i соответствует году 1950 + i.
    """
    sum_un = sum(world_thousands) * 1000.0
    if sum_un >= _TOTAL_EVER_LOW:
        raise ValueError("Нижняя оценка N должна быть больше суммы живорождений ООН.")
    lows: list[float] = []
    mids: list[float] = []
    highs: list[float] = []
    for wk in world_thousands:
        b = float(wk * 1000.0)
        lows.append(b / _TOTAL_EVER_LOW)
        mids.append(b / _TOTAL_EVER_CENTRAL)
        highs.append(b / _TOTAL_EVER_HIGH)
    return {
        "description_ru": (
            "Доля календарного года среди всех когда-либо родившихся: отношение мировых "
            "живорождений года (ООН WPP) к выбранной оценке числа всех родившихся."
        ),
        "caution_ru": (
            "Оценки N расходятся между авторами на десятки процентов; до середины XX века "
            "нет единой глобальной регистрации — используйте интервал как порядок неопределённости, "
            "а не доверительный интервал в статистическом смысле."
        ),
        "total_ever_born_persons": {
            "low": _TOTAL_EVER_LOW,
            "central": _TOTAL_EVER_CENTRAL,
            "high": _TOTAL_EVER_HIGH,
        },
        "sum_un_persons": sum_un,
        "share_of_all_births_un_years_in_central": sum_un / _TOTAL_EVER_CENTRAL,
        "pct_year": {"low": lows, "central": mids, "high": highs},
    }
