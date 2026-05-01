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
    "украин": "UKR",
    "ukraine": "UKR",
    "беларус": "BLR",
    "belarus": "BLR",
    "казах": "KAZ",
    "казахстан": "KAZ",
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
    "армени": "ARM",
    "грузи": "GEO",
    "азербайджан": "AZE",
    "бангладеш": "BGD",
    "бразил": "BRA",
    "brazil": "BRA",
    "мексик": "MEX",
    "mexico": "MEX",
    "канада": "CAN",
    "canada": "CAN",
    "испани": "ESP",
    "spain": "ESP",
    "итали": "ITA",
    "italy": "ITA",
    "австрал": "AUS",
    "australia": "AUS",
    "египет": "EGY",
    "egypt": "EGY",
    "юар": "ZAF",
    "south africa": "ZAF",
    "пакистан": "PAK",
    "pakistan": "PAK",
    "индонез": "IDN",
    "indonesia": "IDN",
    "филиппин": "PHL",
    "philippines": "PHL",
    "вьетнам": "VNM",
    "vietnam": "VNM",
    "аргентин": "ARG",
    "argentina": "ARG",
    "коломб": "COL",
    "colombia": "COL",
    "чили": "CHL",
    "chile": "CHL",
    "перу": "PER",
    "peru": "PER",
    "норвег": "NOR",
    "norway": "NOR",
    "швед": "SWE",
    "sweden": "SWE",
    "финлянд": "FIN",
    "finland": "FIN",
    "нидерланд": "NLD",
    "netherlands": "NLD",
    "holland": "NLD",
    "бельги": "BEL",
    "belgium": "BEL",
    "австри": "AUT",
    "austria": "AUT",
    "швейцар": "CHE",
    "switzerland": "CHE",
    "ирланд": "IRL",
    "ireland": "IRL",
    "португал": "PRT",
    "portugal": "PRT",
    "грец": "GRC",
    "greece": "GRC",
    "чех": "CZE",
    "czech": "CZE",
    "венгр": "HUN",
    "hungary": "HUN",
    "румын": "ROU",
    "romania": "ROU",
    "болгар": "BGR",
    "bulgaria": "BGR",
    "хорват": "HRV",
    "croatia": "HRV",
    "серб": "SRB",
    "serbia": "SRB",
    "израил": "ISR",
    "israel": "ISR",
    "ирак": "IRQ",
    "iraq": "IRQ",
    "иран": "IRN",
    "iran": "IRN",
    "сауд": "SAU",
    "saudi": "SAU",
    "оаэ": "ARE",
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
    """Год 4 цифры; не только на границе слов — ловим 1992г, в1998 при отсутствии склейки с цифрой."""
    raw = re.findall(r"(?<!\d)(19[5-9]\d|20[0-2]\d)(?!\d)", text)
    years = [int(x) for x in raw if y_min <= int(x) <= y_max]
    return years


def _candidates_from_hints(norm: str) -> list[str]:
    found: list[str] = []
    for hint, iso in ISO_HINTS.items():
        if hint in norm:
            found.append(iso)
    return found


def _ru_place_variants(norm_key: str) -> list[str]:
    """«Бразилия» ↔ «в Бразилии», «Россия» ↔ «в России» и т.п."""
    if len(norm_key) < 3:
        return []
    out: list[str] = [norm_key]
    if norm_key.endswith("ия") and len(norm_key) >= 5:
        stem = norm_key[:-2]
        out.append(stem + "ии")
        out.append(norm_key[:-1])
    dedup: list[str] = []
    for x in out:
        if x not in dedup and len(x) >= 3:
            dedup.append(x)
    return dedup


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
            for variant in _ru_place_variants(k):
                if len(variant) < 3:
                    continue
                if variant in norm:
                    hits.append((iso, len(variant)))
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

    raw_lower = text.lower().replace("ё", "е")
    norm = _normalize(text)

    years = _extract_years(raw_lower, year_min, year_max)
    if not years:
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
