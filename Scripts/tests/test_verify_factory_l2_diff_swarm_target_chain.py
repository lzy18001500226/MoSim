import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "sunray" / "verify_factory_l2_diff_swarm_target_chain.py"


def load_verifier_module():
    spec = importlib.util.spec_from_file_location("target_chain_verifier", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_load_object_accepts_powershell_utf8_bom(tmp_path: Path) -> None:
    verifier = load_verifier_module()
    fixture = tmp_path / "probe.json"
    fixture.write_text(json.dumps({"status": "passed"}), encoding="utf-8-sig")

    assert verifier.load_object(fixture) == {"status": "passed"}
