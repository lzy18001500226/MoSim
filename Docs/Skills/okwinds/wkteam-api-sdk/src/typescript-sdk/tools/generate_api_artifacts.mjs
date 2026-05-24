import fs from "node:fs/promises";
import path from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

function findRepoRootFrom(startDir) {
  const anchor = path.join("docs", "api", "api-wen-dang2");
  let cur = startDir;
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const candidate = path.join(cur, anchor);
    if (existsSync(candidate)) return cur;
    const parent = path.dirname(cur);
    if (parent === cur) throw new Error(`无法定位 repo root：未找到 ${anchor}`);
    cur = parent;
  }
}

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const packageRoot = path.resolve(scriptDir, "..");
const repoRoot = findRepoRootFrom(packageRoot);
const apiDocsRoot = path.join(repoRoot, "docs", "api", "api-wen-dang2");
const outSchemasDir = path.join(
  repoRoot,
  "docs",
  "specs",
  "engineering-spec",
  "02_Technical_Design",
  "schemas",
);
const outApiSpecPath = path.join(
  repoRoot,
  "docs",
  "specs",
  "engineering-spec",
  "02_Technical_Design",
  "API_SPEC.md",
);
const outCoveragePath = path.join(
  repoRoot,
  "docs",
  "specs",
  "engineering-spec",
  "00_Overview",
  "API_DOC_COVERAGE.generated.md",
);

function stripFrontmatter(md) {
  const s = String(md);
  if (!s.startsWith("---")) return s;
  const idx = s.indexOf("\n---", 3);
  if (idx === -1) return s;
  return s.slice(idx + "\n---".length);
}

function firstHeading(md) {
  const s = stripFrontmatter(md);
  const lines = s.split(/\r?\n/);
  for (const line of lines) {
    const m = /^(#{1,3})\s+(.+?)\s*$/.exec(line);
    if (m) return m[2].trim();
  }
  return null;
}

function extractAfterLabel(md, label) {
  const s = stripFrontmatter(md);
  const idx = s.indexOf(label);
  if (idx === -1) return null;
  const tail = s.slice(idx);
  const lines = tail.split(/\r?\n/).slice(0, 12);
  return lines.join("\n");
}

function extractRequestUrl(md) {
  const block = extractAfterLabel(md, "请求URL");
  if (!block) return null;
  // Common forms:
  // - `http://domain/path`
  // - [http://domain/path](http://domain/path)
  // - http://domain/path
  const mTick = /`(https?:\/\/[^`]+)`/.exec(block);
  if (mTick) return mTick[1];
  const mLink = /\((https?:\/\/[^)\s]+)\)/.exec(block);
  if (mLink) return mLink[1];
  const mPlain = /\bhttps?:\/\/[^\s)]+/.exec(block);
  if (mPlain) return mPlain[0];
  return null;
}

function extractRequestMethod(md) {
  // Preferred: explicit "请求方式"
  const block = extractAfterLabel(md, "请求方式");
  if (block) {
    const m = /\b(GET|POST|PUT|PATCH|DELETE)\b/i.exec(block);
    if (m) return m[1].toUpperCase();
  }

  // Fallback: some docs list method right after 请求URL block as bullet
  const urlBlock = extractAfterLabel(md, "请求URL");
  if (urlBlock) {
    const m = /\b(GET|POST|PUT|PATCH|DELETE)\b/i.exec(urlBlock);
    if (m) return m[1].toUpperCase();
  }

  return null;
}

function extractHeaders(md) {
  const block = extractAfterLabel(md, "请求头Headers");
  if (!block) return [];
  const lines = block.split(/\r?\n/);
  const headers = [];
  for (const line of lines) {
    const m = /^\*\s+([^：:]+)[：:]\s*(.+)\s*$/.exec(line.trim());
    if (m) headers.push({ name: m[1].trim(), value: m[2].trim() });
  }
  return headers;
}

function parseMarkdownTable(md, headerText) {
  const s = stripFrontmatter(md);
  const idx = s.indexOf(headerText);
  if (idx === -1) return [];
  const tail = s.slice(idx);
  const lines = tail.split(/\r?\n/);
  const tableStart = lines.findIndex((l) => l.includes("|") && l.includes("参数名"));
  if (tableStart === -1) return [];

  const rows = [];
  for (let i = tableStart; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line.startsWith("|")) {
      if (rows.length > 0) break;
      continue;
    }
    const cells = line
      .split("|")
      .slice(1, -1)
      .map((c) => c.trim());
    if (cells.every((c) => c === "")) continue;
    rows.push(cells);
  }

  if (rows.length < 2) return [];
  const header = rows[0];
  const divider = rows[1];
  if (divider.some((c) => !/^-+$/.test(c.replaceAll(" ", "")))) {
    // Not a standard markdown table; best-effort: keep as-is
  }

  const body = rows.slice(2);
  return body.map((cells) => {
    const obj = {};
    for (let i = 0; i < header.length; i++) obj[header[i] || `col${i + 1}`] = cells[i] ?? "";
    return obj;
  });
}

function extractParams(md) {
  // Many docs use "参数：" section.
  return parseMarkdownTable(md, "参数");
}

function extractReturnData(md) {
  return parseMarkdownTable(md, "返回数据");
}

function normalizePathFromRequestUrl(requestUrl) {
  if (!requestUrl) return null;
  try {
    const u = new URL(requestUrl);
    return u.pathname || null;
  } catch {
    // requestUrl might be `http://域名地址/sendFile`
    const m = /^https?:\/\/[^/]+(\/.+)$/.exec(requestUrl);
    return m ? m[1] : null;
  }
}

