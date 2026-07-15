from Scripts.quality.check_frontend_handoff_contract import validate


def test_frontend_handoff_contract() -> None:
    assert validate() == []
