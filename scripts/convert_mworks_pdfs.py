#!/usr/bin/env python3
"""Convert high-value MWORKS PDF documents into Markdown for agent lookup.

Two conversion paths are supported:

1. `--method pymupdf`: local text fallback, fast and offline.
2. `--method mineru`: one-by-one MinerU precise API upload, better for tables,
   formulas, layout, and scanned pages. The token must be provided through the
   `MINERU_API_TOKEN` environment variable.

Usage:
    uv run --with pymupdf python scripts/convert_mworks_pdfs.py --method pymupdf
    uv run --with pymupdf python scripts/convert_mworks_pdfs.py --method mineru --limit 3
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib import request, error
from zipfile import ZipFile
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import time

import fitz  # type: ignore[import-not-found]


SOURCE_ROOT = Path("MWORKS高校星火计划资料包")
OUTPUT_ROOT = Path("docs/mworks/converted")
TMP_ROOT = Path("docs/mworks/tmp/mineru")
MINERU_BASE_URL = "https://mineru.net/api/v4"


@dataclass(frozen=True)
class PdfTarget:
    topic: str
    output_name: str
    source: str
    priority: str
    note: str


TARGETS = [
    PdfTarget(
        "sysplorer",
        "Syslab与Sysplorer双向集成_2024a.md",
        "培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/07-MWORKS.Syslab和MWORKS.Sysplorer双向集成(2024a)/01-MWORKS.Syslab和MWORKS.Sysplorer双向集成.pdf",
        "P0",
        "Syslab/Sysplorer 双向数据、仿真与 API 集成流程。",
    ),
    PdfTarget(
        "sysplorer",
        "Syslab与Sysplorer双向集成_2025b.md",
        "培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/08-MWORKS.Syslab与MWORKS.Sysplorer双向集成(2025b)/Syslab与Sysplorer双向集成.pdf",
        "P0",
        "较新版本的 Syslab/Sysplorer 集成材料。",
    ),
    PdfTarget(
        "sysplorer",
        "Modelica语法详解_模型行为描述.md",
        "培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/05-Modelica语法详解/04-Modelica语法详解-模型行为描述.pdf",
        "P0",
        "Modelica 方程、算法、事件等模型行为表达。",
    ),
    PdfTarget(
        "sysplorer",
        "Modelica语法详解_模型重用.md",
        "培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/05-Modelica语法详解/09-Modelica语法详解-模型重用.pdf",
        "P0",
        "继承、替换、参数化和可复用模型结构。",
    ),
    PdfTarget(
        "syslab",
        "MWORKS.Syslab控制系统工具箱.md",
        "培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/01-控制系统工具箱应用/01-2024a/MWORKS.Syslab控制系统工具箱.pdf",
        "P1",
        "控制系统建模、时域/频域分析、PID 与状态反馈。",
    ),
    PdfTarget(
        "syslab",
        "MWORKS.Syslab控制系统工具箱APP.md",
        "培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/02-控制系统设计与分析APP/01-2024a/MWORKS.Syslab控制系统工具箱APP(应用程序).pdf",
        "P1",
        "控制系统设计与分析 APP 操作流程。",
    ),
    PdfTarget(
        "optimization",
        "MWORKS.Sysplorer参数估计工具箱应用.md",
        "培训课程配套材料/01-官网课程配套材料/05-基于模型的设计优化/02-参数估计工具箱应用/01-2023b/MWORKS.Sysplorer参数估计工具箱应用.pdf",
        "P1",
        "模型参数估计、仿真对齐和优化流程。",
    ),
    PdfTarget(
        "control",
        "Syslab系统辨识工具箱.md",
        "培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/03-控制系统之系统辨识工具箱/01-2024b/Syslab控制系统之系统辨识工具箱.pdf",
        "P1",
        "辨识流程，可用于模型不确定性和控制器整定支撑。",
    ),
    PdfTarget(
        "control",
        "Syslab鲁棒控制工具箱.md",
        "培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/04-鲁棒控制工具箱应用/01-2024b/Syslab控制系统之鲁棒控制工具箱.pdf",
        "P1",
        "鲁棒控制分析和设计方法。",
    ),
    PdfTarget(
        "api",
        "MWORKS.Sysplorer外部接口_外部函数.md",
        "培训课程配套材料/01-官网课程配套材料/03-扩展接口调用/02-MWORKS.Sysplorer外部接口-外部函数(C、C++、Fortran)/01-2023b/MWORKS.Sysplorer外部接口-外部函数(C、C++、Fortran).pdf",
        "P2",
        "外部函数接口，后续联动 C/C++ 或外部算法时参考。",
    ),
    PdfTarget(
        "api",
        "MWORKS.Sysplorer工具箱运行脚本_Python.md",
        "培训课程配套材料/01-官网课程配套材料/03-扩展接口调用/03-MWORKS.Sysplorer工具箱运行脚本（Python）/01-2024a/MWORKS.Sysplorer工具箱运行脚本（Python）.pdf",
        "P2",
        "Sysplorer Python 脚本运行和自动化接口。",
    ),
    PdfTarget(
        "api",
        "MWORKS.Syslab外部函数调用.md",
        "培训课程配套材料/01-官网课程配套材料/03-扩展接口调用/01-MWORKS.Syslab外部函数调用/01-2023a/MWORKS.Syslab外部函数调用.pdf",
        "P2",
        "Syslab 调用 Python/C/外部函数的参考。",
    ),
    PdfTarget(
        "challenge",
        "智能无人系统应用挑战赛_无人车避障竞赛规则.md",
        "培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/01-第一期/无人车避障3.0竞赛规则.pdf",
        "P1",
        "挑战赛规则和评价方式参考。",
    ),
    PdfTarget(
        "challenge",
        "智能无人系统应用挑战赛_专项培训一.md",
        "培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/01-第一期/智能无人系统应用挑战赛-无人车避障赛道专项培训（一）.pdf",
        "P1",
        "智能无人系统场景、模型和控制展示参考。",
    ),
    PdfTarget(
        "challenge",
        "智能无人系统应用挑战赛_专项培训二.md",
        "培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/02-第二期/无人车避障赛道专项培训（二）.pdf",
        "P1",
        "路径规划、避障和展示流程参考。",
    ),
]


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def extract_pdf(path: Path) -> tuple[int, str]:
    doc = fitz.open(path)
    pages: list[str] = []
    for index, page in enumerate(doc, start=1):
        text = clean_text(page.get_text("text"))
        if text:
            pages.append(f"## Page {index}\n\n```text\n{text}\n```")
        else:
            pages.append(f"## Page {index}\n\n> No extractable text found on this page.")
    return doc.page_count, "\n\n".join(pages)


def safe_stem(text: str) -> str:
    stem = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", text, flags=re.UNICODE).strip("_")
    return stem[:120] or "document"


def request_json(url: str, *, token: str, method: str = "GET", data: dict | None = None, timeout: int = 60) -> dict:
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = request.Request(url, data=body, method=method)
    req.add_header("Accept", "*/*")
    req.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from MinerU: {detail}") from exc
    return json.loads(payload)


def upload_file(upload_url: str, source: Path, timeout: int = 300) -> None:
    failures: list[str] = []
    try:
        import requests  # type: ignore[import-not-found]

        for attempt in range(1, 4):
            try:
                with source.open("rb") as f:
                    resp = requests.put(upload_url, data=f, timeout=timeout)
                if resp.status_code == 200:
                    return
                failures.append(f"requests attempt {attempt}: HTTP {resp.status_code}: {resp.text[:400]}")
            except Exception as exc:
                failures.append(f"requests attempt {attempt}: {exc}")
            time.sleep(min(2 * attempt, 6))
    except Exception as exc:
        failures.append(f"requests unavailable: {exc}")

    powershell = shutil.which("powershell.exe")
    source_win = to_windows_path(source) if powershell else None
    if powershell and source_win:
        command = (
            "$ErrorActionPreference='Stop'; & curl.exe --fail --silent --show-error "
            "--retry 3 --retry-delay 2 -X PUT -T "
            f"{powershell_single_quote(source_win)} {powershell_single_quote(upload_url)}"
        )
        result = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-Command",
                command,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0:
            return
        failures.append(f"windows curl fallback: {result.stderr.strip() or result.stdout.strip() or result.returncode}")

    for attempt in range(1, 4):
        req = request.Request(upload_url, data=source.read_bytes(), method="PUT")
        try:
            with request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    return
                failures.append(f"urllib attempt {attempt}: HTTP {resp.status}")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            failures.append(f"urllib attempt {attempt}: HTTP {exc.code}: {detail}")
        except Exception as exc:
            failures.append(f"urllib attempt {attempt}: {exc}")
        time.sleep(min(2 * attempt, 6))

    curl = shutil.which("curl")
    if curl:
        result = subprocess.run(
            [curl, "--fail", "--silent", "--show-error", "--retry", "3", "--retry-delay", "2", "-X", "PUT", "-T", str(source), upload_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0:
            return
        failures.append(f"curl fallback: {result.stderr.strip() or result.stdout.strip() or result.returncode}")

    raise RuntimeError("MinerU upload failed; " + " | ".join(failures))


def to_windows_path(path: Path) -> str | None:
    wslpath = shutil.which("wslpath")
    if not wslpath:
        return None
    result = subprocess.run(
        [wslpath, "-w", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def powershell_single_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def download_file(url: str, output: Path, timeout: int = 300) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    for attempt in range(1, 4):
        try:
            with request.urlopen(url, timeout=timeout) as resp:
                output.write_bytes(resp.read())
                return
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            failures.append(f"urllib attempt {attempt}: HTTP {exc.code}: {detail}")
        except Exception as exc:
            failures.append(f"urllib attempt {attempt}: {exc}")
        time.sleep(min(2 * attempt, 6))

    curl = shutil.which("curl")
    if curl:
        result = subprocess.run(
            [curl, "--fail", "--silent", "--show-error", "--location", "--retry", "3", "--retry-delay", "2", "-o", str(output), url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0 and output.exists() and output.stat().st_size > 0:
            return
        failures.append(f"curl fallback: {result.stderr.strip() or result.stdout.strip() or result.returncode}")

    powershell = shutil.which("powershell.exe")
    output_win = to_windows_path(output) if powershell else None
    if powershell and output_win:
        command = (
            "$ErrorActionPreference='Stop'; Invoke-WebRequest -Uri "
            f"{powershell_single_quote(url)} -OutFile {powershell_single_quote(output_win)}"
        )
        result = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-Command",
                command,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0 and output.exists() and output.stat().st_size > 0:
            return
        failures.append(f"powershell fallback: {result.stderr.strip() or result.stdout.strip() or result.returncode}")

    raise RuntimeError("MinerU result download failed; " + " | ".join(failures))


def write_mineru_result_log(target: PdfTarget, batch_id: str, data_id: str, result_item: dict) -> Path:
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    log_path = TMP_ROOT / "last_result.json"
    payload = {
        "source": target.source,
        "output_name": target.output_name,
        "batch_id": batch_id,
        "data_id": data_id,
        "state": result_item.get("state"),
        "full_zip_url": result_item.get("full_zip_url"),
        "err_msg": result_item.get("err_msg", ""),
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return log_path


def find_full_markdown(extract_dir: Path) -> Path | None:
    candidates = sorted(extract_dir.rglob("full.md"))
    if candidates:
        return candidates[0]
    candidates = sorted(extract_dir.rglob("*.md"))
    return candidates[0] if candidates else None


def promote_mineru_markdown(
    target: PdfTarget,
    *,
    source: Path,
    extract_dir: Path,
    batch_id: str,
) -> dict[str, str]:
    output = OUTPUT_ROOT / target.topic / target.output_name
    output.parent.mkdir(parents=True, exist_ok=True)
    full_md = find_full_markdown(extract_dir)
    if full_md is None:
        raise RuntimeError(f"MinerU result has no Markdown file for {source.name}")

    image_source = full_md.parent / "images"
    image_dir_name = f"{output.stem}_images"
    image_output = output.parent / image_dir_name
    body = full_md.read_text(encoding="utf-8", errors="replace").strip()
    if image_source.exists():
        if image_output.exists():
            shutil.rmtree(image_output)
        shutil.copytree(image_source, image_output)
        body = body.replace("](images/", f"]({image_dir_name}/")
        body = body.replace('src="images/', f'src="{image_dir_name}/')
        body = body.replace("src='images/", f"src='{image_dir_name}/")

    digest = hashlib.sha1(source.read_bytes()).hexdigest()[:12]
    title = target.output_name.removesuffix(".md")
    image_count = len(list(image_output.glob("*"))) if image_output.exists() else 0
    output.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"- Source: `{source.as_posix()}`",
                "- Converted by: `MinerU precise API`",
                f"- Conversion date: `{date.today().isoformat()}`",
                "- Review status: `MinerU converted; spot check recommended`",
                f"- Priority: `{target.priority}`",
                f"- Source SHA1: `{digest}`",
                f"- MinerU batch id: `{batch_id}`",
                f"- Images: `{image_count}`",
                f"- Notes: {target.note}",
                "",
                body,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "source": target.source,
        "output": output.as_posix(),
        "status": "mineru_converted",
        "pages": "-",
        "images": str(image_count),
    }


def inspect_existing_result(target: PdfTarget) -> dict[str, str]:
    output = OUTPUT_ROOT / target.topic / target.output_name
    if not output.exists():
        return {"source": target.source, "output": output.as_posix(), "status": "missing", "pages": "-"}
    text = output.read_text(encoding="utf-8", errors="ignore")
    result = {"source": target.source, "output": output.as_posix(), "status": "converted", "pages": "-", "images": "-"}
    if "Converted by: `MinerU precise API`" in text:
        result["status"] = "mineru_converted"
        image_dir = output.parent / f"{output.stem}_images"
        if image_dir.exists():
            result["images"] = str(len([p for p in image_dir.iterdir() if p.is_file()]))
    elif "Converted by: `local PyMuPDF fallback`" in text:
        result["status"] = "converted"
        match = re.search(r"- Pages: `([^`]+)`", text)
        if match:
            result["pages"] = match.group(1)
    return result


def write_markdown(target: PdfTarget) -> dict[str, str]:
    source = SOURCE_ROOT / target.source
    output = OUTPUT_ROOT / target.topic / target.output_name
    output.parent.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        output.write_text(
            "\n".join(
                [
                    f"# {target.output_name.removesuffix('.md')}",
                    "",
                    f"- Source: `{source.as_posix()}`",
                    "- Converted by: `local PyMuPDF fallback`",
                    f"- Conversion date: `{date.today().isoformat()}`",
                    "- Review status: `missing source`",
                    f"- Priority: `{target.priority}`",
                    "",
                    "Source PDF was not found.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return {"source": target.source, "output": output.as_posix(), "status": "missing"}

    page_count, body = extract_pdf(source)
    digest = hashlib.sha1(source.read_bytes()).hexdigest()[:12]
    title = target.output_name.removesuffix(".md")
    output.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"- Source: `{source.as_posix()}`",
                "- Converted by: `local PyMuPDF fallback`",
                f"- Conversion date: `{date.today().isoformat()}`",
                "- Review status: `unchecked; MinerU retry recommended`",
                f"- Priority: `{target.priority}`",
                f"- Source SHA1: `{digest}`",
                f"- Pages: `{page_count}`",
                f"- Notes: {target.note}",
                "",
                "> MinerU MCP was attempted first in this environment, but the current network path to MinerU returned SSL EOF/disconnect errors. This file is a local text-extraction fallback for search and implementation reference.",
                "",
                body,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {"source": target.source, "output": output.as_posix(), "status": "converted", "pages": str(page_count)}


def write_markdown_with_mineru(
    target: PdfTarget,
    *,
    token: str,
    model_version: str,
    poll_interval: int,
    timeout_seconds: int,
    force: bool,
    continue_on_download_error: bool,
) -> dict[str, str]:
    source = SOURCE_ROOT / target.source
    output = OUTPUT_ROOT / target.topic / target.output_name
    output.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return {"source": target.source, "output": output.as_posix(), "status": "missing"}
    if output.exists() and not force:
        text = output.read_text(encoding="utf-8", errors="ignore")
        if "Converted by: `MinerU precise API`" in text:
            return {"source": target.source, "output": output.as_posix(), "status": "skipped"}

    data_id = safe_stem(f"{target.priority}_{target.topic}_{source.stem}_{hashlib.sha1(target.source.encode()).hexdigest()[:8]}")
    apply_payload = {
        "files": [{"name": source.name, "data_id": data_id}],
        "model_version": model_version,
        "language": "ch",
        "enable_formula": True,
        "enable_table": True,
        "extra_formats": ["html"],
    }
    apply_result = request_json(f"{MINERU_BASE_URL}/file-urls/batch", token=token, method="POST", data=apply_payload)
    if apply_result.get("code") != 0:
        raise RuntimeError(f"MinerU upload URL request failed for {source.name}: {apply_result.get('msg')}")
    batch_id = apply_result["data"]["batch_id"]
    upload_url = apply_result["data"]["file_urls"][0]
    upload_file(upload_url, source)

    deadline = time.time() + timeout_seconds
    last_state = "waiting-file"
    result_item: dict | None = None
    while time.time() < deadline:
        poll_result = request_json(f"{MINERU_BASE_URL}/extract-results/batch/{batch_id}", token=token)
        if poll_result.get("code") != 0:
            raise RuntimeError(f"MinerU poll failed for {source.name}: {poll_result.get('msg')}")
        items = poll_result.get("data", {}).get("extract_result", [])
        result_item = items[0] if items else None
        last_state = result_item.get("state", last_state) if result_item else last_state
        if last_state == "done":
            break
        if last_state == "failed":
            raise RuntimeError(f"MinerU parse failed for {source.name}: {result_item.get('err_msg', '')}")
        time.sleep(poll_interval)
    else:
        raise TimeoutError(f"MinerU parse timeout for {source.name}; last state: {last_state}")

    if not result_item or not result_item.get("full_zip_url"):
        raise RuntimeError(f"MinerU did not return full_zip_url for {source.name}")

    log_path = write_mineru_result_log(target, batch_id, data_id, result_item)
    print(f"MinerU result URL: {result_item['full_zip_url']}")
    print(f"MinerU result log: {log_path}")

    work_dir = TMP_ROOT / data_id
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    zip_path = work_dir / "result.zip"
    try:
        download_file(result_item["full_zip_url"], zip_path)
    except Exception as exc:
        if continue_on_download_error:
            return {
                "source": target.source,
                "output": output.as_posix(),
                "status": "mineru_url_ready",
                "pages": "-",
                "full_zip_url": result_item["full_zip_url"],
                "error": str(exc),
            }
        raise
    extract_dir = work_dir / "unzipped"
    with ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)
    return promote_mineru_markdown(target, source=source, extract_dir=extract_dir, batch_id=batch_id)


def write_index(results: list[dict[str, str]], method: str) -> None:
    index_path = OUTPUT_ROOT / "转换索引.md"
    lines = [
        "# MWORKS PDF 转换索引",
        "",
        f"- Generated: `{date.today().isoformat()}`",
        "- Preferred converter: `MinerU MCP`",
        f"- Current converter: `{method}`",
        "- Review note: 重要 API、公式、表格和代码块仍需结合 MCP 官方文档或原 PDF 复核。",
        "",
        "| Status | Topic | Pages | Images | Markdown | Source | Result URL |",
        "|---|---|---:|---:|---|---|---|",
    ]
    by_output = {r["output"]: r for r in results}
    for target in TARGETS:
        output = (OUTPUT_ROOT / target.topic / target.output_name).as_posix()
        result = by_output.get(output) or inspect_existing_result(target)
        lines.append(
            "| "
            + " | ".join(
                [
                    result.get("status", "unknown"),
                    target.topic,
                    result.get("pages", "-"),
                    result.get("images", "-"),
                    f"`{output}`",
                    f"`{target.source}`",
                    result.get("full_zip_url", "-"),
                ]
            )
            + " |"
        )
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pending_downloads(results: list[dict[str, str]]) -> None:
    pending = [r for r in results if r.get("status") == "mineru_url_ready"]
    if not pending:
        return
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TMP_ROOT / "pending_downloads.md"
    lines = [
        "# MinerU Pending Downloads",
        "",
        f"Generated: `{time.strftime('%Y-%m-%d %H:%M:%S')}`",
        "",
        "| Source | Output | URL | Error |",
        "|---|---|---|---|",
    ]
    for item in pending:
        lines.append(
            "| "
            + " | ".join(
                [
                    item.get("source", "-"),
                    item.get("output", "-"),
                    item.get("full_zip_url", "-"),
                    item.get("error", "-").replace("|", "\\|").replace("\n", " ")[:500],
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Pending MinerU downloads: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=["pymupdf", "mineru"], default="pymupdf")
    parser.add_argument("--limit", type=int, default=0, help="Convert only the first N targets; 0 means all targets.")
    parser.add_argument("--priority", action="append", choices=["P0", "P1", "P2"], help="Filter target priority. Can be repeated.")
    parser.add_argument("--model-version", default="vlm", choices=["pipeline", "vlm"])
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--force", action="store_true", help="Overwrite existing MinerU-converted files.")
    parser.add_argument(
        "--continue-on-download-error",
        action="store_true",
        help="Record MinerU result URLs and continue if downloading result zip fails.",
    )
    parser.add_argument(
        "--import-mineru-result",
        type=Path,
        help="Import a manually downloaded MinerU result zip or extracted directory for the first selected target.",
    )
    return parser.parse_args()


def select_targets(args: argparse.Namespace) -> list[PdfTarget]:
    targets = TARGETS
    if args.priority:
        allowed = set(args.priority)
        targets = [target for target in targets if target.priority in allowed]
    if args.limit > 0:
        targets = targets[: args.limit]
    return targets


def main() -> int:
    args = parse_args()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    targets = select_targets(args)
    method_label = args.method
    if args.import_mineru_result:
        method_label = "manual_mineru_import"
        if not targets:
            raise SystemExit("No target selected for --import-mineru-result.")
        target = targets[0]
        source = SOURCE_ROOT / target.source
        import_path = args.import_mineru_result
        if not import_path.exists():
            raise SystemExit(f"MinerU result path not found: {import_path}")
        work_dir = TMP_ROOT / f"manual_import_{safe_stem(target.output_name)}"
        if work_dir.exists():
            shutil.rmtree(work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        if import_path.is_file():
            with ZipFile(import_path) as zf:
                zf.extractall(work_dir)
            extract_dir = work_dir
        else:
            extract_dir = import_path
        results = [promote_mineru_markdown(target, source=source, extract_dir=extract_dir, batch_id="manual_import")]
    elif args.method == "mineru":
        token = os.environ.get("MINERU_API_TOKEN")
        if not token:
            raise SystemExit("MINERU_API_TOKEN is not set. Set it in the environment, not in tracked files.")
        results = []
        for index, target in enumerate(targets, start=1):
            print(f"[{index}/{len(targets)}] MinerU converting: {target.source}")
            results.append(
                write_markdown_with_mineru(
                    target,
                    token=token,
                    model_version=args.model_version,
                    poll_interval=args.poll_interval,
                    timeout_seconds=args.timeout_seconds,
                    force=args.force,
                    continue_on_download_error=args.continue_on_download_error,
                )
            )
    else:
        results = [write_markdown(target) for target in targets]
    write_index(results, method_label)
    write_pending_downloads(results)
    converted = sum(1 for r in results if r["status"] in {"converted", "mineru_converted", "skipped"})
    missing = sum(1 for r in results if r["status"] == "missing")
    print(f"Processed PDFs: {converted}")
    print(f"Missing PDFs: {missing}")
    print(f"Index: {OUTPUT_ROOT / '转换索引.md'}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
