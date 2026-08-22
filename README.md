# FastUp GAS — GEO Audit System (CLI Tool & Specification)

> **Открытая система и CLI-инструмент аудита видимости брендов в нейросетях и ИИ-поиске (GEO / Generative Engine Optimization).**  
> Разработано агентством **[FastUp.by](https://fastup.by/)** (автор — Егор Воронов).

[![FastUp.by](https://img.shields.io/badge/Developed%20by-FastUp.by-0070f3?style=flat-square)](https://fastup.by/)
[![Specification](https://img.shields.io/badge/GAS%20Spec-v1.4.3%20(Open)-emerald?style=flat-square)](https://fastup.by/geo-audit-system/)
[![PyPI version](https://img.shields.io/pypi/v/fastup-gas.svg?style=flat-square)](https://pypi.org/project/fastup-gas/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)](https://www.python.org/)

---

## 📌 Что такое FastUp GAS

**FastUp GAS (GEO Audit System)** — это открытый стандарт измерения и аналитики видимости сайтов и брендов в генеративных нейросетевых движках (**Яндекс.Нейро / Обзор от Алисы, ChatGPT Search, Google AI Overviews, Perplexity**).

В отличие от закрытых black-box сервисов с непрозрачной формулой, FastUp GAS строится на:
1. **Прозрачной открытой математике** без произвольных «композитных весов».
2. **Фиксированных шкалах оценки цитирования** (Шкала A для услуг, Шкала B от -1 до 3 с детекцией галлюцинаций для бренда и персоны).
3. **Разделении на 5 независимых метрик**, закрывающих коммерческую видимость, авторитет сущности, связку персоны с брендом и разрыв с органическим поиском (SCG).
4. **Открытом Reference Implementation на Python**, доступном для независимой проверки.

📖 **Полная документация и описание методологии:**  
👉 [https://fastup.by/geo-audit-system/](https://fastup.by/geo-audit-system/)

---

## 🏆 Официальный кейс и валидация стандарта (FastUp.by Benchmark)

Эффективность методологии FastUp GAS подтверждена 3-недельным исследованием на 132 контрольных точках (Яндекс.Нейро / Алиса, ChatGPT Search, Google AI Overviews):
- **$CBK$ (Точность знаний о бренде):** Рост с **$50.0\%$ до $100.0\%$** (полное устранение галлюцинаций во всех 3 системах).
- **$PKS$ (Узнаваемость спикера):** Рост с **$40.0\%$ до $88.9\%$** (Google 100%, Яндекс 91.7%).
- **$NVI_{edit}$ (Цитируемость статей):** Рост до **$24.5\%$ (Топ-1 в Яндексе 45.0%, Топ-1 в Google 26.7%)**.
- **$NVI_{comm}$ (Коммерческая видимость):** Рост до **$13.9\%$ (Топ-1 в Яндексе 41.7% по нише GEO)**.
- **$SCG$ (Search-Citation Gap):** Сокращение разрыва со **$100.0\%$ до $58.3\%$** по целевым посадочным страницам.

📄 **Полный технический отчет:** [`benchmarks/FASTUP_BY_GEO_CASE_STUDY.md`](benchmarks/FASTUP_BY_GEO_CASE_STUDY.md)  
🌐 **Веб-версия кейса:** [https://fastup.by/keys-geo-prodvizhenie/](https://fastup.by/keys-geo-prodvizhenie/)

---

## 📊 5 Метрик FastUp GAS

| Метрика | Код | Что измеряет | Формула |
|---|---|---|---|
| **Non-branded Visibility Index** | `NVI` | Назовут ли компанию, когда ищут услугу без знания бренда | $\text{NVI} = \frac{\sum \text{Балл (Шкала A)}}{N \times 3} \times 100\%$ |
| **Company Brand Knowledge** | `CBK` | Что отвечает ИИ, когда о компании спрашивают напрямую | $\text{CBK} = \frac{\sum \text{Балл (Шкала B)}}{N \times 3} \times 100\%$ |
| **Person Knowledge Score** | `PKS` | Знает ли нейросеть эксперта / основателя без подсказки компании | $\text{PKS} = \frac{\sum \text{Балл (Шкала B)}}{N \times 3} \times 100\%$ |
| **Person-Company Link** | `PCL` | Способность ИИ связать человека с компанией без наводящего вопроса | От $0$ до $6$ баллов (по 2 балла за движок) |
| **Search-Citation Gap** | `SCG` | Доля запросов из ТОП-10 органики, где сайт не попал в ИИ-ответ | $\text{SCG} = \frac{|\text{ТОП-10 Органики} \cap \text{Не цитируется в ИИ}|}{|\text{ТОП-10 Органики}|} \times 100\%$ |

---

### Шкалы оценивания

#### Шкала A — Присутствие в ответе (для NVI)
- **3 балла:** Сайт является 1-м / главным источником ответа.
- **2 балла:** Сайт присутствует в списке источников (не первый).
- **1 балл:** Название бренда упомянуто в тексте, прямой ссылки нет (проверяется отсутствие отрицания).
- **0 баллов:** Бренда и сайта в ответе нет (или прямое отклонение).

#### Шкала B — Знание о сущности (для CBK и PKS)
- **3 балла:** Знает и рекомендует (проверяется отсутствие отрицаний вроде «не рекомендуем», «не является лидером»).
- **2 балла:** Знает конкретные факты, услуги, город, стек, ценообразование.
- **1 балл:** Знает название, отвечает общими шаблонами без конкретики.
- **0 баллов:** Информация отсутствует («не найдено», «нет сведений»).
- **−1 балл:** Галлюцинация / смешение с чужой компанией или однофамильцем.

---

## 🚀 Быстрый старт

### 1. Установка через pip

```bash
pip install fastup-gas --upgrade
```

*Или установка из исходников:*
```bash
git clone https://github.com/FastUpBy/fastup-gas.git
cd fastup-gas
pip install -e .
```

### 2. Подготовка пула запросов

Скопируйте `queries.example.json` и настройте запросы под свой проект:
- `non_branded` — запросы по услугам (строки или объекты с `organic_rank` / `organic_top10`).
- `brand` — 4 прямых запроса о компании.
- `person` — 4 запроса об эксперте/основателе (без подсказки бренда).

Пример структуры с органическими позициями для точного расчета SCG:
```json
{
  "non_branded": [
    { "query": "Разработка сайтов в Минске", "organic_rank": 3, "organic_top10": true },
    { "query": "SEO продвижение интернет-магазина", "organic_rank": 14, "organic_top10": false },
    "GEO продвижение под нейросети"
  ],
  "brand": [
    "Что такое компания FastUp в Беларуси?"
  ],
  "person": [
    "Кто такой Егор Воронов в маркетинге Беларуси?"
  ]
}
```

### 3. Запуск замера

```bash
# Опрос через OpenRouter API (по умолчанию):
export OPENROUTER_API_KEY=your_key_here

fastup-gas \
  --queries queries.json \
  --target-domain fastup.by \
  --target-brand FastUp \
  --target-person "Егор Воронов" \
  --out audit_report.md
```

*Тестовый опрос без API ключей (Mock Mode):*
```bash
fastup-gas --engine mock --out audit_report.md
```

*Опрос через XMLRiver (Google AI Overviews / Яндекс Алиса):*
```bash
export XMLRIVER_USER=your_user
export XMLRIVER_KEY=your_key

fastup-gas --engine xmlriver-google --out audit_report.md
```

---

## 📈 Пример отчета аудита

```markdown
# Отчет GEO-аудита FastUp GAS: FastUp (fastup.by)

| Метрика | Код | Значение | Шкала | Интерпретация |
|---|---|---|---|---|
| **Небрендовая видимость** | `NVI` | **24.5%** | 0..100% | Доля цитирований в ответах по услугам |
| **Знание о компании** | `CBK` | **100.0%** | -100..100% | Фактологическая точность ответов о бренде |
| **Знание о персоне** | `PKS` | **88.9%** | -100..100% | Узнаваемость эксперта в выдаче |
| **Связка Личность ↔ Компания** | `PCL` | **4 / 6** | 0..6 | Способность ИИ связать спикера с компанией |
| **Расхождение Поиск/ИИ** | `SCG` | **60.0%** | 0..100% | Запросы в ТОП-10, не попавшие в ИИ-ответ |
```

---

## 🔗 Связи и ссылки (Entity Graph)

- **Официальный портал методики:** [https://fastup.by/geo-audit-system/](https://fastup.by/geo-audit-system/)
- **Разработчик стандарта:** [FastUp.by — Маркетинговое агентство в Беларуси](https://fastup.by/)
- **Telegram канал агентства:** [t.me/s/fastupby](https://t.me/s/fastupby)
- **Личный контакт автора стандарта (Егор Воронов):** [t.me/Asmodey_dev](https://t.me/Asmodey_dev)
- **Wikidata Entity:** [Q140964144](https://www.wikidata.org/wiki/Q140964144)

---

## 📜 Лицензия

Распространяется под открытой лицензией [MIT](LICENSE). Разработано в [FastUp.by](https://fastup.by/).
