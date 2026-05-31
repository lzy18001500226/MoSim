#!/usr/bin/env python3
"""Simple evaluation script for HeavySkill outputs."""

import argparse
import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from workflow.utils import extract_boxed_answer


def normalize_answer(answer: str) -> str:
    answer = answer.strip()
    answer = re.sub(r"\s+", " ", answer)
    return answer


def evaluate_single(predicted: str, target: str) -> bool:
    pred = normalize_answer(extract_boxed_answer(predicted) or predicted[-200:])
    tgt = normalize_answer(target)

    if pred == tgt:
        return True
    try:
        return abs(float(pred) - float(tgt)) < 1e-6
    except (ValueError, TypeError):
        pass
    return pred.lower() == tgt.lower()


def main():
    parser = argparse.ArgumentParser(description="Evaluate HeavySkill outputs")
    parser.add_argument("--result_file", type=str, required=True, help="Output JSON from run_heavyskill.py")
    parser.add_argument("--target_file", type=str, required=True, help="JSON file with targets [{query, target}, ...]")
    args = parser.parse_args()

    with open(args.result_file, "r", encoding="utf-8") as f:
        results = json.load(f)
    with open(args.target_file, "r", encoding="utf-8") as f:
        targets = json.load(f)

    target_map = {}
    for item in targets:
        target_map[item["query"]] = item["target"]

    correct = 0
    total = 0
    for result in results:
        query = result["query"]
        if query not in target_map:
            print(f"WARNING: No target for query: {query[:80]}...")
            continue
        target = target_map[query]
        predicted = result["final_answer"]
        is_correct = evaluate_single(predicted, target)
        correct += int(is_correct)
        total += 1
        status = "PASS" if is_correct else "FAIL"
        print(f"[{status}] {query[:60]}... -> {extract_boxed_answer(predicted) or '(no boxed)'}")

    print(f"\nAccuracy: {correct}/{total} = {correct/total*100:.1f}%" if total > 0 else "No evaluable results")


if __name__ == "__main__":
    main()
