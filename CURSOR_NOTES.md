# Подсказки для Cursor / AI-агента

> Этот файл — для AI-ассистента (Cursor, Claude Code, etc.), которому
> отдают этот проект. Содержит контекст и типичные задачи.

## Что это за проект

Демографический калькулятор «Лотерея рождения». Показывает вероятность
случайному младенцу родиться в данной стране в данном году, на данных
UN World Population Prospects 2024.

Две версии:
- `static/index.html` — автономный одностраничник (HTML/CSS/vanilla JS +
  d3-geo через CDN). Деплоится на GitHub Pages.
- `app/streamlit_app.py` — Streamlit-приложение. Деплоится на Streamlit
  Community Cloud.

Обе используют один и тот же `data/births_compact.json`, который генерируется
из `data/WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx` скриптом
`scripts/build_data.py`.

## Сначала проверь, что всё работает

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Пересобрать данные (необязательно — JSON уже в репо)
python scripts/build_data.py

# 3. Запустить статический сайт локально
python -m http.server 8000 --directory static
# открыть http://localhost:8000

# 4. Запустить Streamlit
streamlit run app/streamlit_app.py
```

## Типичные задачи

### Деплой на GitHub

```bash
git init
git add .
git commit -m "Initial commit"
gh repo create birth-lottery --public --source=. --push
# или вручную: создать репо на github.com и
# git remote add origin https://github.com/USER/birth-lottery.git
# git push -u origin main
```

### Включить GitHub Pages

1. Settings → Pages
2. Source: **Deploy from a branch**
3. Branch: `main`, folder: `/static`
4. Save

Сайт будет на `https://USER.github.io/birth-lottery/`.

### Деплой Streamlit

1. Зайти на https://share.streamlit.io
2. New app → выбрать репо
3. **Main file path: `app/streamlit_app.py`**
4. **Python version: 3.11+**
5. Deploy

### Изменить данные / страны / годы

- Редактировать `scripts/build_data.py`:
  - `RU_NAMES` — русские названия стран (словарь ISO3 → имя)
  - `REGIONS` — региональная классификация
  - `YEAR_MIN`, `YEAR_MAX` — диапазон лет
- Запустить `python scripts/build_data.py`
- `data/births_compact.json` обновится автоматически

### Изменить дизайн HTML-версии

Все стили и JS внутри `static/index.html` (одним файлом — это намеренно,
чтобы он работал с GitHub Pages без ассетов).

CSS-переменные палитры в начале `<style>`:
```css
--paper: #f4ecd8;
--terracotta: #b8492f;
--ink: #2a1810;
/* и т.д. */
```

### Изменить дизайн Streamlit-версии

`app/streamlit_app.py` — стили в первом `st.markdown(... unsafe_allow_html=True)`.
Цвета темы — в `.streamlit/config.toml`.

## Известные подводные камни

1. **Не удалять `data/births_compact.json`.** Streamlit-версия его читает
   напрямую и не запускает build при деплое.
2. **xlsx-файл ООН должен лежать в `data/`** с точно таким именем:
   `WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx` (без скобок и
   модификаторов). Иначе build упадёт.
3. **GitHub Pages не любит большие файлы.** xlsx ~5 МБ — это нормально, но
   если будет больше 100 МБ, нужен Git LFS.
4. **Streamlit Cloud — Python 3.11+.** Проверьте в настройках при деплое.

## Структура данных

```python
DATA = {
    "metadata": {
        "year_start": 1950,
        "year_end": 2024,
        "world": [91824, 95012, ...]   # длина 75, тысячи рождений по годам
    },
    "countries": {
        "RUS": {
            "n": "Russian Federation",   # name (en)
            "r": "Россия",               # name_ru
            "g": "Europe",               # group/region
            "b": [2746, 2932, ...]       # array length 75, thousands
        },
        ...
    }
}
```

Доступ:
```python
births_in_thousands = DATA["countries"]["RUS"]["b"][year - 1950]
world_in_thousands = DATA["metadata"]["world"][year - 1950]
probability = births_in_thousands / world_in_thousands
```
