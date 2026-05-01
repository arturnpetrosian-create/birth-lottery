"""
Разбор свободного текста «где и когда родился» для подстановки в расчёты WPP.

Без вызова внешних LLM: эвристики и сопоставление с каталогом стран датасета.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Частые обращения → ISO3 (современные границы ООН в датасете)
ISO_HINTS: dict[str, str] = {
    "рф": "RUS",
    "россии": "RUS",
    "россия": "RUS",
    "рсфср": "RUS",
    "ссср": "RUS",
    "soviet": "RUS",
    "russia": "RUS",
    "ukraine": "UKR",
    "украин": "UKR",
    "беларус": "BLR",
    "belarus": "BLR",
    "казах": "KAZ",
    "узбек": "UZB",
    "сша": "USA",
    "америк": "USA",
    "usa": "USA",
    "united states": "USA",
    "кита": "CHN",
    "china": "CHN",
    "индии": "IND",
    "индия": "IND",
    "india": "IND",
    "герман": "DEU",
    "germany": "DEU",
    "франц": "FRA",
    "france": "FRA",
    "польш": "POL",
    "poland": "POL",
    "япон": "JPN",
    "japan": "JPN",
    "турц": "TUR",
    "turkey": "TUR",
    "британ": "GBR",
    "uk": "GBR",
    "англи": "GBR",
    "казахстан": "KAZ",
    "армени": "ARM",
    "грузи": "GEO",
    "азербайджан": "AZE",
    "бангладеш": "BGD",
}


@dataclass(frozen=True)
class ParsedBirthQuery:
    """Результат разбора пользовательской фразы."""

    year: int | None
    iso: str | None
    country_ru: str | None
    ok: bool
    message_ru: str


def _normalize(text: str) -> str:
    t = text.lower().replace("ё", "е")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _extract_years(text: str, y_min: int, y_max: int) -> list[int]:
    raw = re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", text)
    years = [int(x) for x in raw if y_min <= int(x) <= y_max]
    return years


def _candidates_from_hints(norm: str) -> list[str]:
    found: list[str] = []
    for hint, iso in ISO_HINTS.items():
        if hint in norm:
            found.append(iso)
    return found


def _candidates_from_catalog(norm: str, countries: dict[str, dict[str, Any]]) -> list[tuple[str, int]]:
    """Пары (iso, длина совпавшей подстроки)."""
    hits: list[tuple[str, int]] = []
    for iso, rec in countries.items():
        for key in (rec.get("r") or "", rec.get("n") or ""):
            if not key:
                continue
            k = _normalize(key)
            if len(k) < 3:
                continue
            if k in norm:
                hits.append((iso, len(k)))
    hits.sort(key=lambda x: -x[1])
    return hits


def parse_birth_description(
    text: str,
    countries: dict[str, dict[str, Any]],
    year_min: int,
    year_max: int,
) -> ParsedBirthQuery:
    if not text or not text.strip():
        return ParsedBirthQuery(
            year=None,
            iso=None,
            country_ru=None,
            ok=False,
            message_ru="Напишите одну-две фразы: страна (как вам удобно) и год рождения, например: «Россия, 1992» или «родился в Польше в 1980».",
        )

    norm = _normalize(text)
    years = _extract_years(norm, year_min, year_max)
    if not years:
        return ParsedBirthQuery(
            year=None,
            iso=None,
            country_ru=None,
            ok=False,
            message_ru=f"Не нашёл год в диапазоне {year_min}–{year_max}. Добавьте четырёхзначный год, например 1997.",
        )

    year = years[-1]

    iso_set: list[str] = []
    iso_set.extend(_candidates_from_hints(norm))
    catalog_hits = _candidates_from_catalog(norm, countries)
    if catalog_hits:
        best_len = catalog_hits[0][1]
        iso_set.extend(iso for iso, ln in catalog_hits if ln == best_len)
    uniq: list[str] = []
    for i in iso_set:
        if i not in uniq:
            uniq.append(i)

    if not uniq:
        return ParsedBirthQuery(
            year=year,
            iso=None,
            country_ru=None,
            ok=False,
            message_ru="Страну не распознал. Попробуйте официальное русское название (например «Япония») или ISO3 в латинице (JPN).",
        )

    if len(uniq) > 1:
        labels = [countries[i]["r"] for i in uniq[:5]]
        return ParsedBirthQuery(
            year=year,
            iso=None,
            country_ru=None,
            ok=False,
            message_ru="Подходит несколько стран: " + ", ".join(labels) + ". Уточните формулировку.",
        )

    iso = uniq[0]
    return ParsedBirthQuery(
        year=year,
        iso=iso,
        country_ru=countries[iso]["r"],
        ok=True,
        message_ru=f"Применено: **{countries[iso]['r']}**, **{year}** — поля года и страны обновлены.",
    )
