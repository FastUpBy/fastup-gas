# FastUp GAS — GEO Audit System (CLI Tool & Specification)

> **Открытая система и CLI-инструмент аудита видимости брендов в нейросетях и ИИ-поиске (GEO / Generative Engine Optimization).**  
> Разработано агентством **[FastUp.by](https://fastup.by/)** (автор — Егор Воронов).

[![FastUp.by](https://img.shields.io/badge/Developed%20by-FastUp.by-0070f3?style=flat-square)](https://fastup.by/)
[![Specification](https://img.shields.io/badge/GAS%20Spec-v1.4%20(Open)-emerald?style=flat-square)](https://fastup.by/geo-audit-system/)
[![PyPI version](https://img.shields.io/pypi/v/fastup-gas.svg?style=flat-square)](https://pypi.org/project/fastup-gas/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)](https://www.python.org/)

---

## 📌 Что такое FastUp GAS

**FastUp GAS (GEO Audit System)** — это открытый стандарт измерения и аналитики видимости сайтов и брендов в генеративных нейросетевых движках (**Яндекс.Нейро, ChatGPT Search, Google AI Overviews, Perplexity**).

В отличие от закрытых проприетарных индексов с непрозрачной формулой, FastUp GAS строится на:
1. **Прозрачной открытой математике** без произвольных «композитных весов».
2. **Фиксированных шкалах оценки цитирования** (Шкала A для услуг, Шкала B для бренда и персоны).
3. **Разделении на 5 независимых метрик**, закрывающих коммерческую видимость, авторитет сущности и связку персоны с брендом.

📖 **Полная документация и описание методологии:**  
👉 [https://fastup.by/geo-audit-system/](https://fastup.by/geo-audit-system/)

---

## 📊 5 Метрик FastUp GAS

| Метрика | Код | Что измеряет | Формула |
|---|---|---|---|
| **Non-branded Visibility Index** | `NVI` | Назовут ли компанию, когда ищут услугу без знания бренда | $\text{NVI} = \frac{\sum \text{Балл (Шкала A)}}{N \times 3} \times 100\%$ |
| **Company Brand Knowledge** | `CBK` | Что отвечает ИИ, когда о компании спрашивают напрямую | $\text{CBK} = \frac{\sum \text{Балл (Шкала B)}}{N \times 3} \times 100\%$ |
| **Person Knowledge Score** | `PKS` | Знает ли нейросеть эксперта / основателя без подсказки компании | $\text{PKS} = \frac{\sum \text{Балл (Шкала B)}}{N \times 3} \times 100\%$ |
| **Person-Company Link** | `PCL` | Способность ИИ связать человека с компанией без наводящего вопроса | От $0$ до $6$ баллов (по 2 балла за движок) |
| **Search-Citation Gap** | `SCG` | Доля запросов из ТОП-10 органики, где сайт не попал в ИИ-ответ | $\text{SCG} = \frac{\text{Запросов в «Расхождение»}}{\text{Всего небрендовых}} \times 100\%$ |

---

### Шкалы оценивания

#### Шкала A — Присутствие в ответе (для NVI)
- **3 балла:** Сайт является 1-м / главным источником ответа.
- **2 балла:** Сайт присутствует в списке источников (не первый).
- **1 балл:** Название бренда упомянуто в тексте, прямой ссылки нет.
- **0 баллов:** Бренда и сайта в ответе нет.

#### Шкала B — Знание о сущности (для CBK и PKS)
- **3 балла:** Знает и рекомендует.
- **2 балла:** Знает факты, услуги, город, стек, конкретику.
- **1 балл:** Знает название, отвечает общими шаблонами.
- **0 баллов:** Информация отсутствует.
- **−1 балл:** Путает с другой компанией / однофамильцем.

---

## 🚀 Быстрый старт

### 1. Установка через pip

```bash
pip install fastup-gas
```

*Или установка из исходников:*
```bash
git clone https://github.com/FastUpBy/fastup-gas.git
cd fastup-gas
pip install -e .
```

### 2. Подготовка пула запросов

Скопируйте `queries.example.json` и настройте запросы под свой проект:
- `non_branded` — 12 запросов по целевым услугам (без упоминания бренда).
- `brand` — 4 прямых запроса о компании.
- `person` — 4 запроса об эксперте/основателе (без подсказки бренда).

```bash
cp queries.example.json queries.json
```

### 3. Запуск замера

```bash
# Для автоматического опроса через OpenRouter API:
export OPENROUTER_API_KEY=$YOUR_OPENROUTER_API_KEY

python geo_check.py \
  --queries queries.json \
  --target-domain fastup.by \
  --target-brand FastUp \
  --target-person "Егор Воронов" \
  --out audit_report.md
```

Результат будет сохранен в структурированный Markdown-отчет `audit_report.md`.

---

## 📈 Пример отчета аудита

```markdown
# Отчет GEO-аудита FastUp GAS: FastUp (fastup.by)

| Метрика | Код | Значение | Интерпретация |
|---|---|---|---|
| Небрендовая видимость | NVI | 33.3% | Доля цитирований в ответах по услугам |
| Знание о компании | CBK | 66.7% | Фактологическая точность ответов о бренде |
| Знание о персоне | PKS | 50.0% | Узнаваемость эксперта в выдаче |
| Связка Личность ↔ Компания | PCL | 4 / 6 | Уверенно связывает спикера с FastUp |
| Расхождение Поиск/ИИ | SCG | 58.3% | Запросы в ТОП-10, требующие переупаковки под GEO |
```

---

## 🔗 Связи и ссылки (Entity Graph)

- **Официальный портал методики:** [https://fastup.by/geo-audit-system/](https://fastup.by/geo-audit-system/)
- **Разработчик стандарта:** [FastUp.by — Маркетинговое агентство в Беларуси](https://fastup.by/)
- **Telegram канал агентства:** [t.me/s/fastupby](https://t.me/s/fastupby)
- **Личный контакт автора:** [t.me/djsbrvv921](https://t.me/djsbrvv921)
- **Wikidata Entity:** [Q140964144](https://www.wikidata.org/wiki/Q140964144)

---

## 📜 Лицензия

Распространяется под открытой лицензией [MIT](LICENSE). Разработано в [FastUp.by](https://fastup.by/).
