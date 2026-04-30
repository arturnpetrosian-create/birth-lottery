# Birth Lottery — демографический атлас когортных вероятностей рождения

> Интерактивный атлас удельного веса страны в&nbsp;мировой когорте живорождений
> по&nbsp;данным **UN&nbsp;World&nbsp;Population&nbsp;Prospects&nbsp;2024** (Estimates 1950–2023 +
> Medium variant 2024). 211&nbsp;стран &times; 75&nbsp;лет = ≈&nbsp;15&nbsp;800&nbsp;country-year-наблюдений.

## О чём это

Калькулятор показывает **априорную вероятность места рождения** —
формально это доля живорождений в&nbsp;стране&nbsp;C среди всех живорождений мира
за тот же год&nbsp;Y:

```
P(C | Y) = births(C, Y) / world_births(Y)
```

Это позволяет за два контрола (год + страна) увидеть:

- удельный вес страны в **глобальной когорте новорождённых** того года;
- ранг по абсолютному числу живорождений среди ≈&nbsp;200&nbsp;стран мира;
- изотип-визуализацию (1&nbsp;000&nbsp;точек) — сколько из тысячи случайных младенцев мира родились здесь;
- интерактивную хороплет-карту (Plotly equal-earth, лог-шкала);
- кривую живорождений 1950–2024 со скользящим средним и маркером выбранного года;
- сопоставление траектории двух стран (демографическая компаративистика).

**Источник данных:** [UN World Population Prospects 2024](https://population.un.org/wpp/) —
официальные оценки Population Division, Department of Economic and Social Affairs.
Лицензия CC&nbsp;BY&nbsp;3.0&nbsp;IGO.

## Структура проекта

```
birth-lottery/
├── README.md                                                       Этот файл
├── LICENSE                                                         MIT (код) + CC BY 3.0 IGO (данные)
├── requirements.txt                                                Python-зависимости
├── .gitignore
├── .streamlit/config.toml                                          Тема Streamlit
│
├── data/
│   ├── WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx         Исходник UN WPP 2024
│   └── births_compact.json                                         Компактный датасет (~100 KB)
│
├── scripts/
│   └── build_data.py                                               XLSX UN → births_compact.json
│
├── static/
│   └── index.html                                                  Автономный одностраничник для GitHub Pages
│
├── app/
│   └── streamlit_app.py                                            Версия для Streamlit Community Cloud
│
└── docs/
    └── METHODOLOGY.md                                              Подробная методология
```

## Быстрый старт

### Streamlit-версия (рекомендуется)

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
# → http://localhost:8501
```

### Статический одностраничник

```bash
python -m http.server 8000 --directory static
# → http://localhost:8000
```

Файл `static/index.html` полностью автономный — нужен только интернет
для подгрузки шрифтов (Fraunces, JetBrains Mono) и топологии границ
с&nbsp;CDN (`world-atlas/countries-110m.json`).

### Пересборка датасета из исходного xlsx ООН

```bash
pip install -r requirements.txt
python scripts/build_data.py
# → обновит data/births_compact.json
```

## Деплой на Streamlit Community Cloud

1. Запушьте репозиторий на GitHub (публичный).
2. Зайдите на [share.streamlit.io](https://share.streamlit.io), авторизуйтесь через GitHub.
3. **New app** → выберите репозиторий и ветку.
4. Main file path: `app/streamlit_app.py`.
5. Python version: `3.11+`.
6. Deploy. Сборка занимает ≈&nbsp;1–2&nbsp;мин.

Бесплатно для публичных репозиториев. Streamlit Cloud сам прочитает
`requirements.txt` и поднимет приложение.

## Деплой на GitHub Pages (статический сайт)

```bash
git push
# Settings → Pages → Source: Deploy from a branch
# Branch: main, folder: /static
```

Через 1–2 минуты сайт будет доступен по адресу `https://<user>.github.io/<repo>/`.

## Структура `births_compact.json`

```json
{
  "metadata": {
    "source": "UN World Population Prospects 2024",
    "license": "CC BY 3.0 IGO",
    "units": "thousands of live births per year",
    "year_start": 1950,
    "year_end":   2024,
    "world": [91824, 92507, ..., 132406]
  },
  "countries": {
    "RUS": {
      "n": "Russian Federation",
      "r": "Россия",
      "g": "Europe",
      "b": [2746, 2932, ..., 1222]
    }
    // ...
  }
}
```

Доступ к числу живорождений: `b[year - 1950]` (в&nbsp;тысячах).

## Что не учтено

- **Младенческая и&nbsp;детская смертность** (U5MR). Считается чистая «лотерея места рождения»
  на момент живорождения, без поправки на выживаемость. В&nbsp;развивающихся странах
  1950-х&nbsp;годов U5MR&nbsp;могла достигать 25–30%, что заметно меняет «вероятность вырасти здесь».
- **Миграция** в первые годы жизни. Младенец, рождённый в&nbsp;C и переехавший в&nbsp;C', в нашей модели — рождённый в&nbsp;C.
- **Изменение государственных границ.** ООН ретроспективно применяет современные
  (на 2024) границы стран. То&nbsp;есть «Россия 1950» = территория РСФСР, не СССР; см. [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).
- **Малые территории** (пик &lt; 1&nbsp;000 живорождений в&nbsp;год) исключены как
  статистически шумные. Это, в&nbsp;частности, Ватикан, Токелау, Питкэрн.

## Методология

См. [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) — подробное описание
источника, методов оценки UN&nbsp;WPP (vital&nbsp;registration, переписи, DHS/MICS,
indirect&nbsp;methods), точности по&nbsp;группам стран и возможных расширений.

## Лицензии

- **Код** — MIT.
- **Данные ООН** — Creative Commons Attribution 3.0 IGO ([CC&nbsp;BY&nbsp;3.0&nbsp;IGO](https://creativecommons.org/licenses/by/3.0/igo/)).
- **Карта мира** — Natural Earth (public domain) через [`world-atlas`](https://github.com/topojson/world-atlas).
- **Шрифты** — Fraunces (OFL), JetBrains Mono (OFL).

## Стек

- Python 3.11+, pandas, openpyxl
- Streamlit + Plotly (интерактивная версия)
- D3 v7 + topojson (статическая версия)

## Цитирование

Если используете датасет или калькулятор в&nbsp;публикации, пожалуйста, цитируйте:

> United Nations, Department of Economic and Social Affairs, Population Division (2024).
> *World Population Prospects 2024.* Online Edition.
