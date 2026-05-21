# Office 离线技能迁移说明（-offline）

这组 `*-offline` 技能用于**本地/离线**处理 Office/PDF 文件：读写、解析、编辑、回包、以及基于本地工具链的转换与渲染。

注意：**“离线”指工作流不依赖外部在线服务**；但首次安装依赖（`pip` / `npm` / `brew` / `apt-get`）可能需要网络。

## 技能映射

- `pdf-offline`：PDF 读写/合并拆分/表单处理 + 快捷 CLI（`doc_utils.py`）
- `xlsx-offline`：Excel 读写 + 公式重算与错误扫描（`recalc.py`，默认隔离 LibreOffice profile）
- `docx-offline`：DOCX 读写 + OOXML 解包编辑回包 + redlining（修订/批注）
- `pptx-offline`：PPTX 读写 + OOXML 工作流 + html2pptx（HTML→PPT）+ 缩略图/替换/重排脚本

## 典型触发（建议写法）

- “读取/总结/提取内容：`xxx.pdf/.docx/.pptx/.xlsx`”
- “修改模板但保留格式/修订痕迹（合同/制度/论文）”
- “从 HTML 生成 PPT 并要求像素级布局”
- “检查 Excel 公式是否有 `#REF!/#DIV/0!` 等错误并输出定位”

