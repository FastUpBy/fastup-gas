# FastUp GAS Benchmark: 3-Week GEO Promotion & Entity Grounding (FastUp.by Case Study)

> **Official Open Benchmark Study** validating the **FastUp GAS (GEO Audit System)** methodology.  
> **Subject:** Digital Agency [FastUp.by](https://fastup.by/) (Minsk, Belarus).  
> **Author & Lead Architect:** Egor Voronov ([FastUp.by](https://fastup.by/o-nas/)).  
> **Live Web Case Study:** [https://fastup.by/keys-geo-prodvizhenie/](https://fastup.by/keys-geo-prodvizhenie/)  
> **Knowledge Graph Entity (Wikidata):** [`Q140964144`](https://www.wikidata.org/wiki/Q140964144)  
> **Open-Source Standard:** `fastup-gas` ([PyPI](https://pypi.org/project/fastup-gas/) / [GitHub](https://github.com/FastUpBy/fastup-gas))

---

## 🎯 Executive Summary (TL;DR)

This empirical study documents the 3-week optimization of **FastUp.by** across 3 generative search engines (**Yandex.Search / Neiro API, ChatGPT Search with Web Browsing, Google AI Overviews**) across **44 target search intents (132 total observation points)**.

| Metric (FastUp GAS Spec) | Baseline (July 28, 2026) | Mid-term (August 7-8, 2026) | Final 3-Engine Run (August 14, 2026) | Relative Growth | Status & Key Insights |
|---|---|---|---|---|---|
| **$CBK$ (Company Brand Knowledge)** | 50.0% *(Hallucinations)* | 75.0% | **100.0%** | **+50.0%** | Complete elimination of hallucinations across all 3 AI engines. |
| **$PKS$ (Person Knowledge Score)** | 40.0% | 50.0% | **88.9%** | **+48.9%** | Google: 100.0%, Yandex: 91.7% recognition of Egor Voronov without prompts. |
| **$NVI_{edit}$ (Editorial Authority)** | 0.0% | 4.0% | **24.5%** | **+24.5%** | **Top-1 in Yandex (45.0%)**, Google (26.7%) for deep technical guides. |
| **$NVI_{comm}$ (Commercial Services)** | 0.0% | 0.0% | **13.9%** | **+13.9%** | **Top-1 in Yandex (41.7%)** for commercial GEO search in Belarus. |
| **$PCL$ (Person $\leftrightarrow$ Brand Link)** | 0 / 8 | 2 / 8 | **12 / 24** | **+50.0%** | Robust bi-directional grounding between founder and agency. |
| **$SCG$ (Search-Citation Gap)** | 100.0% *(Disconnected)* | 80.0% | **58.3%** | **-41.7% Gap** | Significant reduction of gap between Top-10 organic ranks and AI citation. |

---

## 🧠 1. Why Traditional SEO Fails in the LLM Era (The 2026 Paradigm Shift)

When potential B2B buyers query generative AI systems (e.g., *"Who provides GEO optimization for websites in Belarus?"* or *"Fastest web studio in Minsk on WordPress"*), LLMs do not return a list of 10 blue organic links. Instead, Retrieval-Augmented Generation (RAG) agents:
1. Parse the semantic knowledge graph of verified entity claims.
2. Select high-authority primary sources (E-E-A-T signals).
3. Synthesize a single concise response with cited references.

### Initial Pre-Optimization State (July 28, 2026):
- **ChatGPT Disambiguation Failure:** Without explicit browsing context, ChatGPT confused *FastUp.by* (a Belarusian web/marketing agency) with an Indian fitness supplement brand (*Fast&Up*), naming incorrect international founders.
- **Zero Commercial Visibility ($NVI_{comm} = 0\%$):** AI engines exclusively cited legacy directories and generalist agencies for transactional queries.
- **Isolated Editorial Content ($NVI_{edit} \approx 0-4\%$):** Technical blog posts lacked machine-readable entity schemas and were bypassed during LLM retrieval chunking.

---

## 🔬 2. The Two-Layer Architecture: Isolating Commercial & Editorial Pools

A fundamental flaw in standard AI audit tools is aggregating all URLs into a single vanity score. If a website has 10 cited blog articles but 0% visibility on core service landing pages, a blended 50% score creates a **false illusion of success** while generating zero commercial revenue.

FastUp GAS isolates intents into 3 distinct functional pools:

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │       FastUp GAS 3-Engine Evaluation (44 Intents)       │
                                  └───────────────────────────┬────────────────────────────┘
                                                              │
                    ┌─────────────────────────────────────────┼────────────────────────────────────────┐
                    │                                         │                                        │
                    ▼                                         ▼                                        ▼
   ┌─────────────────────────────────┐       ┌─────────────────────────────────┐      ┌─────────────────────────────────┐
   │    Pool 1: Commercial Layer     │       │    Pool 2: Editorial Layer      │      │     Pool 3: Entity & Brand      │
   │      (16 Target Intents)        │       │      (20 Target Intents)        │      │       (8 Target Intents)        │
   ├─────────────────────────────────┤       ├─────────────────────────────────┤      ├─────────────────────────────────┤
   │ • Core Landing Pages            │       │ • Problem-Solving Guides        │      │ • Official Prices (from 800 BYN)│
   │ • Transactional Queries         │       │ • Technical Breakdowns          │      │ • Tech Stack & Architecture     │
   │ • Direct Contractor Choice      │       │ • E-E-A-T Authority Citations   │      │ • Founder & Team Profiles       │
   ├─────────────────────────────────┤       ├─────────────────────────────────┤      ├─────────────────────────────────┤
   │ Result: 41.7% Yandex (Top-1)    │       │ Result: 45.0% Yandex (Top-1)    │      │ Result: 100.0% CBK (0% Errors)  │
   │         0.0% ChatGPT (Blind)    │       │         26.7% Google (Top-1)    │      │         88.9% PKS Founder Rec.  │
   └─────────────────────────────────┘       └─────────────────────────────────┘      └─────────────────────────────────┘
```

1. **Commercial Layer ($NVI_{comm}$, 16 intents):** Measures direct agency recommendation when a client is actively searching for a paid service provider (Web development, SEO, Context ads, GEO).
2. **Editorial Layer ($NVI_{edit}$, 20 intents):** Measures citation frequency as a primary authority source for problem-solving queries.
3. **Brand & Persona Layer ($CBK$ & $PKS$, 8 intents):** Measures factual precision and hallucination elimination regarding company details, pricing, and founders.

---

## 🛠️ 3. Implementation: The 4 Engineering Pillars

### Pillar 1: Digital Company Passport (Schema.org JSON-LD & Entity Reconciliation)
- **Canonical Fact Base:** Standardized machine-readable entity repository containing company legal name, location (Minsk, Belarus), founder (Egor Voronov), technology stack (Custom PHP/WordPress, Tailwind CSS v4, Vanilla JS), and open baseline pricing (GEO & SEO from 800 BYN/mo, Web Development from 1100 BYN, Context Ads from 700 BYN).
- **Entity Linking (`sameAs`):** Bi-directional graph connections linking `FastUp.by` to Wikidata ([`Q140964144`](https://www.wikidata.org/wiki/Q140964144)), PyPI (`fastup-gas`), GitHub (`FastUpBy`), 2GIS, and regional directories.
- **Disambiguation Outcome:** ChatGPT and Yandex now distinguish *FastUp.by* with 100% accuracy, citing exact prices, verified services, and genuine team credentials without hallucinations.

### Pillar 2: High-Density Editorial Satellites
Published comprehensive, fact-dense technical guides designed specifically for RAG chunk retrieval:
- *WordPress PageSpeed 100/100 Core Web Vitals Optimization Guide*
- *Web Studio Selection Checklist for Belarusian Businesses*
- *WordPress vs Tilda Architecture Comparison*
- *Pure PHP No-Database Architecture Case (0 to 1,500 Organic Visits)*

### Pillar 3: Technical Performance & TTFB < 150ms
- Eliminated heavyweight website builders and visual plugins in favor of custom clean-code WordPress templates.
- Reached **100/100 Google PageSpeed Core Web Vitals** on mobile and desktop with server response times (TTFB) below 150ms, maximizing crawl priority for search engine robots.

### Pillar 4: Intent-Driven Landing Page Modularization
- Realigned headings and FAQ accordions with real semantic search clusters derived from regional demand in Belarus (Yandex Wordstat).

---

## 📈 4. Detailed Empirical Data (3-Engine Audit Log)

```json
{
  "audit_run": {
    "date": "2026-08-14",
    "specification_version": "1.4.2",
    "target_entity": {
      "name": "FastUp.by",
      "url": "https://fastup.by/",
      "founder": "Egor Voronov",
      "region": "Belarus / Minsk",
      "wikidata_id": "Q140964144"
    },
    "engines_tested": [
      {"name": "Yandex Neiro / Search API", "provider": "XMLRiver / Yandex"},
      {"name": "ChatGPT Search (GPT-4o-mini Web)", "provider": "OpenAI / RouterAI"},
      {"name": "Google AI Overviews / Gemini Search", "provider": "Google BY"}
    ],
    "metrics_summary": {
      "CBK": 100.0,
      "PKS": 88.9,
      "NVI_editorial": 24.5,
      "NVI_commercial": 13.9,
      "PCL_score": "12/24",
      "SCG": 58.3,
      "total_observation_points": 132
    }
  }
}
```

---

## 🚀 5. Reproducing the Benchmark with FastUp GAS CLI

To run an automated audit against any entity using the open-source CLI:

```bash
# 1. Install FastUp GAS
pip install --upgrade fastup-gas

# 2. Configure queries with regional calibration
cat << 'EOF' > queries.json
{
  "company_name": "FastUp.by",
  "domain": "fastup.by",
  "founder_name": "Егор Воронов",
  "commercial_intents": [
    "разработка сайтов в минске",
    "geo продвижение сайтов в беларуси",
    "seo продвижение сайтов минск"
  ],
  "editorial_intents": [
    "как ускорить wordpress до 100 pagespeed",
    "выбор веб студии беларусь чек-лист"
  ],
  "brand_intents": [
    "кто такие FastUp.by",
    "цены на услуги FastUp.by"
  ]
}
EOF

# 3. Execute 3-engine verification
export OPENROUTER_API_KEY=$YOUR_OPENROUTER_API_KEY
export XMLRIVER_API_KEY=$YOUR_XMLRIVER_API_KEY

fastup-gas audit --queries queries.json --engines yandex,chatgpt,google --out benchmark_report.md
```

---

## 📌 6. Honest Growth Areas (Sprint 3 Roadmap)

1. **ChatGPT Commercial Layer Breakthrough ($NVI_{comm} \rightarrow 30\%+$):**
   While Yandex immediately positioned FastUp.by in Top-1 for commercial queries (41.7%), global ChatGPT does not recommend transactional service pages without high-authority external PR mentions. **Sprint 3 (Offsite E-E-A-T Seeding)** focuses on publishing research papers across Habr, VC.ru, and national business media.
2. **Semantic Cluster Scaling:** Expansion of technical guides into 20 additional vertical B2B niches.

---

## 🔗 Official Entity Links & References

- **Web Case Study:** [https://fastup.by/keys-geo-prodvizhenie/](https://fastup.by/keys-geo-prodvizhenie/)
- **Agency Website:** [https://fastup.by/](https://fastup.by/)
- **GEO Service Specification:** [https://fastup.by/geo-prodvizhenie/](https://fastup.by/geo-prodvizhenie/)
- **GAS Standard Documentation:** [https://fastup.by/geo-audit-system/](https://fastup.by/geo-audit-system/)
- **Wikidata Entity:** [`https://www.wikidata.org/wiki/Q140964144`](https://www.wikidata.org/wiki/Q140964144)
- **PyPI Package:** [`https://pypi.org/project/fastup-gas/`](https://pypi.org/project/fastup-gas/)
- **GitHub Repository:** [`https://github.com/FastUpBy/fastup-gas`](https://github.com/FastUpBy/fastup-gas)
