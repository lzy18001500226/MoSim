# wkteam-api-sdk（Python 3.11）

本目录交付 `wkteam api-wen-dang2` 的 **Python SDK**。权威输入是仓库内离线文档与生成的 catalog：

- `docs/api/api-wen-dang2/`
- `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`

目标：接口全覆盖（当前 127 endpoint）、可离线回归、可配置鉴权/超时/重试/并发限制、日志脱敏与 hook。

## 安装（开发态）

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

> 说明：本 SDK 默认不读取 `.env`。`base_url` 与 `authorization` 必须由调用方配置。

## 快速开始（同步）

```python
from wkteam_api_sdk import WkteamClient

client = WkteamClient(
    base_url="https://api.example.com",
    authorization="YOUR_AUTH_TOKEN",
)

res = client.api.deng_lu.deng_lu_wei_kong_ping_tai_di_yi_bu(callbackUrl="https://your.webhook")
print(res)
```

## 快速开始（异步）

```python
import asyncio
from wkteam_api_sdk import AsyncWkteamClient


async def main() -> None:
    client = AsyncWkteamClient(base_url="https://api.example.com", authorization="YOUR_AUTH_TOKEN")
    res = await client.api.biao_qian.get_contact_label_list(wId="...")
    print(res)


asyncio.run(main())
```

## 开发命令

在仓库根目录（`wkteam-api-sdk/`）执行：

- 生成 Python wrappers/manifest：
  - `python3.11 src/python-sdk/tools/generate_sdk.py`
- 运行离线回归：
  - `PYTHONPATH=src/python-sdk python3.11 -m pytest -q src/python-sdk/tests`

也可以进入 `src/python-sdk/` 目录执行（无需设置 `PYTHONPATH`）：

- `python3.11 tools/generate_sdk.py`
- `python3.11 -m pytest -q`

## 配置说明

关键配置项（与工程规格保持一致）：

- `base_url`：API baseUrl（必填）
- `authorization`：`Authorization` 原始值（必填），或函数（sync/async）
- `authorization_header_name`：默认 `Authorization`
- `authorization_prefix`：默认不加前缀
- `timeout_ms`：默认 `15000`
- `retry`：分类重试（safe vs side_effect）
- `hooks`：on_request/on_response/on_retry/on_error

完整配置约束见：`docs/specs/engineering-spec/04_Operations/CONFIGURATION.md`
