import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


builder = load_module(
    "build_offline_expansion_inventory",
    ROOT / "Scripts/quality/build_offline_expansion_inventory.py",
)
checker = load_module(
    "check_offline_expansion_inventory",
    ROOT / "Scripts/quality/check_offline_expansion_inventory.py",
)


class OfflineExpansionInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "Config/control_platform/offline_expansion_inventory.json"
        cls.data = json.loads(cls.path.read_text(encoding="utf-8"))

    def test_inventory_is_reproducible_from_frozen_baseline(self):
        self.assertEqual(builder.build_inventory(), self.data)

    def test_checked_inventory_passes(self):
        self.assertEqual([], checker.validate(self.data))
        self.assertEqual(77, len(self.data["modules"]))

    def test_blocked_module_cannot_be_default_legal_profile(self):
        changed = copy.deepcopy(self.data)
        blocked = next(
            module
            for module in changed["modules"]
            if module["baseline_maturity"] == "blocked"
        )
        blocked["legal_default_profile_state"] = "DEFAULT_PROFILE_REQUIRED"
        errors = checker.validate(changed)
        self.assertTrue(any("blocked module" in error for error in errors))

    def test_duplicate_module_id_fails(self):
        changed = copy.deepcopy(self.data)
        changed["modules"][1]["module_id"] = changed["modules"][0]["module_id"]
        errors = checker.validate(changed)
        self.assertTrue(any("duplicate module_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
