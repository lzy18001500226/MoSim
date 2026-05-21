from __future__ import annotations

import json
from pathlib import Path

from wkteam_api_sdk.manifest import operation_ids


def _repo_root() -> Path:
    anchor = Path("docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json")
    for p in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (p / anchor).exists():
            return p
    raise RuntimeError("无法定位仓库根目录：未找到 api_catalog.json（anchor）")


def test_every_catalog_operation_id_has_wrapper() -> None:
    """AT-008：不漏接口（覆盖性核验）。

    断言：catalog(kind='endpoint') 的 operationId 集合 == Python SDK manifest.operation_ids 集合。
    """

    catalog_path = _repo_root() / "docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json"
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog = raw.get("catalog") or []
    catalog_ops = {e["operationId"] for e in catalog if e.get("kind") == "endpoint"}

    sdk_ops = set(operation_ids)

    missing = sorted(catalog_ops - sdk_ops)
    extra = sorted(sdk_ops - catalog_ops)

    assert not missing, f"SDK 漏实现 operationId：{missing[:20]} (total={len(missing)})"
    assert not extra, f"SDK 多出 operationId（可能生成器漂移）：{extra[:20]} (total={len(extra)})"