function toOperationId(moduleName, fileStem) {
  const cleanModule = moduleName.replaceAll(/[^a-zA-Z0-9]+/g, "_").replaceAll(/^_+|_+$/g, "");
  const cleanStem = fileStem.replaceAll(/[^a-zA-Z0-9]+/g, "_").replaceAll(/^_+|_+$/g, "");
  return `${cleanModule}_${cleanStem}` || fileStem;
}

async function listMarkdownFiles(dir) {
  const out = [];
  async function walk(d) {
    const entries = await fs.readdir(d, { withFileTypes: true });
    for (const e of entries) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) await walk(p);
      else if (e.isFile() && e.name.endsWith(".md")) out.push(p);
    }
  }
  await walk(dir);
  return out.sort((a, b) => a.localeCompare(b));
}

function relFromRepo(p) {
  return path.relative(repoRoot, p).replaceAll("\\", "/");
}

function groupBy(arr, keyFn) {
  const m = new Map();
  for (const it of arr) {
    const k = keyFn(it);
    const list = m.get(k) ?? [];
    list.push(it);
    m.set(k, list);
  }
  return m;
}

function isCategoryReadme(relPath) {
  return relPath.endsWith("/README.md") || relPath.endsWith("\\README.md");
}

function classifyKind({ relPath, requestUrl, method, params, returns }) {
  if (isCategoryReadme(relPath)) return "category";
  if (requestUrl || method) return "endpoint";
  // Non-endpoint reference docs (e.g., callback payload interpretation)
  if ((params && params.length > 0) || (returns && returns.length > 0)) return "reference";
  return "reference";
}

function toMarkdownCell(s) {
  return String(s ?? "")
    .replaceAll("|", "\\|")
    .replaceAll("\n", " ")
    .trim();
}

function toMarkdownTable(rows, columnOrder) {
  if (!rows || rows.length === 0) return null;
  const cols = columnOrder ?? Object.keys(rows[0] ?? {});
  const header = `| ${cols.map(toMarkdownCell).join(" | ")} |`;
  const divider = `| ${cols.map(() => "---").join(" | ")} |`;
  const body = rows.map((r) => `| ${cols.map((c) => toMarkdownCell(r[c] ?? "")).join(" | ")} |`);
  return [header, divider, ...body].join("\n");
}

