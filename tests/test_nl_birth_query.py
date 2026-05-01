"""Разбор свободного текста страна + год."""
from __future__ import annotations

import json
from pathlib import Path

from domain.nl_birth_query import parse_birth_description

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "births_compact.json"


def test_parse_russia_year() -> None:
    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    countries = data["countries"]
    p = parse_birth_description("я из России, 1992 год", countries, 1950, 2024)
    assert p.ok and p.iso == "RUS" and p.year == 1992


def test_parse_poland_english() -> None:
    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    p = parse_birth_description("born Poland 1980", data["countries"], 1950, 2024)
    assert p.ok and p.iso == "POL" and p.year == 1980


def test_parse_missing_year() -> None:
    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    p = parse_birth_description("только Турция", data["countries"], 1950, 2024)
    assert not p.ok and p.year is None


def test_parse_empty() -> None:
    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    p = parse_birth_description("   ", data["countries"], 1950, 2024)
    assert not p.ok
