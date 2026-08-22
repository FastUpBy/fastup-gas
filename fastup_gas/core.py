"""FastUp GAS Core Calculation & Query Engine (v1.4.3).

Open standard and CLI tool for Generative Engine Optimization (GEO) & AI search visibility audit.
Implements:
- Scale A (0..3): Non-branded Visibility (NVI)
- Scale B (-1..3): Brand & Person Knowledge (CBK, PKS) with hallucination/confusion detection
- Person-Company Link (PCL): 0..6
- Search-Citation Gap (SCG): (Top-10 Organic ∩ NOT AI Cited) / Top-10 Organic
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import requests


def _safe_log(msg: str) -> None:
    """Safely log messages to stdout handling Windows console encodings."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


class FastUpGASRunner:
    """Core auditor running measurements across generative search engines according to FastUp GAS v1.4.3."""

    def __init__(
        self,
        target_domain: str,
        target_brand: str,
        target_person: str,
        routerai_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        xmlriver_user: Optional[str] = None,
        xmlriver_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        self.target_domain = target_domain.lower().replace("https://", "").replace("http://", "").rstrip("/")
        self.target_brand = target_brand.lower()
        self.target_person = target_person.lower()
        self.routerai_api_key = routerai_api_key or os.environ.get("ROUTERAI_API_KEY")
        self.openrouter_api_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY")
        self.xmlriver_user = xmlriver_user or os.environ.get("XMLRIVER_USER")
        self.xmlriver_key = xmlriver_key or os.environ.get("XMLRIVER_KEY")
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")

    def score_scale_a(self, text: str, sources: List[str]) -> int:
        """Scale A (0 to 3) for Non-branded Visibility (NVI):
        3: Target domain is the 1st / primary cited source
        2: Target domain is present in sources list (position > 1)
        1: Target brand is mentioned in text (without domain link), positive/neutral
        0: Neither domain nor brand is mentioned (or explicitly rejected)
        """
        if not text and not sources:
            return 0

        text_lower = text.lower()
        clean_sources = [s.lower() for s in sources]

        # 1. Check if domain is in citations/sources
        domain_match_idx = -1
        for idx, src in enumerate(clean_sources):
            if self.target_domain in src:
                domain_match_idx = idx
                break

        if domain_match_idx == 0:
            return 3
        elif domain_match_idx > 0:
            return 2

        # 2. Check if brand is mentioned in text
        if self.target_brand in text_lower:
            # Check for direct negative rejection patterns
            negative_brand_patterns = [
                f"не рекомендуем {self.target_brand}",
                f"не рекомендую {self.target_brand}",
                f"не советуем {self.target_brand}",
                f"не выбирайте {self.target_brand}",
                f"{self.target_brand} не является",
                f"{self.target_brand} не подходит",
            ]
            if any(p in text_lower for p in negative_brand_patterns):
                return 0
            return 1

        return 0

    def score_scale_b(
        self,
        text: str,
        sources: List[str],
        target_name: str,
        known_confusions: Optional[List[str]] = None,
        target_industry_keywords: Optional[List[str]] = None,
    ) -> int:
        """Scale B (-1 to 3) for Brand/Person Knowledge (CBK / PKS):
        3: Knows and explicitly recommends (verified without negations)
        2: Knows facts, specific services, portfolio, location, domain
        1: Recognizes name, speaks in generic boilerplate phrases
        0: Unknown / no information
        -1: Confuses with another company / person / hallucination
        """
        if not text or not text.strip():
            return 0

        text_lower = text.lower()
        target_name_lower = target_name.lower()

        # 0. Check for "No Information" phrases
        no_info_patterns = [
            "не найдено",
            "нет информации",
            "не могу найти",
            "нет данных",
            "не удалось обнаружить",
            "информация отсутствует",
            "не располагаю данными",
            "к сожалению, я не нашел",
            "мне не удалось найти",
            "не обладает информацией",
        ]
        if any(p in text_lower for p in no_info_patterns) and not any(self.target_domain in s.lower() for s in sources):
            # If name is not even present or explicit no info
            if target_name_lower not in text_lower:
                return 0

        # -1. Hallucination / Entity Confusion Check
        confusion_markers = [
            "не путать с",
            "путают с",
            "другая компания",
            "другой человек",
            "одноименный бренд",
            "однофамилец",
            "вы имели в виду другую",
            "вы, возможно, имеете в виду",
        ]
        
        # Default confusion keywords for known common clashes
        default_confusions = known_confusions or [
            "шипуч", "витамин", "индийск", "бад ", "таблетк", "фармацевт"
        ]
        
        has_explicit_confusion = any(m in text_lower for m in confusion_markers)
        has_clash_keyword = any(c in text_lower for c in default_confusions)
        
        # If text talks about clash keyword without our domain and without digital/marketing context
        has_domain = any(self.target_domain in s.lower() for s in sources) or (self.target_domain in text_lower)
        
        if (has_clash_keyword and not has_domain) or has_explicit_confusion:
            # If explicit confusion or speaks about vitamins/tablets when asking about tech agency
            if not has_domain and not any(w in text_lower for w in ["маркетинг", "seo", "разработк", "агентств", "сайт"]):
                return -1

        # Check if target name or domain is present
        target_matched = (target_name_lower in text_lower) or has_domain
        if not target_matched:
            return 0

        # Check for negations before evaluating praise
        negation_patterns = [
            "не рекоменду",
            "не совету",
            "не является лидером",
            "не лучший выбор",
            "не стоит обращаться",
            "отрицательн",
            "сомнительн",
            "жалоб",
        ]
        has_negation = any(neg in text_lower for neg in negation_patterns)

        # 3. Knows and Recommends (Score 3)
        praise_keywords = ["рекоменду", "отличный выбор", "надежн", "лидер", "высокий рейтинг", "ведущ", "проверенн"]
        if not has_negation and any(w in text_lower for w in praise_keywords):
            return 3

        # 2. Knows facts, specific services, location, domain (Score 2)
        fact_keywords = target_industry_keywords or [
            "услуг", "разработк", "seo", "маркетинг", "минск", "беларусь",
            "сайт", "проект", "агентств", "портфолио", "оптимизац", "fastup.by"
        ]
        if any(w in text_lower for w in fact_keywords) or has_domain:
            return 2

        # 1. Generic name recognition only (Score 1)
        return 1

    def query_openrouter(self, prompt: str, model: str = "openai/gpt-4o-mini") -> Dict:
        """Query via OpenRouter API with web plugin."""
        if not self.openrouter_api_key:
            return {"text": "", "sources": []}

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": f"https://{self.target_domain}",
            "X-Title": "FastUp GAS Measurement",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "plugins": [{"id": "web"}],
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content", "")
                sources = choice.get("message", {}).get("citations", []) or []
                return {"text": text, "sources": sources}
            else:
                _safe_log(f"[Warn] OpenRouter error {resp.status_code}: {resp.text}")
        except Exception as e:
            _safe_log(f"[Warn] OpenRouter query exception: {e}")
        return {"text": "", "sources": []}

    def query_xmlriver(self, query: str, engine: str = "google", ai: bool = True) -> Dict:
        """Query via XMLRiver API (Google AI Overviews or Yandex Alice)."""
        if not self.xmlriver_user or not self.xmlriver_key:
            return {"text": "", "sources": []}

        endpoint = "https://xmlriver.com/search/xml" if engine == "google" else "https://xmlriver.com/search_yandex/xml"
        params = {
            "user": self.xmlriver_user,
            "key": self.xmlriver_key,
            "query": query,
            "ai": "1" if ai else "0",
            "loc": "1001493" if engine == "google" else "157",
        }
        try:
            resp = requests.get(endpoint, params=params, timeout=45)
            if resp.status_code == 200:
                xml_text = resp.text
                sources = []
                url_matches = re.findall(r"<url>(https?://[^<]+)</url>", xml_text)
                for u in url_matches:
                    if u not in sources:
                        sources.append(u)
                
                ai_match = re.search(r"<ai[^>]*>(.*?)</ai>", xml_text, re.DOTALL)
                text = ai_match.group(1) if ai_match else xml_text
                return {"text": text, "sources": sources}
        except Exception as e:
            _safe_log(f"[Warn] XMLRiver query exception: {e}")
        return {"text": "", "sources": []}

    def _normalize_query(self, item: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize query input from either string or dictionary."""
        if isinstance(item, str):
            return {
                "query": item,
                "organic_top10": None,
                "organic_rank": None
            }
        elif isinstance(item, dict):
            query = item.get("query", "")
            rank = item.get("organic_rank")
            top10 = item.get("organic_top10")
            if top10 is None and rank is not None:
                top10 = (1 <= rank <= 10)
            return {
                "query": query,
                "organic_top10": top10,
                "organic_rank": rank
            }
        return {"query": str(item), "organic_top10": None, "organic_rank": None}

    def run_audit(
        self,
        queries_data: Dict[str, Any],
        engine_func: Optional[Any] = None,
        assume_organic_if_missing: bool = False
    ) -> Dict[str, Any]:
        """Execute complete FastUp GAS audit across non-branded, brand, and person queries."""
        raw_non_branded = queries_data.get("non_branded", [])
        raw_brand = queries_data.get("brand", [])
        raw_person = queries_data.get("person", [])

        non_branded = [self._normalize_query(q) for q in raw_non_branded]
        brand = [self._normalize_query(q) for q in raw_brand]
        person = [self._normalize_query(q) for q in raw_person]

        query_runner = engine_func or self.query_openrouter

        results: Dict[str, Any] = {
            "version": "1.4.3",
            "timestamp": datetime.utcnow().isoformat(),
            "target": {
                "domain": self.target_domain,
                "brand": self.target_brand,
                "person": self.target_person,
            },
            "non_branded_scores": [],
            "brand_scores": [],
            "person_scores": [],
            "pcl_score": 0,
            "scg_details": {
                "total_queries": len(non_branded),
                "top10_organic_count": 0,
                "gap_count": 0,
                "mode": "verified_serp" if any(q["organic_top10"] is not None for q in non_branded) else "estimated_all_queries"
            },
            "metrics": {},
        }

        _safe_log(f"[*] Running FastUp GAS v1.4.3 Audit for {self.target_brand.title()} ({self.target_domain})...")

        # 1. Non-branded (NVI & SCG)
        total_scale_a = 0
        organic_eligible_count = 0
        gap_count = 0

        for q_item in non_branded:
            q_text = q_item["query"]
            res = query_runner(q_text)
            text = res.get("text", "")
            sources = res.get("sources", [])

            score = self.score_scale_a(text, sources)
            total_scale_a += score

            # Determine organic Top-10 status
            if q_item["organic_top10"] is not None:
                in_organic = q_item["organic_top10"]
            elif assume_organic_if_missing:
                in_organic = True
            else:
                in_organic = None

            is_cited = (score >= 2)
            is_gap = (in_organic is True and not is_cited) if in_organic is not None else (not is_cited)

            if in_organic is True:
                organic_eligible_count += 1
                if is_gap:
                    gap_count += 1
            elif in_organic is None and assume_organic_if_missing:
                organic_eligible_count += 1
                if is_gap:
                    gap_count += 1

            results["non_branded_scores"].append({
                "query": q_text,
                "score": score,
                "is_cited": is_cited,
                "in_organic_top10": in_organic,
                "organic_rank": q_item["organic_rank"],
                "is_gap": is_gap,
                "sources": sources[:3],
            })

        max_nvi_points = len(non_branded) * 3
        nvi = (total_scale_a / max_nvi_points) * 100 if max_nvi_points > 0 else 0.0

        # SCG calculation
        if organic_eligible_count > 0:
            scg = (gap_count / organic_eligible_count) * 100.0
            results["scg_details"]["top10_organic_count"] = organic_eligible_count
            results["scg_details"]["gap_count"] = gap_count
        else:
            un_cited_total = sum(1 for item in results["non_branded_scores"] if not item["is_cited"])
            scg = (un_cited_total / len(non_branded)) * 100.0 if non_branded else 0.0
            results["scg_details"]["top10_organic_count"] = len(non_branded)
            results["scg_details"]["gap_count"] = un_cited_total

        # 2. Brand Knowledge (CBK)
        total_brand_score = 0
        for q_item in brand:
            q_text = q_item["query"]
            res = query_runner(q_text)
            score = self.score_scale_b(res.get("text", ""), res.get("sources", []), self.target_brand)
            total_brand_score += score
            results["brand_scores"].append({
                "query": q_text,
                "score": score,
                "text_snippet": res.get("text", "")[:150],
            })

        max_brand_points = len(brand) * 3
        cbk = (total_brand_score / max_brand_points) * 100 if max_brand_points > 0 else 0.0
        cbk = max(-100.0, round(cbk, 1))

        # 3. Person Knowledge (PKS)
        total_person_score = 0
        for q_item in person:
            q_text = q_item["query"]
            res = query_runner(q_text)
            score = self.score_scale_b(res.get("text", ""), res.get("sources", []), self.target_person)
            total_person_score += score
            results["person_scores"].append({
                "query": q_text,
                "score": score,
                "text_snippet": res.get("text", "")[:150],
            })

        max_person_points = len(person) * 3
        pks = (total_person_score / max_person_points) * 100 if max_person_points > 0 else 0.0
        pks = max(-100.0, round(pks, 1))

        # 4. Person-Company Link (PCL: 0-6 score)
        pcl_engine_score = 0
        p1_res = query_runner(f"Кто такой {self.target_person.title()} в Беларуси?")
        p1_text = p1_res.get("text", "").lower()
        p1_sources = [s.lower() for s in p1_res.get("sources", [])]

        if self.target_brand in p1_text or self.target_domain in p1_text or any(self.target_domain in s for s in p1_sources):
            pcl_engine_score = 2
        else:
            p2_res = query_runner(f"{self.target_person.title()} связан с компанией {self.target_brand.title()}?")
            p2_text = p2_res.get("text", "").lower()
            if self.target_brand in p2_text or self.target_domain in p2_text or "да" in p2_text[:50]:
                pcl_engine_score = 1

        results["pcl_score"] = pcl_engine_score
        results["metrics"] = {
            "NVI": round(nvi, 1),
            "CBK": round(cbk, 1),
            "PKS": round(pks, 1),
            "PCL": pcl_engine_score,
            "SCG": round(scg, 1),
        }
        return results

    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate structured markdown report from audit results."""
        m = results["metrics"]
        t = results["target"]
        scg_info = results.get("scg_details", {})

        md = []
        md.append(f"# Отчет GEO-аудита FastUp GAS: {t['brand'].title()} ({t['domain']})")
        md.append(f"\n**Дата замера:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        md.append(f"**Методика:** FastUp GAS v{results.get('version', '1.4.3')} ([Спецификация и документация](https://fastup.by/geo-audit-system/))")
        md.append(f"**Объект аудита:** Домен `{t['domain']}`, Бренд `{t['brand'].title()}`, Персона `{t['person'].title()}`\n")
        md.append("---")
        md.append("\n## 📊 Сводные метрики видимости в нейросетях (FastUp GAS)")
        md.append("\n| Метрика | Код | Значение | Шкала | Интерпретация |")
        md.append("|---|---|---|---|---|")
        md.append(f"| **Небрендовая видимость** | `NVI` | **{m['NVI']}%** | 0..100% | Доля рекомендаций и цитирований при поиске услуг без бренда |")
        md.append(f"| **Знание о компании** | `CBK` | **{m['CBK']}%** | -100..100% | Полнота и точность фактологических ответов ИИ при прямом запросе |")
        md.append(f"| **Знание о персоне** | `PKS` | **{m['PKS']}%** | -100..100% | Узнаваемость спикера/эксперта в ИИ без подсказки бренда |")
        md.append(f"| **Связка Личность ↔ Компания** | `PCL` | **{m['PCL']} / 6** | 0..6 | Способность ИИ связать персону с компанией |")
        md.append(f"| **Расхождение Поиск/ИИ** | `SCG` | **{m['SCG']}%** | 0..100% | Доля запросов из ТОП-10 органики, отсутствующих в ИИ-ответах |")

        if scg_info.get("mode") == "verified_serp":
            md.append(f"\n> ℹ️ *SCG рассчитан на основе подтвержденных позиций ТОП-10 органического поиска ({scg_info.get('gap_count')}/{scg_info.get('top10_organic_count')} в разрыве).*")
        else:
            md.append(f"\n> ℹ️ *SCG рассчитан по общему пулу небрендовых запросов (для точной калибровки укажите `organic_top10: true` в queries.json).*")

        md.append("\n---")
        md.append("\n## 🔍 Детализация по небрендовым запросам (NVI / SCG)")
        md.append("\n| Запрос | Балл (Шкала A: 0-3) | Органика ТОП-10 | Статус SCG | Источники ИИ |")
        md.append("|---|---|---|---|---|")
        for item in results.get("non_branded_scores", []):
            org_status = f"Топ-{item['organic_rank']}" if item.get("organic_rank") else ("Да" if item.get("in_organic_top10") else "—")
            gap_status = "⚠️ Разрыв (в ТОП, нет в ИИ)" if item.get("is_gap") else ("✅ Цитируется" if item.get("is_cited") else "⚪ Не цитируется")
            srcs = ", ".join(item.get("sources", [])) if item.get("sources") else "—"
            md.append(f"| {item['query']} | {item['score']} | {org_status} | {gap_status} | `{srcs}` |")

        md.append("\n---")
        md.append("\n## 🏢 Детализация: Знание о компании (CBK) и персоне (PKS)")
        md.append("\n| Тип | Запрос | Балл (Шкала B: -1..3) | Примечание |")
        md.append("|---|---|---|---|")
        for item in results.get("brand_scores", []):
            md.append(f"| Бренд (`CBK`) | {item['query']} | **{item['score']}** | {item.get('text_snippet', '')[:80]}... |")
        for item in results.get("person_scores", []):
            md.append(f"| Персона (`PKS`) | {item['query']} | **{item['score']}** | {item.get('text_snippet', '')[:80]}... |")

        md.append("\n---\n")
        md.append("💡 *Отчет сгенерирован автоматически открытым инструментом FastUp GAS CLI (v1.4.3).*")
        md.append("Разработано [FastUp.by](https://fastup.by/) — Маркетинговое агентство в Беларуси.")
        return "\n".join(md)
