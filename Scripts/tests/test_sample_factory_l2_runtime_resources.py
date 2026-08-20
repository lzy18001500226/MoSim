from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SAMPLER = ROOT / "Scripts" / "sunray" / "sample_factory_l2_runtime_resources.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sample_factory_l2_runtime_resources", SAMPLER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_process_rows_keeps_command_arguments_separate() -> None:
    module = load_module()

    rows = module.parse_process_rows(
        "  40    10  12.5  0.1  1234 gzserver /usr/bin/gzserver --verbose\n"
    )

    assert rows == [
        {
            "pid": 40,
            "ppid": 10,
            "cpu_percent": 12.5,
            "memory_percent": 0.1,
            "rss_kib": 1234,
            "command": "gzserver",
            "arguments": "/usr/bin/gzserver --verbose",
        }
    ]


def test_descendant_process_ids_excludes_unrelated_processes() -> None:
    module = load_module()
    processes = [
        {"pid": 10, "ppid": 1},
        {"pid": 11, "ppid": 10},
        {"pid": 12, "ppid": 11},
        {"pid": 13, "ppid": 1},
    ]

    assert module.descendant_process_ids(processes, 10) == {10, 11, 12}
    assert module.descendant_process_ids(processes, 99) == set()
