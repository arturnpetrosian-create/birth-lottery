"""
build_data.py
─────────────
Превращает оригинальный xlsx ООН в компактный JSON для веб-приложения.

Вход:   data/WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx
Выход:  data/births_compact.json

Запуск:
    python scripts/build_data.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import defaultdict

import pandas as pd

_ROOT_STR = str(Path(__file__).resolve().parent.parent)
if _ROOT_STR not in sys.path:
    sys.path.insert(0, _ROOT_STR)

from domain.historical_ever_born import (  # noqa: E402
    build_historical_calibration,
    pct_year_among_ever_born,
)

# ============================================================================
# Конфигурация путей
# ============================================================================
ROOT = Path(__file__).parent.parent
SRC_XLSX = ROOT / "data" / "WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx"
OUT_JSON = ROOT / "data" / "births_compact.json"

YEAR_MIN = 1950
YEAR_MAX = 2024

# ============================================================================
# Русские названия стран
# ============================================================================
RU_NAMES = {
    "AFG": "Афганистан", "ALB": "Албания", "DZA": "Алжир", "AND": "Андорра",
    "AGO": "Ангола", "ATG": "Антигуа и Барбуда", "ARG": "Аргентина",
    "ARM": "Армения", "AUS": "Австралия", "AUT": "Австрия", "AZE": "Азербайджан",
    "BHS": "Багамы", "BHR": "Бахрейн", "BGD": "Бангладеш", "BRB": "Барбадос",
    "BLR": "Беларусь", "BEL": "Бельгия", "BLZ": "Белиз", "BEN": "Бенин",
    "BTN": "Бутан", "BOL": "Боливия", "BIH": "Босния и Герцеговина",
    "BWA": "Ботсвана", "BRA": "Бразилия", "BRN": "Бруней", "BGR": "Болгария",
    "BFA": "Буркина-Фасо", "BDI": "Бурунди", "CPV": "Кабо-Верде",
    "KHM": "Камбоджа", "CMR": "Камерун", "CAN": "Канада", "CAF": "ЦАР",
    "TCD": "Чад", "CHL": "Чили", "CHN": "Китай", "COL": "Колумбия",
    "COM": "Коморы", "COG": "Конго", "COD": "ДР Конго", "CRI": "Коста-Рика",
    "CIV": "Кот-д'Ивуар", "HRV": "Хорватия", "CUB": "Куба", "CYP": "Кипр",
    "CZE": "Чехия", "DNK": "Дания", "DJI": "Джибути", "DMA": "Доминика",
    "DOM": "Доминиканская Респ.", "ECU": "Эквадор", "EGY": "Египет",
    "SLV": "Сальвадор", "GNQ": "Экв. Гвинея", "ERI": "Эритрея",
    "EST": "Эстония", "SWZ": "Эсватини", "ETH": "Эфиопия", "FJI": "Фиджи",
    "FIN": "Финляндия", "FRA": "Франция", "GAB": "Габон", "GMB": "Гамбия",
    "GEO": "Грузия", "DEU": "Германия", "GHA": "Гана", "GRC": "Греция",
    "GRD": "Гренада", "GTM": "Гватемала", "GIN": "Гвинея", "GNB": "Гвинея-Бисау",
    "GUY": "Гайана", "HTI": "Гаити", "HND": "Гондурас", "HUN": "Венгрия",
    "ISL": "Исландия", "IND": "Индия", "IDN": "Индонезия", "IRN": "Иран",
    "IRQ": "Ирак", "IRL": "Ирландия", "ISR": "Израиль", "ITA": "Италия",
    "JAM": "Ямайка", "JPN": "Япония", "JOR": "Иордания", "KAZ": "Казахстан",
    "KEN": "Кения", "KIR": "Кирибати", "PRK": "Северная Корея",
    "KOR": "Южная Корея", "KWT": "Кувейт", "KGZ": "Киргизия", "LAO": "Лаос",
    "LVA": "Латвия", "LBN": "Ливан", "LSO": "Лесото", "LBR": "Либерия",
    "LBY": "Ливия", "LIE": "Лихтенштейн", "LTU": "Литва", "LUX": "Люксембург",
    "MDG": "Мадагаскар", "MWI": "Малави", "MYS": "Малайзия", "MDV": "Мальдивы",
    "MLI": "Мали", "MLT": "Мальта", "MHL": "Маршалловы Острова",
    "MRT": "Мавритания", "MUS": "Маврикий", "MEX": "Мексика",
    "FSM": "Микронезия", "MDA": "Молдова", "MCO": "Монако", "MNG": "Монголия",
    "MNE": "Черногория", "MAR": "Марокко", "MOZ": "Мозамбик", "MMR": "Мьянма",
    "NAM": "Намибия", "NRU": "Науру", "NPL": "Непал", "NLD": "Нидерланды",
    "NZL": "Новая Зеландия", "NIC": "Никарагуа", "NER": "Нигер",
    "NGA": "Нигерия", "MKD": "Северная Македония", "NOR": "Норвегия",
    "OMN": "Оман", "PAK": "Пакистан", "PLW": "Палау", "PSE": "Палестина",
    "PAN": "Панама", "PNG": "Папуа — Новая Гвинея", "PRY": "Парагвай",
    "PER": "Перу", "PHL": "Филиппины", "POL": "Польша", "PRT": "Португалия",
    "QAT": "Катар", "ROU": "Румыния", "RUS": "Россия", "RWA": "Руанда",
    "KNA": "Сент-Китс и Невис", "LCA": "Сент-Люсия", "VCT": "Сент-Винсент",
    "WSM": "Самоа", "SMR": "Сан-Марино", "STP": "Сан-Томе",
    "SAU": "Саудовская Аравия", "SEN": "Сенегал", "SRB": "Сербия",
    "SYC": "Сейшелы", "SLE": "Сьерра-Леоне", "SGP": "Сингапур",
    "SVK": "Словакия", "SVN": "Словения", "SLB": "Соломоновы Острова",
    "SOM": "Сомали", "ZAF": "ЮАР", "SSD": "Южный Судан", "ESP": "Испания",
    "LKA": "Шри-Ланка", "SDN": "Судан", "SUR": "Суринам", "SWE": "Швеция",
    "CHE": "Швейцария", "SYR": "Сирия", "TJK": "Таджикистан",
    "TZA": "Танзания", "THA": "Таиланд", "TLS": "Восточный Тимор",
    "TGO": "Того", "TON": "Тонга", "TTO": "Тринидад и Тобаго",
    "TUN": "Тунис", "TUR": "Турция", "TKM": "Туркмения", "TUV": "Тувалу",
    "UGA": "Уганда", "UKR": "Украина", "ARE": "ОАЭ",
    "GBR": "Великобритания", "USA": "США", "URY": "Уругвай",
    "UZB": "Узбекистан", "VUT": "Вануату", "VEN": "Венесуэла",
    "VNM": "Вьетнам", "YEM": "Йемен", "ZMB": "Замбия", "ZWE": "Зимбабве",
    # Зависимые территории и автономии с заметным населением
    "PRI": "Пуэрто-Рико", "HKG": "Гонконг", "MAC": "Макао", "TWN": "Тайвань",
    "REU": "Реюньон", "NCL": "Новая Каледония",
    "PYF": "Французская Полинезия", "GUF": "Французская Гвиана",
    "MTQ": "Мартиника", "GLP": "Гваделупа", "CUW": "Кюрасао", "ABW": "Аруба",
    "GIB": "Гибралтар", "BMU": "Бермуды", "CYM": "Каймановы Острова",
    "TCA": "Теркс и Кайкос", "FRO": "Фарерские острова", "GRL": "Гренландия",
    "VIR": "Виргинские о-ва (США)", "GUM": "Гуам",
    "ASM": "Американское Самоа", "MNP": "Сев. Марианские о-ва",
    "COK": "Острова Кука", "NIU": "Ниуэ", "TKL": "Токелау",
    "WLF": "Уоллис и Футуна", "SHN": "Святая Елена", "FLK": "Фолкленды",
    "ESH": "Зап. Сахара", "AIA": "Ангилья", "MSR": "Монтсеррат",
    "VGB": "Виргинские о-ва (Брит.)", "SXM": "Синт-Мартен",
    "BES": "Карибские Нидерланды", "MAF": "Сен-Мартен",
    "BLM": "Сен-Бартелеми", "SPM": "Сен-Пьер", "MYT": "Майотта",
    "IMN": "О. Мэн", "JEY": "Джерси", "GGY": "Гернси",
    "CXR": "О. Рождества", "CCK": "Кокосовые острова", "NFK": "О. Норфолк",
    "XKX": "Косово",
}

# Региональная классификация (geoscheme — упрощённая)
REGIONS = {
    "Africa": [
        "DZA", "AGO", "BEN", "BWA", "BFA", "BDI", "CPV", "CMR", "CAF", "TCD",
        "COM", "COG", "COD", "CIV", "DJI", "EGY", "GNQ", "ERI", "SWZ", "ETH",
        "GAB", "GMB", "GHA", "GIN", "GNB", "KEN", "LSO", "LBR", "LBY", "MDG",
        "MWI", "MLI", "MRT", "MUS", "MAR", "MOZ", "NAM", "NER", "NGA", "RWA",
        "STP", "SEN", "SYC", "SLE", "SOM", "ZAF", "SSD", "SDN", "TZA", "TGO",
        "TUN", "UGA", "ZMB", "ZWE", "REU", "MYT", "ESH", "SHN",
    ],
    "Asia": [
        "AFG", "ARM", "AZE", "BHR", "BGD", "BTN", "BRN", "KHM", "CHN", "CYP",
        "GEO", "IND", "IDN", "IRN", "IRQ", "ISR", "JPN", "JOR", "KAZ", "KWT",
        "KGZ", "LAO", "LBN", "MYS", "MDV", "MNG", "MMR", "NPL", "PRK", "OMN",
        "PAK", "PSE", "PHL", "QAT", "SAU", "SGP", "KOR", "LKA", "SYR", "TJK",
        "THA", "TLS", "TUR", "TKM", "ARE", "UZB", "VNM", "YEM", "HKG", "MAC", "TWN",
    ],
    "Europe": [
        "ALB", "AND", "AUT", "BLR", "BEL", "BIH", "BGR", "HRV", "CZE", "DNK",
        "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "ISL", "IRL", "ITA", "LVA",
        "LIE", "LTU", "LUX", "MLT", "MDA", "MCO", "MNE", "NLD", "MKD", "NOR",
        "POL", "PRT", "ROU", "RUS", "SMR", "SRB", "SVK", "SVN", "ESP", "SWE",
        "CHE", "UKR", "GBR", "FRO", "GIB", "IMN", "JEY", "GGY", "XKX",
    ],
    "Americas": [
        "ATG", "ARG", "BHS", "BRB", "BLZ", "BOL", "BRA", "CAN", "CHL", "COL",
        "CRI", "CUB", "DMA", "DOM", "ECU", "SLV", "GRD", "GTM", "GUY", "HTI",
        "HND", "JAM", "MEX", "NIC", "PAN", "PRY", "PER", "KNA", "LCA", "VCT",
        "SUR", "TTO", "USA", "URY", "VEN", "PRI", "VIR", "GUF", "MTQ", "GLP",
        "CUW", "ABW", "BMU", "CYM", "TCA", "GRL", "AIA", "MSR", "VGB", "SXM",
        "BES", "MAF", "BLM", "SPM", "FLK",
    ],
    "Oceania": [
        "AUS", "FJI", "KIR", "MHL", "FSM", "NRU", "NZL", "PLW", "PNG", "WSM",
        "SLB", "TON", "TUV", "VUT", "NCL", "PYF", "GUM", "ASM", "MNP", "COK",
        "NIU", "TKL", "WLF", "NFK", "CXR", "CCK",
    ],
}
ISO_TO_REGION = {iso: region for region, isos in REGIONS.items() for iso in isos}


def _world_population_july_2024_thousands(df_all: pd.DataFrame) -> float | None:
    """Численность «World» на 1 июля 2024 (тысячи человек), если колонка есть в xlsx."""
    name_col = "Region, subregion, country or area *"
    pop_col = None
    for col in df_all.columns:
        label = str(col)
        if "Total Population" in label and "1 July" in label and "thousands" in label.lower():
            pop_col = col
            break
    if pop_col is None:
        return None
    world = df_all[
        (df_all[name_col] == "World") & (df_all["Year"].astype(int) == YEAR_MAX)
    ]
    if world.empty:
        return None
    raw = world.iloc[0][pop_col]
    if pd.isna(raw):
        return None
    return float(raw)


# ============================================================================
# Основная функция сборки
# ============================================================================
def build() -> dict:
    if not SRC_XLSX.exists():
        sys.exit(
            f"\n❌ Не нашёл исходник: {SRC_XLSX}\n"
            f"   Скачайте его с https://population.un.org/wpp/downloads "
            f"(файл WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx) "
            f"и положите в data/.\n"
        )

    print(f"📖 Читаю {SRC_XLSX.name}...")
    estimates = pd.read_excel(SRC_XLSX, sheet_name="Estimates", header=16)
    medium = pd.read_excel(SRC_XLSX, sheet_name="Medium variant", header=16)
    df_all = pd.concat([estimates, medium], ignore_index=True)

    countries_df = df_all[df_all["Type"] == "Country/Area"].copy()
    print(f"   найдено {countries_df['ISO3 Alpha-code'].nunique()} стран/территорий")

    # Извлекаем нужные колонки
    keep = ["ISO3 Alpha-code", "Region, subregion, country or area *", "Year",
            "Births (thousands)"]
    df = countries_df[keep].copy()
    df.columns = ["iso3", "name", "year", "births"]
    df = df.dropna(subset=["iso3", "births"])
    df["year"] = df["year"].astype(int)
    df = df[(df["year"] >= YEAR_MIN) & (df["year"] <= YEAR_MAX)]

    # Мировые тоталы — из строк World
    world_df = df_all[df_all["Region, subregion, country or area *"] == "World"][
        ["Year", "Births (thousands)"]
    ].copy()
    world_df.columns = ["year", "births"]
    world_df["year"] = world_df["year"].astype(int)
    world_df = world_df[
        (world_df["year"] >= YEAR_MIN) & (world_df["year"] <= YEAR_MAX)
    ]
    world_arr = [
        int(round(world_df[world_df["year"] == y]["births"].iloc[0]))
        for y in range(YEAR_MIN, YEAR_MAX + 1)
    ]

    # По странам
    per_country = defaultdict(dict)
    names = {}
    for _, row in df.iterrows():
        iso = row["iso3"]
        if pd.isna(iso):
            continue
        per_country[iso][row["year"]] = round(float(row["births"]), 1)
        names.setdefault(iso, row["name"])

    # Фильтрация: только страны с пиком >= 1k рождений (исключает Ватикан и т.п.)
    valid = {
        iso: yrs for iso, yrs in per_country.items()
        if max(yrs.values()) >= 1.0 and len(yrs) >= 50
    }
    print(f"   после фильтрации малых территорий: {len(valid)} стран")

    world_births_sum_persons = int(round(sum(world_arr) * 1000.0))
    pop2024k = _world_population_july_2024_thousands(df_all)

    meta: dict = {
        "source": "UN World Population Prospects 2024",
        "citation": (
            "United Nations, Department of Economic and Social Affairs, "
            "Population Division (2024). World Population Prospects 2024."
        ),
        "license": "CC BY 3.0 IGO",
        "units": "thousands of live births per year",
        "year_start": YEAR_MIN,
        "year_end": YEAR_MAX,
        "world": world_arr,
        "world_births_sum_1950_2024_persons": world_births_sum_persons,
    }
    if pop2024k is not None:
        meta["world_population_july_2024_thousands"] = round(pop2024k, 1)

    # Сборка финального компактного словаря
    out = {
        "metadata": meta,
        "countries": {},
    }

    skipped = []
    for iso, yrs in valid.items():
        if iso not in RU_NAMES:
            skipped.append((iso, names.get(iso, "?")))
            continue
        arr = []
        for y in range(YEAR_MIN, YEAR_MAX + 1):
            v = yrs.get(y, 0)
            arr.append(round(v, 0) if v >= 10 else round(v, 1))
        out["countries"][iso] = {
            "n": names.get(iso, iso),
            "r": RU_NAMES[iso],
            "g": ISO_TO_REGION.get(iso, "Other"),
            "b": arr,
        }

    if skipped:
        print(f"   ⚠️  пропущено без русского имени: {skipped}")

    print(f"   итого {len(out['countries'])} стран в JSON")

    world_f = [float(x) for x in world_arr]
    historical = pct_year_among_ever_born(world_f)
    historical["calibration_pre_1950"] = build_historical_calibration(world_f)
    out["historical_ever_born"] = historical
    print("   добавлен блок historical_ever_born (доля года среди всех родившихся)")

    return out


def main():
    out = build()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    sz_kb = OUT_JSON.stat().st_size / 1024
    print(f"\n✅ Записано в {OUT_JSON} ({sz_kb:.1f} KB)")

    # Sanity-check
    print("\n🔬 Проверка значений (по официальным данным UN WPP 2024):")
    for iso, year in [("RUS", 1992), ("USA", 1985), ("JPN", 1950),
                      ("CHN", 2000), ("IND", 2024), ("ARM", 1990)]:
        c = out["countries"][iso]
        b_thousands = c["b"][year - YEAR_MIN]
        w_thousands = out["metadata"]["world"][year - YEAR_MIN]
        pct = b_thousands / w_thousands * 100
        print(
            f"   {iso} {year}: {b_thousands * 1000:>13,.0f} рождений, "
            f"{pct:.3f}% мира, 1 из {w_thousands / b_thousands:,.0f}"
        )


if __name__ == "__main__":
    main()
