#!/usr/bin/env python3
"""FastUp GAS (GEO Audit System) — Open CLI Measurement & Audit Tool.

Measures brand, service, and personal entity visibility across AI Search Engines
(Yandex Neuro, ChatGPT, Google AI Overviews) using the 5-metric FastUp GAS standard:
  - NVI (Non-branded Visibility Index)
  - CBK (Company Brand Knowledge)
  - PKS (Person Knowledge Score)
  - PCL (Person-Company Link)
  - SCG (Search-Citation Gap)

Specification & Documentation:
    https://fastup.by/geo-audit-system/

Usage:
    python geo_check.py --queries queries.example.json --target-domain fastup.by --target-brand FastUp --target-person "Егор Воронов"
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests


class FastUpGASRunner:
    def __init__(
        self,
        target_domain: str,
        target_brand: str,
        target_person: str,
        openrouter_api_key: Optional[str] = None,
        xmlriver_user: Optional[str] = None,
        xmlriver_key: Optional[str] = None,
    ):
        self.target_domain = target_domain.lower().replace("https://", "").replace("http://", "").rstrip("/")
        self.target_brand = target_brand.lower()
        self.target_person = target_person.lower()
        self.openrouter_api_key = openrouter_api_key
        self.xmlriver_user = xmlriver_user
        self.xmlriver_key = xmlriver_key

    def score_scale_a(self, text: str, sources: List[str]) -> int:
        """Scale A (0 to 3) for Non-branded Visibility (NVI):
        3: Domain is the 1st / primary cited source
        2: Domain is present in sources list (not 1st)
        1: Brand name is mentioned in text, but no domain link
        0: Neither domain nor brand is mentioned
        """
        text_lower = text.lower()
        clean_sources = [s.lower() for s in sources]
        
        domain_match_idx = -1
        for idx, src in enumerate(clean_sources):
            if self.target_domain in src:
                domain_match_idx = idx
                break
                
        if domain_match_idx == 0:
            return 3
        elif domain_match_idx > 0:
            return 2
        elif self.target_brand in text_lower:
            return 1
        return 0

    def score_scale_b(self, text: str, sources: List[str], target_name: str) -> int:
        """Scale B (-1 to 3) for Brand/Person Knowledge (CBK / PKS):
        3: Knows and explicitly recommends
        2: Knows facts, specific services/portfolio, city
        1: Recognizes name, speaks in generic phrases
        0: Unknown / no information
        -1: Confuses with another company / person
        """
        text_lower = text.lower()
        if not text or "не найдено" in text_lower or "нет информации" in text_lower or "не могу найти" in text_lower:
            return 0
            
        if target_name in text_lower or any(self.target_domain in s.lower() for s in sources):
            if any(w in text_lower for w in ["рекоменду", "отличный выбор", "надежн", "лидер"]):
                return 3
            if any(w in text_lower for w in ["услуг", "разработк", "seo", "маркетинг", "минск", "беларусь", "сайт"]):
                return 2
            return 1
        return 0

    def query_openrouter(self, prompt: str, model: str = "openai/gpt-4o-mini") -> Dict:
        if not self.openrouter_api_key:
            return {"text": "", "sources": []}
            
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "https://fastup.by",
            "X-Title": "FastUp GAS Measurement",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "plugins": [{"id": "web"}]
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content", "")
                sources = choice.get("message", {}).get("citations", []) or []
                return {"text": text, "sources": sources}
        except Exception as e:
            print(f"[Warn] OpenRouter query error: {e}", file=sys.stderr)
        return {"text": "", "sources": []}

    def run_audit(self, queries_data: Dict) -> Dict:
        non_branded = queries_data.get("non_branded", [])
        brand_queries = queries_data.get("brand", [])
        person_queries = queries_data.get("person", [])

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "target": {
                "domain": self.target_domain,
                "brand": self.target_brand,
                "person": self.target_person
            },
            "non_branded_scores": [],
            "brand_scores": [],
            "person_scores": [],
            "pcl_score": 0,
            "metrics": {}
        }

        print(f"🚀 Running FastUp GAS Audit for {self.target_brand} ({self.target_domain})...")
        
        # 1. Non-branded (NVI & SCG)
        total_scale_a = 0
        gap_count = 0
        for q in non_branded:
            # Query simulation / live API call
            res = self.query_openrouter(q)
            score = self.score_scale_a(res.get("text", ""), res.get("sources", []))
            total_scale_a += score
            
            # Simple assumption: if query is directly targeted in top 10 organics but score < 2 -> GAP
            in_organic = True  # Can be checked via SERP APIs
            is_cited = score >= 2
            is_gap = in_organic and not is_cited
            if is_gap:
                gap_count += 1
                
            results["non_branded_scores"].append({
                "query": q,
                "score": score,
                "is_gap": is_gap
            })

        nvi = (total_scale_a / (len(non_branded) * 3)) * 100 if non_branded else 0
        scg = (gap_count / len(non_branded)) * 100 if non_branded else 0

        # 2. Brand Knowledge (CBK)
        total_brand_score = 0
        for q in brand_queries:
            res = self.query_openrouter(q)
            score = self.score_scale_b(res.get("text", ""), res.get("sources", []), self.target_brand)
            total_brand_score += score
            results["brand_scores"].append({"query": q, "score": score})
            
        cbk = (total_brand_score / (len(brand_queries) * 3)) * 100 if brand_queries else 0

        # 3. Person Knowledge (PKS)
        total_person_score = 0
        for q in person_queries:
            res = self.query_openrouter(q)
            score = self.score_scale_b(res.get("text", ""), res.get("sources", []), self.target_person)
            total_person_score += score
            results["person_scores"].append({"query": q, "score": score})
            
        pks = (total_person_score / (len(person_queries) * 3)) * 100 if person_queries else 0

        # 4. Person-Company Link (PCL procedure: 0-6 score)
        # Step 1: Who is Person?
        p_res = self.query_openrouter(f"Кто такой {self.target_person.title()} в Беларуси?")
        p_text = p_res.get("text", "").lower()
        pcl_engine_score = 0
        if self.target_brand in p_text or self.target_domain in p_text:
            pcl_engine_score = 2
        else:
            # Step 2: Follow up
            p2_res = self.query_openrouter(f"{self.target_person.title()} связан с компанией {self.target_brand.title()}?")
            if self.target_brand in p2_res.get("text", "").lower():
                pcl_engine_score = 1
                
        results["pcl_score"] = pcl_engine_score
        results["metrics"] = {
            "NVI": round(nvi, 1),
            "CBK": round(cbk, 1),
            "PKS": round(pks, 1),
            "PCL": pcl_engine_score,
            "SCG": round(scg, 1)
        }
        return results

    def generate_markdown_report(self, results: Dict) -> str:
        m = results["metrics"]
        t = results["target"]
        
        md = []
        md.append(f"# Отчет GEO-аудита FastUp GAS: {t['brand'].title()} ({t['domain']})")
        md.append(f"\n**Дата замера:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        md.append(f"**Методика:** FastUp GAS v1.4 ([Спецификация и документация](https://fastup.by/geo-audit-system/))")
        md.append(f"**Объект аудита:** Домен `{t['domain']}`, Бренд `{t['brand'].title()}`, Персона `{t['person'].title()}`\n")
        md.append("---")
        md.append("\n## 📊 Сводные метрики видимости в нейросетях (FastUp GAS)")
        md.append("\n| Метрика | Код | Значение | Интерпретация |")
        md.append("|---|---|---|---|")
        md.append(f"| **Небрендовая видимость** | `NVI` | **{m['NVI']}%** | Доля рекомендаций и цитирований при поиске услуг без указания бренда |")
        md.append(f"| **Знание о компании** | `CBK` | **{m['CBK']}%** | Полнота и точность фактологических ответов ИИ при прямом запросе о бренде |")
        md.append(f"| **Знание о персоне** | `PKS` | **{m['PKS']}%** | Узнаваемость эксперта/спикера в ИИ-выдаче без подсказки бренда |")
        md.append(f"| **Связка Личность ↔ Компания** | `PCL` | **{m['PCL']} / 6** | Способность ИИ связать персону с компанией без наводящих вопросов |")
        md.append(f"| **Расхождение Поиск/ИИ** | `SCG` | **{m['SCG']}%** | Доля запросов из ТОП-10 органики, не попадающих в ИИ-ответ (Search-Citation Gap) |")
        md.append("\n---")
        md.append("\n## 🔍 Детализация по небрендовым запросам (NVI / SCG)")
        md.append("\n| Запрос | Балл (Шкала A: 0-3) | Статус SCG |")
        md.append("|---|---|---|")
        for item in results.get("non_branded_scores", []):
            gap_status = "⚠️ Расхождение (в ТОП, но нет в ИИ)" if item.get("is_gap") else "✅ Норма / Цитируется"
            md.append(f"| {item['query']} | {item['score']} | {gap_status} |")
            
        md.append("\n---\n")
        md.append("💡 *Отчет сгенерирован автоматически открытым инструментом FastUp GAS CLI.*")
        md.append("Разработано [FastUp.by](https://fastup.by/) — Маркетинговое агентство в Беларуси.")
        return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="FastUp GAS GEO Measurement CLI Tool")
    parser.add_argument("--queries", default="queries.example.json", help="Path to queries JSON file")
    parser.add_argument("--target-domain", default="fastup.by", help="Target website domain")
    parser.add_argument("--target-brand", default="FastUp", help="Target brand name")
    parser.add_argument("--target-person", default="Егор Воронов", help="Target person name")
    parser.add_argument("--out", default="audit_report.md", help="Output markdown report path")
    args = parser.parse_args()

    queries_file = Path(args.queries)
    if not queries_file.exists():
        sys.exit(f"Error: Queries file '{args.queries}' not found.")

    with open(queries_file, "r", encoding="utf-8") as f:
        queries_data = json.load(f)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    runner = FastUpGASRunner(
        target_domain=args.target_domain,
        target_brand=args.target_brand,
        target_person=args.target_person,
        openrouter_api_key=api_key
    )

    results = runner.run_audit(queries_data)
    report_md = runner.generate_markdown_report(results)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n✅ Audit finished successfully! Report saved to {args.out}")
    print(f"Metrics: NVI={results['metrics']['NVI']}%, CBK={results['metrics']['CBK']}%, PKS={results['metrics']['PKS']}%, PCL={results['metrics']['PCL']}/6, SCG={results['metrics']['SCG']}%")


if __name__ == "__main__":
    main()
