"""从 `api_catalog.json` 生成 Python SDK 的 wrappers 与 manifest。

生成目标：
- `src/python-sdk/wkteam_api_sdk/manifest.py`
- `src/python-sdk/wkteam_api_sdk/generated_api.py`

约束：
- 同输入同输出（稳定生成）
- 不做伪精确类型推断：无法确定的类型使用 Any
"""

from __future__ import annotations

import json
import keyword
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _find_repo_root(start: Path) -> Path:
    """向上查找仓库根目录（以 `docs/specs/engineering-spec/.../api_catalog.json` 为锚点）。"""

    anchor = Path("docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json")
    for p in [start, *start.parents]:
        if (p / anchor).exists():
            return p
    raise RuntimeError(f"无法定位仓库根目录：未找到 {anchor.as_posix()}")


def _normalize_required(value: Any) -> bool:
    v = str(value or "").strip().lower()
    return v in {"是", "y", "yes", "true", "1"}


def _strip_markdown_bold(text: str) -> str:
    m = re.fullmatch(r"\*\*(.+)\*\*", text.strip())
    return m.group(1).strip() if m else text.strip()


def _normalize_param_row(row: dict[str, Any]) -> dict[str, Any]:
    name = row.get("参数名") or row.get("参数") or row.get("字段") or row.get("name")
    required = row.get("必选") or row.get("必填") or row.get("required")
    type_text = row.get("类型") or row.get("数据类型") or row.get("type")
    desc = row.get("说明") or row.get("描述") or row.get("desc")
    return {
        "name": _strip_markdown_bold(str(name or "").strip()),
        "required": _normalize_required(required),
        "type": str(type_text or "").strip(),
        "desc": str(desc or "").strip(),
    }


def _infer_retry_category(entry: dict[str, Any]) -> str:
    title = str(entry.get("title") or "")
    path_text = str(entry.get("path") or "")
    method = str(entry.get("method") or "").upper()
    if method == "GET":
        return "safe"
    if re.match(r"^/(get|query|download|init)", path_text, flags=re.IGNORECASE):
        return "safe"
    if re.search(r"(获取|查询|下载|初始化)", title):
        return "safe"
    return "side_effect"


def _camel_to_snake(text: str) -> str:
    # fooBar -> foo_bar, FooBar -> foo_bar
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.replace("-", "_").replace(" ", "_").lower()


