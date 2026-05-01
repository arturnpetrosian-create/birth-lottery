"""Проверки компактного датасета приложения."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from domain.prb_ever_lived import EVER_LIVED_PRB_2022

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "births_compact.json"


@pytest.fixture(scope="module")
def dataset() -> dict:
    assert DATA_PATH.is_file(), f"Нет файла {DATA_PATH}"
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_ever_lived_constant_is_prb_2022() -> None:
    assert EVER_LIVED_PRB_2022 == 117_000_000_000


def test_all_countries_have_full_series(dataset: dict) -> None:
    meta = dataset["metadata"]
    y0, y1 = meta["year_start"], meta["year_end"]
    span = y1 - y0 + 1
    for iso, rec in dataset["countries"].items():
        assert len(rec["b"]) == span, f"{iso}: длина {len(rec['b'])} != {span}"


def test_country_sum_vs_world_recent_year(dataset: dict) -> None:
    meta = dataset["metadata"]
    y0 = meta["year_start"]
    yi = 1992 - y0
    w = meta["world"][yi]
    s = sum(dataset["countries"][k]["b"][yi] for k in dataset["countries"])
    assert s / w >= 0.95, f"сумма стран / мир = {s/w}"


def test_benchmark_births(dataset: dict) -> None:
    meta = dataset["metadata"]
    y0 = meta["year_start"]

    def row(iso: str, year: int) -> float:
        return float(dataset["countries"][iso]["b"][year - y0])

    assert row("RUS", 1992) == pytest.approx(1621.4, abs=1.0)
    assert row("USA", 1985) == pytest.approx(3844.1, abs=1.0)
    assert row("JPN", 1950) == pytest.approx(2461.5, abs=1.0)


def test_format_tiny_percent_compact_ru() -> None:
    from domain.prb_ever_lived import format_tiny_percent

    assert "," in format_tiny_percent(1.106e-5)
    assert len(format_tiny_percent(1.106e-5)) <= 8
    assert format_tiny_percent(0.15).replace(",", ".") == "15.00"


def test_metadata_world_births_sum_present(dataset: dict) -> None:
    meta = dataset["metadata"]
    assert "world_births_sum_1950_2024_persons" in meta
    expect = int(round(sum(meta["world"]) * 1000))
    assert meta["world_births_sum_1950_2024_persons"] == expect
