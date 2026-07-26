from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUALITY_DIR = ROOT / "Scripts" / "quality"
if str(QUALITY_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_DIR))

from build_g6_controller_execution_matrix import (  # noqa: E402
    g6_route_source_projection,
    route_binding_change_ids,
    source_migration_transition,
    value_sha256,
)


def harness_row(scheme_id: str = "route_00") -> dict[str, object]:
    return {
        "scheme_id": scheme_id,
        "category": "pid_family",
        "formal_harness_state": "missing_closed_loop_harness",
        "current_model_file": f"Models/{scheme_id}.mo",
        "current_model_class": f"MoSim.{scheme_id}",
    }


def matrix_row(index: int) -> dict[str, object]:
    scheme_id = f"route_{index:02d}"
    return {
        "scheme_id": scheme_id,
        "category": "pid_family",
        "evidence_class": "internal_fixed_input_probe",
        "formal_harness_state": "missing_closed_loop_harness",
        "target": {
            "model_file": f"Models/{scheme_id}.mo",
            "model_class": f"MoSim.{scheme_id}",
            "model_sha256": f"hash-{index}",
        },
        "model_load_prerequisites": [],
        "controller_core": {
            "model_file": f"Models/{scheme_id}.mo",
            "model_class": f"MoSim.{scheme_id}",
            "model_sha256": f"hash-{index}",
        },
        "probe_contract": {"input": {"kind": "fixed"}, "result_variables": ["u"]},
        "result_root": f"Results/{scheme_id}",
        "required_artifacts": {"run_record": f"Results/{scheme_id}/RUN_RECORD.json"},
        "state": "pending",
        "claim_boundary": "internal only",
    }


class G6MatrixMetadataContractTests(unittest.TestCase):
    def test_route_projection_ignores_post_g6_metadata_but_not_route_inputs(self) -> None:
        baseline = {
            "schemes": [harness_row()],
            "summary": {"current_mworks_candidate_count": 46},
            "provisional_champion_selection": {"state": "not_selected"},
        }
        metadata_changed = copy.deepcopy(baseline)
        metadata_changed["summary"] = {"provisional_champion_selection_count": 6}
        metadata_changed["provisional_champion_selection"] = {"state": "provisional_selection_recorded"}
        self.assertEqual(
            value_sha256(g6_route_source_projection(baseline)),
            value_sha256(g6_route_source_projection(metadata_changed)),
        )

        route_changed = copy.deepcopy(baseline)
        route_changed["schemes"][0]["current_model_file"] = "Models/changed.mo"
        self.assertNotEqual(
            value_sha256(g6_route_source_projection(baseline)),
            value_sha256(g6_route_source_projection(route_changed)),
        )

    def test_metadata_refresh_rejects_any_route_binding_change(self) -> None:
        previous = {"rows": [matrix_row(index) for index in range(46)]}
        metadata_only = copy.deepcopy(previous)
        self.assertEqual(route_binding_change_ids(previous, metadata_only), [])

        route_changed = copy.deepcopy(previous)
        route_changed["rows"][7]["target"]["model_sha256"] = "changed-target-hash"
        self.assertEqual(route_binding_change_ids(previous, route_changed), ["route_07"])

    def test_source_migration_permits_only_project_root_source_moves(self) -> None:
        previous = {"rows": [matrix_row(index) for index in range(46)]}
        for row in previous["rows"]:
            scheme_id = str(row["scheme_id"])
            for field in ("target", "controller_core"):
                source = row[field]
                source["model_file"] = (
                    f"Models/MoSimQuadrotorModel/Controllers/{scheme_id}.mo"
                )
                source["model_class"] = f"MoSimQuadrotorModel.Controllers.{scheme_id}"

        refreshed = copy.deepcopy(previous)
        for row in refreshed["rows"]:
            scheme_id = str(row["scheme_id"])
            for field in ("target", "controller_core"):
                source = row[field]
                source["model_file"] = f"Models/MoSimQuadrotorModel/Control/{scheme_id}.mo"
                source["model_class"] = f"MoSimQuadrotorModel.Control.{scheme_id}"
                source["model_sha256"] = f"current-hash-{scheme_id}"

        transition = source_migration_transition(previous, refreshed)
        self.assertEqual(transition["changed_route_count"], 46)
        self.assertEqual(transition["unchanged_route_count"], 0)

        changed_probe = copy.deepcopy(refreshed)
        changed_probe["rows"][0]["probe_contract"] = {"input": {"kind": "different"}}
        with self.assertRaisesRegex(ValueError, "probe_contract"):
            source_migration_transition(previous, changed_probe)

        hash_only = copy.deepcopy(previous)
        hash_only["rows"][0]["target"]["model_sha256"] = "unexpected-law-change"
        with self.assertRaisesRegex(ValueError, "path move"):
            source_migration_transition(previous, hash_only)


if __name__ == "__main__":
    unittest.main()
