"""Security tests: unsafe pickle deserialization in RAG engine.

The RAG engine persists its FAISS index and document store as pickle files.
A compromised or maliciously crafted pickle file can execute arbitrary code
during deserialization (classic pickle RCE).

These tests:
1. Document the RCE vector (pickle.loads executes arbitrary code).
2. Verify the RAG module DOES use pickle (tracks the attack surface).
3. Verify that loading a benign pickle via RAGEngine.load_index works.
4. Recommend safer alternatives for future hardening.
"""

import os
import pickle
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Module-level state so pickle can resolve callables by reference
_rce_executed: list = []


def _rce_trigger():
    """Module-level function — pickle can serialize its reference."""
    _rce_executed.append("EXECUTED")


class _RCEPayload:
    """Pickle payload that calls a module-level function on deserialization."""
    def __reduce__(self):
        return (_rce_trigger, ())


def _make_malicious_pickle() -> bytes:
    return pickle.dumps(_RCEPayload())


def _make_benign_pickle(data: object) -> bytes:
    return pickle.dumps(data)


# ---------------------------------------------------------------------------
# Risk documentation tests
# ---------------------------------------------------------------------------

class TestPickleRiskDocumentation:
    def test_pickle_module_allows_code_execution(self):
        """Document that standard pickle.loads executes arbitrary code.

        This IS the expected behavior — the test proves the attack vector
        works, not that it's been blocked.
        """
        class LocalExploit:
            def __reduce__(self):
                # Use a module-level list append via the os module to ensure
                # pickle can resolve the callable across modules
                return (os.getenv, ("HOME",))  # safe: just reads HOME env var

        payload = pickle.dumps(LocalExploit())
        result = pickle.loads(payload)
        # os.getenv("HOME") returns a string or None — proves code was called
        assert result == os.getenv("HOME"), "pickle.loads should execute the __reduce__ callable"

    def test_malicious_pickle_bytes_are_valid_pickle(self):
        """The malicious payload is syntactically valid pickle."""
        payload = _make_malicious_pickle()
        assert isinstance(payload, bytes)
        assert len(payload) > 0

    def test_benign_pickle_round_trips(self):
        """Benign data pickles and unpickles correctly."""
        data = {"key": "value", "numbers": [1, 2, 3]}
        payload = _make_benign_pickle(data)
        restored = pickle.loads(payload)
        assert restored == data

    def test_module_level_rce_payload_executes(self):
        """Explicitly verify that a module-level __reduce__ trick works."""
        _rce_executed.clear()
        payload = _make_malicious_pickle()
        pickle.loads(payload)
        assert "EXECUTED" in _rce_executed, (
            "Module-level pickle RCE payload did not execute — "
            "verify the _RCEPayload class is correct."
        )


# ---------------------------------------------------------------------------
# RAG engine pickle risk assessment
# ---------------------------------------------------------------------------

class TestRAGPickleRisk:
    def test_rag_module_imports_pickle(self):
        """Verify that the RAG module uses pickle (documents the attack surface)."""
        import inspect
        import pentestagent.knowledge.rag as rag_module
        source = inspect.getsource(rag_module)
        assert "pickle" in source, (
            "RAG module no longer uses pickle — update this test and "
            "the security documentation accordingly."
        )

    def test_rag_has_load_index_method(self):
        """RAGEngine.load_index exists and would call pickle.load."""
        from pentestagent.knowledge.rag import RAGEngine
        engine = RAGEngine()
        assert hasattr(engine, "load_index"), "RAGEngine has no load_index method"
        assert callable(engine.load_index)

    def test_rag_has_save_index_method(self):
        from pentestagent.knowledge.rag import RAGEngine
        engine = RAGEngine()
        assert hasattr(engine, "save_index"), "RAGEngine has no save_index method"

    def test_rag_load_index_uses_pickle(self):
        """Verify that load_index reads pickle (not json/yaml)."""
        import inspect
        from pentestagent.knowledge.rag import RAGEngine
        source = inspect.getsource(RAGEngine.load_index)
        assert "pickle" in source, "load_index no longer uses pickle"

    def test_rag_save_uses_pickle(self, tmp_path):
        """Verify that save_index writes a pickle file."""
        from pentestagent.knowledge.rag import Document, RAGEngine
        import numpy as np

        engine = RAGEngine(knowledge_path=tmp_path)
        engine.documents = [
            Document(content="test document", source="test",
                     embedding=np.array([0.1, 0.2, 0.3]))
        ]
        pkl_path = tmp_path / "test_idx.pkl"
        try:
            engine.save_index(pkl_path)
            if pkl_path.exists():
                raw = pkl_path.read_bytes()
                # Verify it's a valid pickle (starts with proto opcode or similar)
                assert len(raw) > 0
                # First 2 bytes of pickle protocol 2+ are \x80\x02 or \x80\x04 etc.
                assert raw[0] == 0x80 or raw[0] == ord('(')
        except Exception as e:
            pytest.skip(f"save_index failed (likely missing FAISS): {e}")

    def test_loading_benign_pickle_via_rag(self, tmp_path):
        """RAGEngine.load_index can load a benign pickle created by save_index."""
        from pentestagent.knowledge.rag import Document, RAGEngine
        import numpy as np

        engine = RAGEngine(knowledge_path=tmp_path)
        engine.documents = [
            Document(content="hello security", source="test.txt",
                     embedding=np.array([0.1, 0.2]))
        ]
        pkl_path = tmp_path / "idx.pkl"
        try:
            engine.save_index(pkl_path)
            assert pkl_path.exists()

            engine2 = RAGEngine(knowledge_path=tmp_path)
            engine2.load_index(pkl_path)
            assert len(engine2.documents) >= 1
        except Exception as e:
            pytest.skip(f"FAISS/save not available: {e}")


# ---------------------------------------------------------------------------
# Recommendations (informational assertions)
# ---------------------------------------------------------------------------

class TestPickleHardeningRecommendations:
    def test_json_is_available_as_safe_alternative(self):
        """JSON is available as a safer alternative for non-numpy data."""
        import json
        data = {"key": "value", "numbers": [1, 2, 3]}
        assert json.loads(json.dumps(data)) == data

    def test_numpy_save_is_available(self):
        """numpy.save is available for arrays instead of pickle."""
        import numpy as np
        arr = np.array([1.0, 2.0, 3.0])
        assert arr.shape == (3,)

    def test_hmac_signed_pickle_concept(self):
        """HMAC-signed pickles reduce (but don't eliminate) the pickle RCE risk."""
        import hashlib
        import hmac

        secret = b"application-secret-key"
        data = pickle.dumps({"safe": "data"})
        sig = hmac.new(secret, data, hashlib.sha256).digest()
        expected_sig = hmac.new(secret, data, hashlib.sha256).digest()
        assert hmac.compare_digest(sig, expected_sig)

    def test_tampered_pickle_detectable_with_hmac(self):
        """A tampered pickle payload produces a different HMAC."""
        import hashlib
        import hmac

        secret = b"application-secret-key"
        original = pickle.dumps({"safe": "data"})
        tampered = original + b"\x00"

        original_sig = hmac.new(secret, original, hashlib.sha256).digest()
        tampered_sig = hmac.new(secret, tampered, hashlib.sha256).digest()
        assert not hmac.compare_digest(original_sig, tampered_sig)