def _safe_identifier(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", name)
    if not cleaned:
        cleaned = "_"
    if re.match(r"^[0-9]", cleaned):
        cleaned = f"_{cleaned}"
    if keyword.iskeyword(cleaned):
        cleaned = f"{cleaned}_"
    return cleaned


def _choose_method_name(entry: dict[str, Any]) -> str:
    p = str(entry.get("path") or "").strip()
    if p:
        segments = [s for s in p.split("/") if s.strip()]
        if segments:
            # 多数 endpoint path 是单段：/addContactLabel
            return _safe_identifier(_camel_to_snake("_".join(segments)))

    module_prefix = str(entry.get("module") or "").replace("-", "_")
    prefix = f"{module_prefix}_" if module_prefix else ""
    op = str(entry.get("operationId") or "")
    rest = op[len(prefix) :] if prefix and op.startswith(prefix) else op
    return _safe_identifier(_camel_to_snake(rest))


def _py_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def _py_literal(value: Any, *, indent: int = 0) -> str:
    pad = " " * indent
    if value is None:
        return "None"
    if value is True:
        return "True"
    if value is False:
        return "False"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return _py_string(value)
    if isinstance(value, list):
        if not value:
            return "[]"
        inner = ",\n".join(f"{' ' * (indent + 2)}{_py_literal(v, indent=indent + 2)}" for v in value)
        return "[\n" + inner + f",\n{pad}]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        # 按 key 排序确保稳定
        items = sorted(value.items(), key=lambda kv: str(kv[0]))
        inner = ",\n".join(
            f"{' ' * (indent + 2)}{_py_string(str(k))}: {_py_literal(v, indent=indent + 2)}"
            for k, v in items
        )
        return "{\n" + inner + f",\n{pad}}}"
    # fallback（尽量不要落到这里）
    return _py_string(str(value))


@dataclass(slots=True)
class EndpointDef:
    operation_id: str
    title: str
    module: str
    method: str
    path: str
    doc: str
    requires_auth: bool
    retry_category: str
    params: list[dict[str, Any]]
    module_attr: str
    method_name: str


def _load_endpoints(catalog_path: Path) -> list[EndpointDef]:
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog = raw.get("catalog") or []
    endpoints = [e for e in catalog if e.get("kind") == "endpoint"]
    endpoints.sort(key=lambda e: (str(e.get("module") or ""), str(e.get("operationId") or "")))

    out: list[EndpointDef] = []
    for e in endpoints:
        headers = e.get("headers")
        if isinstance(headers, list):
            requires_auth = any(str(h.get("name") or "").lower() == "authorization" for h in headers)
        else:
            # 离线文档大多数接口需要鉴权；对于无法判定的情况默认 true
            requires_auth = True

        params_raw = e.get("params")
        params = [_normalize_param_row(r) for r in params_raw] if isinstance(params_raw, list) else []
        params = [p for p in params if p.get("name")]

        module = str(e.get("module") or "")
        module_attr = _safe_identifier(module.replace("-", "_"))
        method_name = _choose_method_name(e)

        out.append(
            EndpointDef(
                operation_id=str(e.get("operationId") or ""),
                title=str(e.get("title") or ""),
                module=module,
                method=str(e.get("method") or "POST").upper(),
                path=str(e.get("path") or ""),
                doc=str(e.get("doc") or ""),
                requires_auth=requires_auth,
                retry_category=_infer_retry_category(e),
                params=params,
                module_attr=module_attr,
                method_name=method_name,
            )
        )

    # collision handling：同一 module_attr 下 method_name 必须唯一
    grouped: dict[str, list[EndpointDef]] = {}
    for e in out:
        grouped.setdefault(e.module_attr, []).append(e)

    for group in grouped.values():
        counts: dict[str, int] = {}
        for e in group:
            counts[e.method_name] = counts.get(e.method_name, 0) + 1

        # 如果冲突：优先改为 operationId 去掉 module 前缀后的 snake 形式
        for e in group:
            if counts.get(e.method_name, 0) <= 1:
                continue
            module_prefix = e.module.replace("-", "_")
            prefix = f"{module_prefix}_" if module_prefix else ""
            rest = e.operation_id[len(prefix) :] if prefix and e.operation_id.startswith(prefix) else e.operation_id
            e.method_name = _safe_identifier(_camel_to_snake(rest))

        # 再次保证唯一：如仍冲突则追加序号
        seen: dict[str, int] = {}
        for e in group:
            base = e.method_name
            seen[base] = seen.get(base, 0) + 1
            if seen[base] > 1:
                e.method_name = f"{base}_{seen[base]}"

    return out


def _map_doc_type_to_py(type_text: str) -> str:
    t = (type_text or "").strip().lower()
    if not t:
        return "Any"
    if "string" in t:
        return "str"
    if any(x in t for x in ["int", "integer", "long", "double", "float", "number"]):
        return "float"
    if any(x in t for x in ["boolean", "bool"]):
        return "bool"
    if any(x in t for x in ["array", "list", "jsonarray"]):
        return "list[Any]"
    if any(x in t for x in ["object", "jsonobject", "map"]):
        return "dict[str, Any]"
    return "Any"


def _render_manifest(endpoints: list[EndpointDef]) -> str:
    endpoint_defs = [
        {
            "operation_id": e.operation_id,
            "title": e.title,
            "module": e.module,
            "module_attr": e.module_attr,
            "method_name": e.method_name,
            "method": e.method,
            "path": e.path,
            "doc": e.doc,
            "requires_auth": e.requires_auth,
            "retry_category": e.retry_category,
            "params": e.params,
        }
        for e in endpoints
    ]
    operation_ids = [e.operation_id for e in endpoints]

    return "\n".join(
        [
            "# ruff: noqa",
            "# @generated by src/python-sdk/tools/generate_sdk.py - DO NOT EDIT",
            "",
            "from __future__ import annotations",
            "",
            "from typing import Literal, TypedDict",
            "",
            "RetryCategory = Literal[\"safe\", \"side_effect\"]",
            "",
            "class ParamDef(TypedDict):",
            "    name: str",
            "    required: bool",
            "    type: str",
            "    desc: str",
            "",
            "class EndpointDef(TypedDict):",
            "    operation_id: str",
            "    title: str",
            "    module: str",
            "    module_attr: str",
            "    method_name: str",
            "    method: str",
            "    path: str",
            "    doc: str",
            "    requires_auth: bool",
            "    retry_category: RetryCategory",
            "    params: list[ParamDef]",
            "",
            f"endpoint_defs: list[EndpointDef] = {_py_literal(endpoint_defs, indent=0)}",
            "",
            f"operation_ids: list[str] = {_py_literal(operation_ids, indent=0)}",
            "",
            "endpoint_by_operation_id: dict[str, EndpointDef] = {d[\"operation_id\"]: d for d in endpoint_defs}",
            "",
            "__all__ = [\"RetryCategory\", \"ParamDef\", \"EndpointDef\", \"endpoint_defs\", \"operation_ids\", \"endpoint_by_operation_id\"]",
            "",
        ]
    )


def _render_generated_api(endpoints: list[EndpointDef]) -> str:
    modules: dict[str, list[EndpointDef]] = {}
    for e in endpoints:
        modules.setdefault(e.module_attr, []).append(e)

    module_attrs = sorted(modules.keys())

    def render_method_sync(e: EndpointDef) -> str:
        params = e.params
        valid_name = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        keyword_set = set(keyword.kwlist)

        required = []
        optional = []
        invalid = []
        for p in params:
            n = str(p.get("name") or "").strip()
            if not n:
                continue
            if not valid_name.match(n) or n in keyword_set:
                invalid.append(n)
                continue
            if p.get("required"):
                required.append(p)
            else:
                optional.append(p)

        lines: list[str] = []
        lines.append(f"    def {e.method_name}(")
        lines.append("        self,")
        lines.append("        *,")
        for p in required:
            py_t = _map_doc_type_to_py(str(p.get("type") or ""))
            lines.append(f"        {p['name']}: {py_t},")
        for p in optional:
            py_t = _map_doc_type_to_py(str(p.get("type") or ""))
            lines.append(f"        {p['name']}: {py_t} | None = None,")
        lines.append("        request_options: RequestOptions | None = None,")
        lines.append("        **extra: Any,")
        lines.append("    ) -> Any:")
        # docstring
        lines.append('        """')
        lines.append(f"        {e.title}")
        lines.append("")
        lines.append(f"        - operationId: {e.operation_id}")
        lines.append(f"        - method: {e.method} {e.path}")
        lines.append(f"        - doc: {e.doc}")
        if invalid:
            lines.append("")
            lines.append("        说明：以下参数名在离线文档中不是合法 Python 标识符，需通过 `**{...}` 方式传入：")
            for n in invalid:
                lines.append(f"        - {n}")
        lines.append('        """')
        # build params dict
        lines.append("        params: dict[str, Any] = {}")
        for p in required:
            lines.append(f"        params[{_py_string(p['name'])}] = {p['name']}")
        for p in optional:
            lines.append(f"        if {p['name']} is not None:")
            lines.append(f"            params[{_py_string(p['name'])}] = {p['name']}")
        lines.append("        if extra:")
        lines.append("            params.update(extra)")
        lines.append("        return self._client.call(")
        lines.append(f"            operation_id={_py_string(e.operation_id)},")
        lines.append(f"            method={_py_string(e.method)},")
        lines.append(f"            path={_py_string(e.path)},")
        lines.append(f"            requires_auth={_py_literal(e.requires_auth)},")
        lines.append(f"            retry_category={_py_string(e.retry_category)},")
        lines.append("            params=params,")
        lines.append("            request_options=request_options,")
        lines.append("        )")
        return "\n".join(lines)

    def render_method_async(e: EndpointDef) -> str:
        params = e.params
        valid_name = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        keyword_set = set(keyword.kwlist)

        required = []
        optional = []
        invalid = []
        for p in params:
            n = str(p.get("name") or "").strip()
            if not n:
                continue
            if not valid_name.match(n) or n in keyword_set:
                invalid.append(n)
                continue
            if p.get("required"):
                required.append(p)
            else:
                optional.append(p)

        lines: list[str] = []
        lines.append(f"    async def {e.method_name}(")
        lines.append("        self,")
        lines.append("        *,")
        for p in required:
            py_t = _map_doc_type_to_py(str(p.get("type") or ""))
            lines.append(f"        {p['name']}: {py_t},")
        for p in optional:
            py_t = _map_doc_type_to_py(str(p.get("type") or ""))
            lines.append(f"        {p['name']}: {py_t} | None = None,")
        lines.append("        request_options: RequestOptions | None = None,")
        lines.append("        **extra: Any,")
        lines.append("    ) -> Any:")
        lines.append('        """')
        lines.append(f"        {e.title}")
        lines.append("")
        lines.append(f"        - operationId: {e.operation_id}")
        lines.append(f"        - method: {e.method} {e.path}")
        lines.append(f"        - doc: {e.doc}")
        if invalid:
            lines.append("")
            lines.append("        说明：以下参数名在离线文档中不是合法 Python 标识符，需通过 `**{...}` 方式传入：")
            for n in invalid:
                lines.append(f"        - {n}")
        lines.append('        """')
        lines.append("        params: dict[str, Any] = {}")
        for p in required:
            lines.append(f"        params[{_py_string(p['name'])}] = {p['name']}")
        for p in optional:
            lines.append(f"        if {p['name']} is not None:")
            lines.append(f"            params[{_py_string(p['name'])}] = {p['name']}")
        lines.append("        if extra:")
        lines.append("            params.update(extra)")
        lines.append("        return await self._client.call(")
        lines.append(f"            operation_id={_py_string(e.operation_id)},")
        lines.append(f"            method={_py_string(e.method)},")
        lines.append(f"            path={_py_string(e.path)},")
        lines.append(f"            requires_auth={_py_literal(e.requires_auth)},")
        lines.append(f"            retry_category={_py_string(e.retry_category)},")
        lines.append("            params=params,")
        lines.append("            request_options=request_options,")
        lines.append("        )")
        return "\n".join(lines)

    blocks: list[str] = []
    blocks.extend(
        [
            "# ruff: noqa",
            "# @generated by src/python-sdk/tools/generate_sdk.py - DO NOT EDIT",
            "",
            "from __future__ import annotations",
            "",
            "from dataclasses import dataclass",
            "from typing import Any",
            "",
            "from .core_client import AsyncWkteamCoreClient, RequestOptions, WkteamCoreClient",
            "",
        ]
    )

    # Root objects
    blocks.append("@dataclass(slots=True)")
    blocks.append("class WkteamApi:")
    blocks.append('    """同步 API 树：client.api.<module>.<method>(...)"""')
    blocks.append("")
    for m in module_attrs:
        class_name = "".join(p.capitalize() for p in m.split("_")) + "Api"
        blocks.append(f"    {m}: \"{class_name}\"")
    blocks.append("")
    blocks.append("    def __init__(self, client: WkteamCoreClient) -> None:")
    for m in module_attrs:
        class_name = "".join(p.capitalize() for p in m.split("_")) + "Api"
        blocks.append(f"        self.{m} = {class_name}(client)")
    blocks.append("")

    blocks.append("@dataclass(slots=True)")
    blocks.append("class AsyncWkteamApi:")
    blocks.append('    """异步 API 树：await client.api.<module>.<method>(...)"""')
    blocks.append("")
    for m in module_attrs:
        class_name = "Async" + "".join(p.capitalize() for p in m.split("_")) + "Api"
        blocks.append(f"    {m}: \"{class_name}\"")
    blocks.append("")
    blocks.append("    def __init__(self, client: AsyncWkteamCoreClient) -> None:")
    for m in module_attrs:
        class_name = "Async" + "".join(p.capitalize() for p in m.split("_")) + "Api"
        blocks.append(f"        self.{m} = {class_name}(client)")
    blocks.append("")

    # Module classes
    for m in module_attrs:
        class_name = "".join(p.capitalize() for p in m.split("_")) + "Api"
        blocks.append("@dataclass(slots=True)")
        blocks.append(f"class {class_name}:")
        blocks.append(f'    """模块：{m}"""')
        blocks.append("")
        blocks.append("    _client: WkteamCoreClient")
        blocks.append("")
        blocks.append("    def __init__(self, client: WkteamCoreClient) -> None:")
        blocks.append("        self._client = client")
        blocks.append("")
        for e in modules[m]:
            blocks.append(render_method_sync(e))
            blocks.append("")

        async_class_name = "Async" + class_name
        blocks.append("@dataclass(slots=True)")
        blocks.append(f"class {async_class_name}:")
        blocks.append(f'    """模块（async）：{m}"""')
        blocks.append("")
        blocks.append("    _client: AsyncWkteamCoreClient")
        blocks.append("")
        blocks.append("    def __init__(self, client: AsyncWkteamCoreClient) -> None:")
        blocks.append("        self._client = client")
        blocks.append("")
        for e in modules[m]:
            blocks.append(render_method_async(e))
            blocks.append("")

    blocks.append("__all__ = [\"WkteamApi\", \"AsyncWkteamApi\"]")
    blocks.append("")
    return "\n".join(blocks)


def _render_operation_index(endpoints: list[EndpointDef]) -> str:
    index: dict[str, dict[str, Any]] = {}
    for e in endpoints:
        index[e.operation_id] = {
            "operation_id": e.operation_id,
            "title": e.title,
            "module": e.module,
            "module_attr": e.module_attr,
            "method_name": e.method_name,
            "method": e.method,
            "path": e.path,
            "doc": e.doc,
            "requires_auth": e.requires_auth,
            "retry_category": e.retry_category,
        }
    # stable output：按 key 排序
    ordered = {k: index[k] for k in sorted(index.keys())}

    return "\n".join(
        [
            "# ruff: noqa",
            "# @generated by src/python-sdk/tools/generate_sdk.py - DO NOT EDIT",
            "",
            "from __future__ import annotations",
            "",
            "from typing import Literal, TypedDict",
            "",
            "RetryCategory = Literal[\"safe\", \"side_effect\"]",
            "",
            "class OperationIndexEntry(TypedDict):",
            "    operation_id: str",
            "    title: str",
            "    module: str",
            "    module_attr: str",
            "    method_name: str",
            "    method: str",
            "    path: str",
            "    doc: str",
            "    requires_auth: bool",
            "    retry_category: RetryCategory",
            "",
            f"operation_index: dict[str, OperationIndexEntry] = {_py_literal(ordered, indent=0)}",
            "",
            "__all__ = [\"RetryCategory\", \"OperationIndexEntry\", \"operation_index\"]",
            "",
        ]
    )


def main() -> None:
    script_path = Path(__file__).resolve()
    repo_root = _find_repo_root(script_path)
    catalog_path = repo_root / "docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json"
    endpoints = _load_endpoints(catalog_path)

    out_manifest = repo_root / "src/python-sdk/wkteam_api_sdk/manifest.py"
    out_api = repo_root / "src/python-sdk/wkteam_api_sdk/generated_api.py"
    out_op_index = repo_root / "src/python-sdk/wkteam_api_sdk/operation_index.py"

    out_manifest.parent.mkdir(parents=True, exist_ok=True)

    out_manifest.write_text(_render_manifest(endpoints), encoding="utf-8")
    out_api.write_text(_render_generated_api(endpoints), encoding="utf-8")
    out_op_index.write_text(_render_operation_index(endpoints), encoding="utf-8")

    print(f"generated: {out_manifest.relative_to(repo_root)}")
    print(f"generated: {out_api.relative_to(repo_root)}")
    print(f"generated: {out_op_index.relative_to(repo_root)}")
    print(f"endpoints: {len(endpoints)}")


if __name__ == "__main__":
    main()
