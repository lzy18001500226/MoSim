"""WebTailBench benchmark integration tests.

These test the dataset loader path: download the official HF dataset,
parse it, and verify the expected fields/categories are populated. They
do NOT invoke the MMRubricAgent judge (no LLM calls).

Mark the ``download`` test with ``pytest -m download`` to skip the HF
round-trip when running offline — the TSV-parser test stands in with a
synthetic fixture.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import pytest


# Category names as they appear in the TSV at time of writing. The README
# shows pretty names ("Hotels", "Shopping", …); the TSV ships the
# underlying split ids ("hotels_head", "shopping_head", …). We keep both
# style-guide and TSV variants here — the test passes if ~half match.
_EXPECTED_CATEGORIES = {
    "flights",
    "hotels_head",
    "shopping_head",
    "restaurants_tail",
    "things_to_do",
    "ticketing",
    "realestate_complex",
    "jobs",
    "shopping_lists_tail",
    "price_comparison",
    "compositional_tasks_v2",
}


def _write_fixture_tsv(
    path: Path, rows: list[dict], fieldnames: list[str] | None = None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = fieldnames or ["benchmark", "id", "task_summary"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def test_benchmark_loads_from_local_tsv_fixture(tmp_path):
    """``load_dataset()`` should consume a TSV placed directly in
    ``data_dir`` without hitting Hugging Face."""
    from webeval.benchmarks import WebTailBenchBenchmark

    fixture = tmp_path / "WebTailBench.tsv"
    _write_fixture_tsv(
        fixture,
        [
            {"benchmark": "flights", "id": "delta_01", "task_summary": "find a flight"},
            {"benchmark": "hotels", "id": "hilton_02", "task_summary": "book a room"},
            {
                "benchmark": "shopping",
                "id": "amazon_03",
                "task_summary": "buy a mouse",
            },
        ],
    )

    bench = WebTailBenchBenchmark(data_dir=str(tmp_path))
    bench.load_dataset()

    assert len(bench.examples) == 3
    ids = {e["id"] for e in bench.examples}
    assert ids == {"delta_01", "hilton_02", "amazon_03"}
    splits = {e["split"] for e in bench.examples}
    assert splits == {"flights", "hotels", "shopping"}

    # get_split_examples must filter correctly.
    flights_only = bench.get_split_examples("flights")
    assert len(flights_only) == 1
    assert flights_only[0]["question"] == "find a flight"

    # None / "*" / "" should return everything.
    assert len(bench.get_split_examples(None)) == 3
    assert len(bench.get_split_examples("*")) == 3


def test_loader_parses_precomputed_rubric(tmp_path):
    """``WebTailBench-v1-rubrics.tsv`` carries a JSON ``precomputed_rubric``
    column. The loader must parse it and stash it on each example so the
    Universal Verifier scores against the published rubric."""
    import json

    from webeval.benchmarks import WebTailBenchBenchmark

    fixture = tmp_path / "WebTailBench-v1-rubrics.tsv"
    rubric_obj = {
        "items": [
            {"criterion": "Use direct flights only", "max_points": 1},
            {"criterion": "Cite a USD price", "max_points": 1},
        ],
        "total_max_points": 2,
    }
    _write_fixture_tsv(
        fixture,
        [
            {
                "benchmark": "flights",
                "id": "united_13",
                "task_summary": "find a flight",
                "precomputed_rubric": json.dumps(rubric_obj),
            },
            {
                "benchmark": "hotels",
                "id": "hilton_99",
                "task_summary": "book a hotel",
                "precomputed_rubric": "",  # missing rubric
            },
        ],
        fieldnames=["benchmark", "id", "task_summary", "precomputed_rubric"],
    )

    bench = WebTailBenchBenchmark(data_dir=str(tmp_path))
    bench.load_dataset()

    by_id = {e["id"]: e for e in bench.examples}
    assert "precomputed_rubric" in by_id["united_13"]
    assert by_id["united_13"]["precomputed_rubric"]["total_max_points"] == 2
    assert (
        by_id["united_13"]["precomputed_rubric"]["items"][0]["criterion"]
        == "Use direct flights only"
    )
    # Empty rubric column must NOT silently produce a placeholder.
    assert "precomputed_rubric" not in by_id["hilton_99"]


def test_precomputed_rubric_threads_into_datapoint(tmp_path):
    """End-to-end: rubric column → example dict → DataPoint.task.metadata.

    This is the contract the Universal Verifier relies on:
    ``MMRubricAgent._extract_input_from_datapoint`` reads
    ``dp.task.metadata['precomputed_rubric']``.
    """
    import json

    from webeval.benchmarks.webtailbench.shared_data_adapter import create_datapoint

    rubric_obj = {"items": [{"criterion": "X", "max_points": 1}], "total_max_points": 1}
    task_data = {
        "id": "t1",
        "question": "do thing",
        "init_url": "https://example.com",
        "split": "flights",
        "category": "flights",
        "precomputed_rubric": rubric_obj,
    }

    # Minimal stand-in for a Trajectory (only attrs the adapter touches).
    class _StubAnswer:
        screenshots: list = []
        final_answer = "done"

    class _StubTraj:
        def __init__(self, p):
            self.path = p
            self.events = []
            self.answer = _StubAnswer()

    candidate = _StubTraj(tmp_path)
    dp = create_datapoint(task_data, candidate)
    assert dp.task.metadata.get("precomputed_rubric") == rubric_obj


@pytest.mark.skipif(
    os.environ.get("WEBTAILBENCH_ALLOW_DOWNLOAD") != "1",
    reason="Set WEBTAILBENCH_ALLOW_DOWNLOAD=1 to run HF download tests",
)
def test_hf_download_pulls_rubrics_file(tmp_path):
    """Live HF download: must pull ``WebTailBench-v1-rubrics.tsv`` and
    every loaded example must carry a ``precomputed_rubric``."""
    from webeval.benchmarks import WebTailBenchBenchmark

    bench = WebTailBenchBenchmark(data_dir=str(tmp_path))
    bench.download_dataset()
    assert (tmp_path / "WebTailBench-v1-rubrics.tsv").exists(), (
        "Loader must download the rubrics file, not the bare WebTailBench.tsv"
    )

    bench.load_dataset()
    assert len(bench.examples) > 500
    missing = [e["id"] for e in bench.examples if "precomputed_rubric" not in e]
    assert not missing, (
        f"{len(missing)}/{len(bench.examples)} examples are missing precomputed_rubric "
        f"(first few: {missing[:5]}). Universal Verifier would silently regenerate."
    )

    categories = {ex["split"] for ex in bench.examples}
    overlap = categories & _EXPECTED_CATEGORIES
    assert len(overlap) >= 6, (
        f"Too few expected categories found: {overlap}. Dataset schema may have changed."
    )
