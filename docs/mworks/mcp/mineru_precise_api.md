# MinerU 精准解析 API 使用说明

> 本文记录 MinerU 精准解析 API 的项目内使用约定。不要把真实 Token 写入本文档、脚本、提交记录或任何可上传仓库的文件。

## 1. 用途

MinerU 精准解析 API 用于将复杂 PDF、图片、Doc/Docx、Ppt/PPTx 和 HTML 文档解析为结构化结果。它比本地文本提取更适合处理：

- 表格、公式、图表和图片；
- 多栏布局、扫描件、水印干扰；
- 需要保留层级结构的官方手册、培训材料和报告素材。

本项目已用 MinerU 精准解析完成 `docs/mworks/converted/` 中的 P0/P1/P2 重点资料转换；后续仅在新增资料或发现解析质量问题时增量重转。

## 2. Token 放置

WSL使用环境变量：

```bash
export MINERU_API_TOKEN="你的 Token"
```

PowerShell：

```powershell
$env:MINERU_API_TOKEN = "你的 Token"
```

不要使用以下做法：

- 不要写入 `.env` 后提交；
- 不要写入 `AGENTS.md`、README、脚本默认值；
- 不要把 Token 粘贴到日志或 issue；
- 不要把包含 Token 的 curl 命令提交到仓库。

## 3. 能力与限制

| 项目             | 限制                                                           |
| ---------------- | -------------------------------------------------------------- |
| 单文件大小       | 200 MB                                                         |
| 单文件页数       | 200 页                                                         |
| 支持格式         | PDF、png、jpg、jpeg、jp2、webp、gif、bmp、Doc、Docx、Ppt、PPTx |
| 模型版本         | `pipeline`、`vlm`、`MinerU-HTML`                         |
| 每日高优先级额度 | 每账号每天 1000 页，超出后优先级降低                           |

非 HTML 文件可选 `pipeline` 或 `vlm`。HTML 文件必须使用 `MinerU-HTML`。

## 4. 推荐参数

MWORKS 资料包的 PDF 通常以中文为主，建议默认：

```json
{
  "model_version": "vlm",
  "language": "ch",
  "enable_formula": true,
  "enable_table": true,
  "is_ocr": false
}
```

如果 PDF 是扫描件或本地兜底转换文本为空，再把 `is_ocr` 设为 `true`。

如果只想先重转部分页面，可设置：

```json
{
  "page_ranges": "1-20"
}
```

## 5. 单个 URL 文件解析

创建任务：

```python
import os
import requests

token = os.environ["MINERU_API_TOKEN"]
url = "https://mineru.net/api/v4/extract/task"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}
data = {
    "url": "https://cdn-mineru.openxlab.org.cn/demo/example.pdf",
    "model_version": "vlm",
    "language": "ch",
    "enable_formula": True,
    "enable_table": True,
}

res = requests.post(url, headers=headers, json=data, timeout=60)
res.raise_for_status()
print(res.json())
```

查询任务：

```python
import os
import requests

token = os.environ["MINERU_API_TOKEN"]
task_id = "创建任务返回的 task_id"
url = f"https://mineru.net/api/v4/extract/task/{task_id}"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}

res = requests.get(url, headers=headers, timeout=60)
res.raise_for_status()
print(res.json())
```

任务完成后，响应中的 `data.full_zip_url` 是结果压缩包地址。非 HTML 文件通常包含：

- `full.md`：Markdown 解析结果；
- `*_content_list.json`：内容列表；
- `layout.json` 或中间处理结果；
- `*_model.json`：模型推理结果。

HTML 文件通常包含：

- `full.md`；
- `main.html`。

## 6. 本地文件批量上传解析

本地 PDF 不能直接传给单文件 URL 接口。应先申请上传链接，再 PUT 上传文件。上传完成后，MinerU 会自动提交解析任务。

申请上传链接：

```python
import os
import requests

token = os.environ["MINERU_API_TOKEN"]
url = "https://mineru.net/api/v4/file-urls/batch"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}
data = {
    "files": [
        {
            "name": "syslab_sysplorer_2024a.pdf",
            "data_id": "syslab_sysplorer_2024a",
            "page_ranges": "1-26"
        }
    ],
    "model_version": "vlm",
    "language": "ch",
    "enable_formula": True,
    "enable_table": True,
}

response = requests.post(url, headers=headers, json=data, timeout=60)
response.raise_for_status()
result = response.json()
print(result)
```

上传文件：

```python
upload_url = result["data"]["file_urls"][0]
with open("syslab_sysplorer_2024a.pdf", "rb") as f:
    upload = requests.put(upload_url, data=f, timeout=600)
upload.raise_for_status()
```

注意：上传文件时不要额外设置 `Content-Type` 请求头。

## 7. URL 批量解析

批量提交 URL：

