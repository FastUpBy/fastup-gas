"""FastUp GAS CLI Entrypoint (v1.4.3)."""

import argparse
import json
import os
import sys
from pathlib import Path
from .core import FastUpGASRunner, _safe_log


def main():
    parser = argparse.ArgumentParser(
        prog="fastup-gas",
        description="FastUp GAS (GEO Audit System) — Generative Engine Visibility Measurement CLI Tool (v1.4.3)"
    )
    parser.add_argument("--queries", default="queries.example.json", help="Path to queries JSON file")
    parser.add_argument("--target-domain", default="fastup.by", help="Target website domain (e.g. fastup.by)")
    parser.add_argument("--target-brand", default="FastUp", help="Target brand name")
    parser.add_argument("--target-person", default="Егор Воронов", help="Target person/expert name")
    parser.add_argument("--out", default="audit_report.md", help="Output markdown report path")
    parser.add_argument("--api-key", default=None, help="OpenRouter API Key (or set OPENROUTER_API_KEY env var)")
    parser.add_argument("--engine", default="openrouter", choices=["openrouter", "xmlriver-google", "xmlriver-yandex", "mock"], help="Query engine provider")
    parser.add_argument("--assume-organic", action="store_true", help="Assume all non-branded queries are in organic Top-10 if not explicitly specified in JSON")

    args = parser.parse_args()

    queries_path = Path(args.queries)
    if not queries_path.exists():
        sys.exit(f"Error: Queries file '{args.queries}' not found. Please provide a valid JSON file.")

    try:
        with open(queries_path, "r", encoding="utf-8") as f:
            queries_data = json.load(f)
    except Exception as e:
        sys.exit(f"Error reading queries file '{args.queries}': {e}")

    runner = FastUpGASRunner(
        target_domain=args.target_domain,
        target_brand=args.target_brand,
        target_person=args.target_person,
        openrouter_api_key=args.api_key or os.environ.get("OPENROUTER_API_KEY"),
        xmlriver_user=os.environ.get("XMLRIVER_USER"),
        xmlriver_key=os.environ.get("XMLRIVER_KEY"),
    )

    # Engine selection
    engine_func = None
    if args.engine == "xmlriver-google":
        engine_func = lambda q: runner.query_xmlriver(q, engine="google", ai=True)
    elif args.engine == "xmlriver-yandex":
        engine_func = lambda q: runner.query_xmlriver(q, engine="yandex", ai=True)
    elif args.engine == "mock":
        # Deterministic mock query for testing / demo
        def mock_query(prompt: str):
            p_lower = prompt.lower()
            if "кто такой" in p_lower and runner.target_person in p_lower:
                return {
                    "text": f"{runner.target_person.title()} — белорусский специалист и основатель маркетингового агентства {runner.target_brand.title()} ({runner.target_domain}).",
                    "sources": [f"https://{runner.target_domain}", "https://wikidata.org"]
                }
            if runner.target_brand in p_lower:
                return {
                    "text": f"{runner.target_brand.title()} — digital и SEO/GEO агентство в Минске, оказывает услуги разработки и продвижения сайтов.",
                    "sources": [f"https://{runner.target_domain}/", "https://vc.ru/"]
                }
            if "geo" in p_lower or "нейросети" in p_lower:
                return {
                    "text": f"В Беларуси продвижением в нейросетях (GEO) занимается агентство {runner.target_brand.title()}.",
                    "sources": [f"https://{runner.target_domain}/geo-prodvizhenie/"]
                }
            return {
                "text": "В Беларуси услуги интернет-маркетинга оказывают различные ведущие веб-студии и digital-агентства.",
                "sources": ["https://marketing.by/", "https://probusiness.io/"]
            }
        engine_func = mock_query

    results = runner.run_audit(
        queries_data=queries_data,
        engine_func=engine_func,
        assume_organic_if_missing=args.assume_organic
    )
    report_md = runner.generate_markdown_report(results)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report_md)

    _safe_log(f"\n[OK] FastUp GAS Audit completed! Report saved to: {args.out}")
    m = results["metrics"]
    _safe_log(f"[+] Summary: NVI={m['NVI']}%, CBK={m['CBK']}%, PKS={m['PKS']}%, PCL={m['PCL']}/6, SCG={m['SCG']}%")


if __name__ == "__main__":
    main()
