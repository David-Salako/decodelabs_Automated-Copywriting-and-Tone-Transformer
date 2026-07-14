"""
Automated Copywriting & Tone Transformer -- CLI entry point.

Interactive mode (just run it, it will prompt you):
    python main.py

Single mode (flags, good for scripting):
    python main.py --product "Nova Sneakers" --description "Lightweight running shoes with carbon-fiber soles" --tone witty --platform instagram

Batch mode (reads a CSV, generates copy for every row concurrently):
    python main.py --batch products.csv
"""

import argparse
import asyncio
import json
import sys

from gemini_client import generate_copy
from batch_runner import run_batch
from prompt_templates import PLATFORM_CONFIGS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate platform-tailored marketing copy with Gemini."
    )
    parser.add_argument("--product", help="Product name")
    parser.add_argument("--description", help="Raw product description")
    parser.add_argument("--tone", help="Tone, e.g. witty, professional, urgent")
    parser.add_argument(
        "--platform",
        choices=list(PLATFORM_CONFIGS.keys()),
        help="Target platform",
    )
    parser.add_argument("--batch", metavar="CSV_PATH", help="Path to a CSV for batch mode")
    return parser


def prompt_for_input() -> dict:
    """Interactive mode: asks the user for each value at the terminal."""
    print("=== Automated Copywriting & Tone Transformer ===\n")

    product = input("Product name: ").strip()
    description = input("Product description: ").strip()
    tone = input("Tone (e.g. witty, professional, urgent, friendly): ").strip()

    platforms = list(PLATFORM_CONFIGS.keys())
    print(f"Platform options: {', '.join(platforms)}")
    platform = input("Platform: ").strip().lower()

    while platform not in platforms:
        print(f"'{platform}' isn't valid. Choose from: {', '.join(platforms)}")
        platform = input("Platform: ").strip().lower()

    return {
        "product": product,
        "description": description,
        "tone": tone,
        "platform": platform,
    }


def run_single(args) -> None:
    missing = [
        name
        for name, val in [
            ("--product", args.product),
            ("--description", args.description),
            ("--tone", args.tone),
            ("--platform", args.platform),
        ]
        if not val
    ]
    if missing:
        print(f"Missing required arguments: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    try:
        result = generate_copy(
            product_name=args.product,
            description=args.description,
            tone=args.tone,
            platform=args.platform,
        )
    except Exception as exc:
        print(f"Copy generation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\n=== {args.platform.upper()} COPY ({args.tone}) ===\n")
    print(f"Headline: {result.headline}\n")
    print(f"{result.body}\n")
    print(f"CTA: {result.call_to_action}")
    if result.hashtags:
        print(f"Hashtags: {' '.join('#' + h.lstrip('#') for h in result.hashtags)}")


def run_batch_mode(csv_path: str) -> None:
    results = asyncio.run(run_batch(csv_path))
    output = [r.model_dump() for r in results]
    out_path = "batch_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    ok = sum(1 for r in results if r.error is None)
    print(f"Generated {ok}/{len(results)} entries successfully.")
    print(f"Full results saved to {out_path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.batch:
        run_batch_mode(args.batch)
        return

    # No flags at all -> drop into interactive mode and ask for each value.
    if not any([args.product, args.description, args.tone, args.platform]):
        answers = prompt_for_input()
        args.product = answers["product"]
        args.description = answers["description"]
        args.tone = answers["tone"]
        args.platform = answers["platform"]

    run_single(args)


if __name__ == "__main__":
    main()