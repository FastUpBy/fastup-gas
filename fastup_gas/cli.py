"""FastUp GAS CLI Entrypoint."""

import argparse
import json
import os
import sys
from pathlib import Path
from .core import FastUpGASRunner


def main():
    parser = argparse.ArgumentParser(
        prog="fastup-gas",
        description="FastUp GAS (GEO Audit System) — Generative Engine Visibility Measurement CLI Tool"
    )
    parser.add_argument("--queries", default="queries.example.json", help="Path to queries JSON file")
    parser.add_argument("--target-domain", default="fastup.by", help="Target website domain (e.g. fastup.by)")
    parser.add_argument("--target-brand", default="FastUp", help="Target brand name")
    parser.add_argument("--target-person", default="Егор Воронов", help="Target person name")
    parser.add_argument("--out", default="audit_report.md", help="Output markdown report path")
    parser.add_argument("--api-key", default=None, help="OpenRouter API Key (or set OPENROUTER_API_KEY env var)")

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
        openrouter_api_key=args.api_key or os.environ.get("OPENROUTER_API_KEY")
    )

    results = runner.run_audit(queries_data)
    report_md = runner.generate_markdown_report(results)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n✅ FastUp GAS Audit completed! Report saved to: {args.out}")
    m = results["metrics"]
    print(f"📈 Summary: NVI={m['NVI']}%, CBK={m['CBK']}%, PKS={m['PKS']}%, PCL={m['PCL']}/6, SCG={m['SCG']}%")


if __name__ == "__main__":
    main()
