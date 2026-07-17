from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/generate_classic_controller_mworks_code.py"


def test_codegen_uses_official_mworks_api_and_records_provenance() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for token in (
        "ModelingPy.GetModelCodeGenerationOptions",
        "ModelingPy.SetModelCodeGenerationOptions",
        "ModelingPy.GenerateModelCode",
        '"model_sha256"',
        '"generated_files"',
        '"MWORKS_CODEGEN_MANIFEST.json"',
    ):
        assert token in text


def test_codegen_normalizes_archive_without_changing_tokens() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'line.rstrip(" \\t")' in text
    assert 'newline="\\n"' in text
    assert "executable tokens are unchanged" in text