```python
import os
import requests

token = os.environ["MINERU_API_TOKEN"]
url = "https://mineru.net/api/v4/extract/task/batch"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}
data = {
    "files": [
        {
            "url": "https://cdn-mineru.openxlab.org.cn/demo/example.pdf",
            "data_id": "example_pdf"
        }
    ],
    "model_version": "vlm",
    "language": "ch",
    "enable_formula": True,
    "enable_table": True,
}

res = requests.post(url, headers=headers, json=data, timeout=60)
res.raise_for_status()
print(res.json())
```

查询批量结果：

```python
import os
import requests

token = os.environ["MINERU_API_TOKEN"]
batch_id = "提交任务返回的 batch_id"
url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}

res = requests.get(url, headers=headers, timeout=60)
res.raise_for_status()
print(res.json())
```

## 8. 回调参数

如使用 `callback`，必须同时提供 `seed`。MinerU 会向回调接口 POST：

- `checksum`：由用户 UID + seed + content 拼接后计算 SHA256；
- `content`：JSON 字符串，需要服务端自行反序列化。

回调接口要求：

- 支持 POST；
- UTF-8 编码；
- `Content-Type: application/json`；
- 返回 HTTP 200 表示接收成功；
- 非 200 会触发最多 5 次重试。

本项目默认不使用 callback，优先轮询任务状态，便于本地脚本和 Codex 调试。

## 9. 常见错误码

| 错误码     | 说明               | 处理建议                           |
| ---------- | ------------------ | ---------------------------------- |
| `A0202`  | Token 错误         | 检查 `Bearer ` 前缀和 Token 内容 |
| `A0211`  | Token 过期         | 更换新 Token                       |
| `-500`   | 传参错误           | 检查参数类型和 `Content-Type`    |
| `-10001` | 服务异常           | 稍后重试                           |
| `-10002` | 请求参数错误       | 检查 JSON 格式                     |
| `-60001` | 生成上传 URL 失败  | 稍后重试                           |
| `-60002` | 文件格式检测失败   | 检查文件后缀和真实格式             |
| `-60003` | 文件读取失败       | 检查文件是否损坏                   |
| `-60004` | 空文件             | 换有效文件                         |
| `-60005` | 文件大小超限       | 拆分文件，单文件不超过 200 MB      |
| `-60006` | 页数超限           | 拆分文件，单文件不超过 200 页      |
| `-60007` | 模型服务暂不可用   | 稍后重试                           |
| `-60008` | URL 读取超时       | 检查 URL 可访问性                  |
| `-60009` | 队列已满           | 稍后重试                           |
| `-60010` | 解析失败           | 稍后重试或换模型                   |
| `-60011` | 获取有效文件失败   | 确认文件已经上传完成               |
| `-60012` | 找不到任务         | 检查 `task_id`                   |
| `-60013` | 无权限访问任务     | 确认 Token 与任务归属一致          |
| `-60014` | 删除运行中任务     | 等任务结束后处理                   |
| `-60015` | 文件转换失败       | 手动转 PDF 后重试                  |
| `-60016` | 指定格式导出失败   | 换导出格式或重试                   |
| `-60017` | 重试次数达到上限   | 后续模型升级后重试                 |
| `-60018` | 每日任务数量达上限 | 次日再试                           |
| `-60019` | HTML 解析额度不足  | 次日再试                           |
| `-60020` | 文件拆分失败       | 稍后重试                           |
| `-60021` | 读取页数失败       | 稍后重试                           |
| `-60022` | 网页读取失败       | 检查网络或稍后重试                 |

## 10. 项目内重转流程

推荐流程：

```text
1. 从 docs/mworks/converted/转换索引.md 选择要重转的 PDF。
2. 从原始资料包复制 PDF 到临时目录，使用英文短文件名。
3. 通过 /api/v4/file-urls/batch 申请上传链接。
4. PUT 上传文件。
5. 轮询 /api/v4/extract-results/batch/{batch_id}。
6. 下载 full_zip_url。
7. 解压 full.md 到 docs/mworks/converted/<topic>/。
8. 保留源路径、模型版本、页数、转换日期和 Review status。
9. 更新 docs/mworks/converted/转换索引.md 和 docs/index/doc_index.md。
```

建议优先重转：

```text
P0: Syslab 与 Sysplorer 双向集成
P0: Modelica 语法详解
P1: Syslab 控制系统工具箱
P1: 参数估计、系统辨识、鲁棒控制
P1: 智能无人系统挑战赛资料
P2: 外部接口和 Python 脚本接口
```

## 11. 与 MinerU MCP 的关系

当前 Codex MCP 中的 `mineru` 服务可通过 `parse_documents` 做快捷解析，但无 Token 时是 Flash 模式，限制更低。精准解析 API 适合：

- 本地资料批量上传；
- 超过 Flash 限制的 PDF；
- 需要 `vlm`、`pipeline`、`MinerU-HTML` 明确模型控制；
- 需要额外导出 `docx`、`html`、`latex`。

如果设置了 `MINERU_API_TOKEN`，优先让 MinerU MCP 自动使用 Token；如果 MCP 网络仍不稳定，再使用本文的 REST API 直连流程排查。
