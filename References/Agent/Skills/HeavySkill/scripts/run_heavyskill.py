#!/usr/bin/env python3
"""CLI entry point for HeavySkill workflow."""

import argparse
import asyncio
import json
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from workflow.config import HeavySkillConfig
from workflow.pipeline import run_heavyskill


def parse_args():
    parser = argparse.ArgumentParser(
        description="HeavySkill: Heavy Thinking as the Inner Skill"
    )

    # Input
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--query", type=str, help="Single query string")
    input_group.add_argument(
        "--input_file", type=str, help="JSON file with queries (list of strings or list of {query, ...})"
    )

    # Model
    parser.add_argument("--model", type=str, required=True, help="Model name for reasoning")
    parser.add_argument("--api_base", type=str, required=True, help="OpenAI-compatible API base URL")
    parser.add_argument("--api_key", type=str, default="EMPTY", help="API key (default: EMPTY)")

    # Summary model (optional, defaults to same as reasoning model)
    parser.add_argument("--summary_model", type=str, default=None, help="Model name for deliberation (default: same as --model)")
    parser.add_argument("--summary_api_base", type=str, default=None, help="API base for deliberation model")
    parser.add_argument("--summary_api_key", type=str, default=None, help="API key for deliberation model")

    # Pipeline parameters
    parser.add_argument("--reason_k", type=int, default=8, help="Number of parallel reasoning trajectories (default: 8)")
    parser.add_argument("--summary_k", type=int, default=4, help="Number of deliberation samples (default: 4)")
    parser.add_argument("--iterations", type=int, default=1, help="Number of deliberation iterations (default: 1)")
    parser.add_argument("--max_trajectory_tokens", type=int, default=80000, help="Max total tokens for trajectories")

    # Prompt
    parser.add_argument("--prompt_type", type=str, default="general", choices=["general", "stem"], help="Prompt template type")
    parser.add_argument("--language", type=str, default="en", choices=["en", "cn"], help="Language for prompts")

    # Generation parameters
    parser.add_argument("--reason_temperature", type=float, default=1.0)
    parser.add_argument("--reason_max_tokens", type=int, default=32768)
    parser.add_argument("--summary_temperature", type=float, default=0.7)
    parser.add_argument("--summary_max_tokens", type=int, default=32768)

    # Output
    parser.add_argument("--output", type=str, default=None, help="Output JSON file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    return parser.parse_args()


def load_queries(args) -> list:
    if args.query:
        return [args.query]

    with open(args.input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        if data and isinstance(data[0], str):
            return data
        return [item["query"] for item in data]
    raise ValueError("Input file must contain a JSON list of strings or objects with 'query' field")


async def main():
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = HeavySkillConfig(
        model_name=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        reason_k=args.reason_k,
        summary_k=args.summary_k,
        iterations=args.iterations,
        max_trajectory_tokens=args.max_trajectory_tokens,
        prompt_type=args.prompt_type,
        language=args.language,
        reason_temperature=args.reason_temperature,
        reason_max_tokens=args.reason_max_tokens,
        summary_temperature=args.summary_temperature,
        summary_max_tokens=args.summary_max_tokens,
        summary_model_name=args.summary_model,
        summary_api_base=args.summary_api_base,
        summary_api_key=args.summary_api_key,
    )

    queries = load_queries(args)
    results = []

    for i, query in enumerate(queries):
        logging.info("Processing query %d/%d", i + 1, len(queries))
        result = await run_heavyskill(query, config)
        results.append({
            "query": result.query,
            "final_answer": result.final_answer,
            "num_trajectories": len(result.trajectories),
            "num_summaries": len(result.summaries),
            "iterations": result.iterations_done,
            "trajectories": result.trajectories,
            "summaries": result.summaries,
        })

        print(f"\n{'='*60}")
        print(f"Query {i+1}: {query[:100]}...")
        print(f"{'='*60}")
        print(f"Trajectories: {len(result.trajectories)}")
        print(f"Final Answer:\n{result.final_answer[:500]}...")
        print()

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logging.info("Results saved to %s", args.output)
    elif len(results) == 1:
        print("\n" + "=" * 60)
        print("FINAL ANSWER:")
        print("=" * 60)
        print(results[0]["final_answer"])


if __name__ == "__main__":
    asyncio.run(main())
