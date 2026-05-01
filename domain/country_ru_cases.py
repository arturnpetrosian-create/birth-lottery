"""
Падежные и предложные формы названий стран для русскоязычных шаблонов.

Для стран из `data/country_cases_ru.json` задаются явные формы; для остальных —
нейтральные конструкции «в стране {номинатив из датасета}», без угадывания скопления.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=1)
def load_country_cases(path: Path | None = None) -> dict[str, dict[str, str]]:
    root = Path(__file__).resolve().parents[1]
    p = path or (root / "data" / "country_cases_ru.json")
    if not p.is_file():
        return {}
    with p.open(encoding="utf-8") as f:
        raw: dict[str, Any] = json.load(f)
    return {str(k).upper(): v for k, v in raw.items() if isinstance(v, dict)}


def in_country_where(iso: str, name_ru_nom: str) -> str:
    """Предложный контекст «где родились»: «в России», «в стране Тувалу»."""
    iso_u = iso.upper()
    row = load_country_cases().get(iso_u)
    if row and row.get("in_country"):
        return str(row["in_country"]).strip()
    return f"в стране {name_ru_nom}"


def genitive_country_share(iso: str, name_ru_nom: str) -> str:
    """Родительный для «доли … в мировом итоге», либо нейтрально «страны {ном}.»."""
    iso_u = iso.upper()
    row = load_country_cases().get(iso_u)
    if row and row.get("gen"):
        return str(row["gen"]).strip()
    return f"страны {name_ru_nom}"


def feminine_adj_country(iso: str) -> str | None:
    """Ж. прилагательное «российская доля» — только если явно задано в JSON."""
    row = load_country_cases().get(iso.upper())
    if row and row.get("adj_f"):
        return str(row["adj_f"]).strip()
    return None
