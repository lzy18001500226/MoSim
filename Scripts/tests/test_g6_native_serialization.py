from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUALITY_DIR = ROOT / "Scripts" / "quality"
if str(QUALITY_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_DIR))

from current_model_entry_map_lib import direct_graphical_native_text


MWORKS_DIR = ROOT / "Scripts" / "mworks"
if str(MWORKS_DIR) not in sys.path:
    sys.path.insert(0, str(MWORKS_DIR))

import run_g6_controller_execution as execution  # noqa: E402


class G6NativeSerializationTests(unittest.TestCase):
    def test_accepts_only_the_complete_sysplorer_default_experiment_tuple(self) -> None:
        source = """model DirectGraph
  import BaseWorkspace.*;
  import SysplorerEmbeddedCoder.Types.*;
  annotation(__MWORKS(version=\"26.3.0\",BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true))), experiment(Algorithm=Euler,Interval=-1));
end DirectGraph;
"""
        native = source.replace(
            "experiment(Algorithm=Euler,Interval=-1)",
            "experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0)",
        ).replace("SampleTime(auto=true)", "SampleTime(auto=true),OutputInterval=0.004")
        changed_stop_time = native.replace("StopTime=0.2", "StopTime=0.3")
        self.assertEqual(direct_graphical_native_text(source), direct_graphical_native_text(native))
        self.assertNotEqual(direct_graphical_native_text(source), direct_graphical_native_text(changed_stop_time))

    def test_execution_guard_restores_only_trailing_whitespace_to_frozen_bytes(self) -> None:
        frozen = b"model NativeWhitespace\n  Real signal;\nend NativeWhitespace;\n"
        native = b"model NativeWhitespace \r\n  Real signal; \r\nend NativeWhitespace;\r\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "NativeWhitespace.mo"
            source.write_bytes(native)
            record: dict[str, object] = {}

            restored = execution.verify_frozen_target_hash(
                record,
                source,
                execution.hashlib.sha256(frozen).hexdigest(),
                "after_simulation",
            )

            self.assertEqual(restored, execution.hashlib.sha256(frozen).hexdigest())
            self.assertEqual(source.read_bytes(), frozen)
            observation = record["target_hash_observations"][0]
            self.assertTrue(observation["native_whitespace_only"])
            self.assertTrue(observation["normalized_source_restored"])

    def test_execution_guard_restores_terminal_newline_omission_to_frozen_bytes(self) -> None:
        frozen = b"model NativeWhitespace\n  Real signal;\nend NativeWhitespace;\n"
        native = b"model NativeWhitespace \r\n  Real signal; \r\nend NativeWhitespace; "
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "NativeWhitespace.mo"
            source.write_bytes(native)
            record: dict[str, object] = {}

            restored = execution.verify_frozen_target_hash(
                record,
                source,
                execution.hashlib.sha256(frozen).hexdigest(),
                "after_session_shutdown",
            )

            self.assertEqual(restored, execution.hashlib.sha256(frozen).hexdigest())
            self.assertEqual(source.read_bytes(), frozen)
            observation = record["target_hash_observations"][0]
            self.assertTrue(observation["native_whitespace_only"])
            self.assertTrue(observation["normalized_source_restored"])

    def test_execution_guard_uses_snapshot_for_frozen_file_without_terminal_newline(self) -> None:
        frozen = b"model NativeWhitespace\n  Real signal;\nend NativeWhitespace;"
        native = b"model NativeWhitespace \r\n  Real signal; \r\nend NativeWhitespace; "
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "NativeWhitespace.mo"
            source.write_bytes(native)
            record: dict[str, object] = {}

            restored = execution.verify_frozen_target_hash(
                record,
                source,
                execution.hashlib.sha256(frozen).hexdigest(),
                "after_session_shutdown",
                frozen_target_bytes=frozen,
                frozen_snapshot_path="raw/frozen_target_source.mo",
            )

            self.assertEqual(restored, execution.hashlib.sha256(frozen).hexdigest())
            self.assertEqual(source.read_bytes(), frozen)
            observation = record["target_hash_observations"][0]
            self.assertTrue(observation["native_whitespace_only"])
            self.assertEqual(observation["frozen_snapshot_sha256"], execution.hashlib.sha256(frozen).hexdigest())
            self.assertEqual(observation["frozen_snapshot_path"], "raw/frozen_target_source.mo")

    def test_before_load_normalization_records_the_restored_frozen_hash(self) -> None:
        frozen = b"model NativeWhitespace\n  Real signal;\nend NativeWhitespace;\n"
        native = b"model NativeWhitespace \n  Real signal; \nend NativeWhitespace;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "NativeWhitespace.mo"
            source.write_bytes(native)
            record: dict[str, object] = {}

            execution.verify_frozen_target_hash(
                record,
                source,
                execution.hashlib.sha256(frozen).hexdigest(),
                "before_load",
            )

            self.assertEqual(record["verified_target_sha256"], execution.hashlib.sha256(frozen).hexdigest())

    def test_execution_guard_rejects_a_non_whitespace_source_change(self) -> None:
        frozen = b"model NativeWhitespace\n  Real signal;\nend NativeWhitespace;\n"
        changed = b"model NativeWhitespace\n  Real changedSignal;\nend NativeWhitespace;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "NativeWhitespace.mo"
            source.write_bytes(changed)

            with self.assertRaisesRegex(RuntimeError, "Source hash changed"):
                execution.verify_frozen_target_hash(
                    {},
                    source,
                    execution.hashlib.sha256(frozen).hexdigest(),
                    "after_simulation",
                )
            self.assertEqual(source.read_bytes(), changed)

    def test_protected_core_guard_restores_only_native_whitespace(self) -> None:
        frozen = b"model ProtectedCore\n  Real signal;\nend ProtectedCore;\n"
        native = b"model ProtectedCore \r\n  Real signal; \r\nend ProtectedCore;\r\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "ProtectedCore.mo"
            source.write_bytes(native)
            binding: dict[str, object] = {
                "path": "Models/ProtectedCore.mo",
                "roles": ["controller_core"],
                "expected_sha256": execution.hashlib.sha256(frozen).hexdigest(),
                "hash_observations": [],
            }

            restored = execution.verify_frozen_protected_source_hash(
                binding,
                source,
                "after_simulation",
                frozen_source_bytes=frozen,
                frozen_snapshot_path="raw/frozen_bound_sources/02_ProtectedCore.mo",
            )

            self.assertEqual(restored, execution.hashlib.sha256(frozen).hexdigest())
            self.assertEqual(source.read_bytes(), frozen)
            observation = binding["hash_observations"][0]
            self.assertTrue(observation["native_whitespace_only"])
            self.assertTrue(observation["matches_frozen_source"])
            self.assertEqual(observation["frozen_snapshot_path"], "raw/frozen_bound_sources/02_ProtectedCore.mo")

    def test_protected_core_guard_rejects_semantic_change(self) -> None:
        frozen = b"model ProtectedCore\n  Real signal;\nend ProtectedCore;\n"
        changed = b"model ProtectedCore\n  Real changedSignal;\nend ProtectedCore;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "ProtectedCore.mo"
            source.write_bytes(changed)
            binding: dict[str, object] = {
                "path": "Models/ProtectedCore.mo",
                "roles": ["controller_core"],
                "expected_sha256": execution.hashlib.sha256(frozen).hexdigest(),
                "hash_observations": [],
            }

            with self.assertRaisesRegex(RuntimeError, "Protected source hash changed"):
                execution.verify_frozen_protected_source_hash(
                    binding,
                    source,
                    "after_simulation",
                    frozen_source_bytes=frozen,
                    frozen_snapshot_path="raw/frozen_bound_sources/02_ProtectedCore.mo",
                )
            self.assertEqual(source.read_bytes(), changed)

    def test_post_shutdown_validation_restores_allowed_native_whitespace(self) -> None:
        frozen = b"model NativeWhitespace\n  Real signal;\nend NativeWhitespace;\n"
        native = b"model NativeWhitespace \r\n  Real signal; \r\nend NativeWhitespace;\r\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "NativeWhitespace.mo"
            cleanup_log = Path(directory) / "session_cleanup.json"
            source.write_bytes(native)
            cleanup_log.write_text("{}", encoding="utf-8")
            record: dict[str, object] = {"scheme_id": "native_whitespace", "status": "passed"}

            outcome = execution.apply_after_session_shutdown_validation(
                record=record,
                model_file=source,
                expected_hash=execution.hashlib.sha256(frozen).hexdigest(),
                cleanup={"requested": True, "verified_closed": True, "finished_at": "2026-07-26T00:00:00+08:00"},
                cleanup_log=cleanup_log,
            )

            self.assertTrue(outcome["integrity_ok"])
            self.assertEqual(record["status"], "passed")
            self.assertEqual(source.read_bytes(), frozen)
            self.assertEqual(record["target_hash_observations"][-1]["phase"], "after_session_shutdown")
            self.assertTrue(record["session_cleanup"]["verified_closed"])

    def test_post_shutdown_validation_marks_semantic_drift_as_source_mismatch(self) -> None:
        frozen = b"model NativeWhitespace\n  Real signal;\nend NativeWhitespace;\n"
        changed = b"model NativeWhitespace\n  Real changedSignal;\nend NativeWhitespace;\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "NativeWhitespace.mo"
            cleanup_log = Path(directory) / "session_cleanup.json"
            source.write_bytes(changed)
            cleanup_log.write_text("{}", encoding="utf-8")
            record: dict[str, object] = {"scheme_id": "semantic_change", "status": "passed"}

            outcome = execution.apply_after_session_shutdown_validation(
                record=record,
                model_file=source,
                expected_hash=execution.hashlib.sha256(frozen).hexdigest(),
                cleanup={"requested": True, "verified_closed": True},
                cleanup_log=cleanup_log,
            )

            self.assertFalse(outcome["integrity_ok"])
            self.assertEqual(outcome["status"], "source_hash_mismatch")
            self.assertEqual(record["status"], "source_hash_mismatch")
            self.assertEqual(source.read_bytes(), changed)


if __name__ == "__main__":
    unittest.main()