async function main() {
  await fs.mkdir(outSchemasDir, { recursive: true });

  const files = await listMarkdownFiles(apiDocsRoot);
  const catalog = [];

  for (const absPath of files) {
    const relPath = relFromRepo(absPath);
    const md = await fs.readFile(absPath, "utf-8");
    const title = firstHeading(md) ?? path.basename(absPath, ".md");

    const parts = relPath.split("/");
    const moduleName = parts.length >= 4 ? parts[3] : "api";
    const fileStem = path.basename(absPath, ".md");

    const requestUrl = extractRequestUrl(md);
    const method = extractRequestMethod(md);
    const headers = extractHeaders(md);
    const params = extractParams(md);
    const returns = extractReturnData(md);
    const endpointPath = normalizePathFromRequestUrl(requestUrl);

    const entry = {
      doc: relPath,
      title,
      module: moduleName,
      kind: classifyKind({ relPath, requestUrl, method, params, returns }),
      operationId: toOperationId(moduleName, fileStem),
      method,
      path: endpointPath,
      requestUrl,
      headers,
      params,
      returns,
    };

    catalog.push(entry);
  }

  const outCatalogPath = path.join(outSchemasDir, "api_catalog.json");
  await fs.writeFile(
    outCatalogPath,
    JSON.stringify({ generatedAt: new Date().toISOString(), catalog }, null, 2),
  );

  // Coverage report (1:1 mapping of docs -> catalog)
  const coverageLines = [
    "# API Doc Coverage (Generated)",
    "",
    `Generated at: \`${new Date().toISOString()}\``,
    "",
    `Docs root: \`${relFromRepo(apiDocsRoot)}/\``,
    `Catalog: \`${relFromRepo(outCatalogPath)}\``,
    "",
    "## Summary",
    "",
    `- Total markdown files: **${files.length}**`,
    `- Catalog entries: **${catalog.length}**`,
    `- Endpoint entries: **${catalog.filter((e) => e.kind === "endpoint").length}**`,
    `- Category entries: **${catalog.filter((e) => e.kind === "category").length}**`,
    "",
    "## Parse Quality (Heuristics)",
    "",
    `- With method: **${catalog.filter((e) => e.method).length}**`,
    `- With path: **${catalog.filter((e) => e.path).length}**`,
    "",
    "## Unparsed / Needs Manual Check",
    "",
  ];

  const needsCheck = catalog
    .filter((e) => e.kind === "endpoint" && (!e.method || !e.path))
    .map((e) => `- \`${e.doc}\` — method=\`${e.method ?? "?"}\` path=\`${e.path ?? "?"}\``);
  coverageLines.push(...(needsCheck.length ? needsCheck : ["- (none)"]));
  coverageLines.push("");

  await fs.writeFile(outCoveragePath, coverageLines.join("\n"));

  // Generated API spec markdown (index table per module)
  const endpointEntries = catalog.filter((e) => e.kind === "endpoint");
  const referenceEntries = catalog.filter((e) => e.kind === "reference");
  const categoryEntries = catalog.filter((e) => e.kind === "category");
  const grouped = groupBy(endpointEntries, (e) => e.module);
  const apiSpecLines = [
    "# API Spec（从离线文档生成）",
    "",
    `Generated at: \`${new Date().toISOString()}\``,
    "",
    "本文件由离线文档自动提取生成，用于 SDK 工程落地：",
    "- 提供 **全量 endpoint 清单**（method/path/参数/返回/鉴权）",
    "- 作为实现与测试的“需求输入”（避免遗漏接口）",
    "",
    "权威来源仍为 `docs/api/` 中的接口说明文档；当解析与原文不一致时，以原文为准，并更新解析规则与本文件。",
    "",
    `Catalog JSON: \`${relFromRepo(outCatalogPath)}\``,
    "",
    "## 全局约定（提炼自离线文档）",
    "",
    "- `baseUrl`：文档中使用 `http://域名地址/...` 占位，SDK 必须允许使用方配置。",
    "- `Authorization`：多数接口需要该请求头（来自登录接口返回）。SDK 默认 **原文注入**，是否添加前缀由配置控制。",
    "- 响应：常见为 `{ code, message/msg, data }`；其中 `code == 1000` 表示成功，`1001` 表示失败（接口间可能存在差异，SDK 需允许接口级覆盖）。",
    "",
    "## 目录",
    "",
  ];

  // Index
  apiSpecLines.push("| module | operationId | title | method | path | doc |");
  apiSpecLines.push("|---|---|---|---|---|---|");
  for (const e of endpointEntries.sort((a, b) => a.operationId.localeCompare(b.operationId))) {
    apiSpecLines.push(
      `| \`${toMarkdownCell(e.module)}\` | \`${toMarkdownCell(e.operationId)}\` | ${toMarkdownCell(
        e.title,
      )} | \`${toMarkdownCell(e.method)}\` | \`${toMarkdownCell(e.path)}\` | \`${toMarkdownCell(e.doc)}\` |`,
    );
  }
  apiSpecLines.push("");

  for (const [moduleName, list] of [...grouped.entries()].sort((a, b) =>
    a[0].localeCompare(b[0]),
  )) {
    apiSpecLines.push(`## 模块：\`${moduleName}\``);
    apiSpecLines.push("");
    for (const e of list.sort((a, b) => a.path.localeCompare(b.path))) {
      apiSpecLines.push(`### ${e.method} ${e.path}`);
      apiSpecLines.push("");
      apiSpecLines.push(`- operationId: \`${e.operationId}\``);
      apiSpecLines.push(`- title: ${e.title}`);
      apiSpecLines.push(`- doc: \`${e.doc}\``);
      if (e.requestUrl) apiSpecLines.push(`- requestUrl (as documented): \`${e.requestUrl}\``);
      if (e.headers?.length) {
        apiSpecLines.push("");
        apiSpecLines.push("**Headers（文档提取）**");
        for (const h of e.headers) apiSpecLines.push(`- ${h.name}: ${h.value}`);
      }

      const paramsTable = toMarkdownTable(
        e.params,
        ["参数名", "必选", "必填", "类型", "说明"].filter((k) => e.params?.[0]?.[k] !== undefined),
      );
      if (paramsTable) {
        apiSpecLines.push("");
        apiSpecLines.push("**参数（文档提取）**");
        apiSpecLines.push("");
        apiSpecLines.push(paramsTable);
      }

      const returnsTable = toMarkdownTable(
        e.returns,
        ["参数名", "类型", "说明"].filter((k) => e.returns?.[0]?.[k] !== undefined),
      );
      if (returnsTable) {
        apiSpecLines.push("");
        apiSpecLines.push("**返回数据（文档提取）**");
        apiSpecLines.push("");
        apiSpecLines.push(returnsTable);
      }

      apiSpecLines.push("");
    }
  }

  if (referenceEntries.length) {
    apiSpecLines.push("## Reference Docs（非 endpoint）");
    apiSpecLines.push("");
    apiSpecLines.push("| title | doc |");
    apiSpecLines.push("|---|---|");
    for (const e of referenceEntries.sort((a, b) => a.doc.localeCompare(b.doc))) {
      apiSpecLines.push(`| ${toMarkdownCell(e.title)} | \`${toMarkdownCell(e.doc)}\` |`);
    }
    apiSpecLines.push("");
  }

  if (categoryEntries.length) {
    apiSpecLines.push("## Category Docs（目录页）");
    apiSpecLines.push("");
    apiSpecLines.push("| title | doc |");
    apiSpecLines.push("|---|---|");
    for (const e of categoryEntries.sort((a, b) => a.doc.localeCompare(b.doc))) {
      apiSpecLines.push(`| ${toMarkdownCell(e.title)} | \`${toMarkdownCell(e.doc)}\` |`);
    }
    apiSpecLines.push("");
  }

  await fs.writeFile(outApiSpecPath, apiSpecLines.join("\n"));

  process.stdout.write(
    `Wrote:\n- ${relFromRepo(outCatalogPath)}\n- ${relFromRepo(outCoveragePath)}\n- ${relFromRepo(outApiSpecPath)}\n`,
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
