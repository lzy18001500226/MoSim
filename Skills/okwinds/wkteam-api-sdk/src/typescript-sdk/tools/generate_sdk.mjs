import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";

/**
 * 根据 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json` 生成 SDK 代码：
 * - `src/generated/endpoints.ts`：endpoint 元数据（method/path/鉴权/参数）
 * - `src/generated/validators.ts`：zod 参数校验器（必填字段）
 * - `src/generated/api.ts`：模块化 API tree（client.api.*）
 * - `src/generated/manifest.ts`：operationId 清单（用于覆盖性测试）
 *
 * 约束：
 * - 生成输出必须稳定（同输入同输出）
 * - 不做伪精确类型推断：无法确定的类型使用 `unknown`
 */

function findRepoRootFrom(startDir) {
  const anchor = path.join(
    "docs",
    "specs",
    "engineering-spec",
    "02_Technical_Design",
    "schemas",
    "api_catalog.json",
  );
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

const catalogPath = path.join(
  repoRoot,
  "docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json",
);
const outDir = path.join(packageRoot, "src/generated");

function toCamelCase(input) {
  return input
    .split(/[-_ ]+/g)
    .filter(Boolean)
    .map((p, idx) => {
      const s = String(p);
      if (idx === 0) return s.charAt(0).toLowerCase() + s.slice(1);
      return s.charAt(0).toUpperCase() + s.slice(1);
    })
    .join("");
}

function snakeToCamel(input) {
  return String(input)
    .split("_")
    .filter(Boolean)
    .map((p, idx) => {
      if (idx === 0) return p.charAt(0).toLowerCase() + p.slice(1);
      return p.charAt(0).toUpperCase() + p.slice(1);
    })
    .join("");
}

function safeIdentifier(name) {
  const cleaned = String(name).replace(/[^a-zA-Z0-9_$]/g, "_");
  return /^[0-9]/.test(cleaned) ? `_${cleaned}` : cleaned;
}

function normalizeRequired(value) {
  const v = String(value ?? "").trim();
  return v === "是" || v.toLowerCase() === "y" || v.toLowerCase() === "yes" || v === "true";
}

function mapDocTypeToZod(typeText) {
  const t = String(typeText ?? "")
    .trim()
    .toLowerCase();
  if (!t) return "z.unknown()";
  if (t.includes("string")) return "z.string()";
  if (
    t.includes("int") ||
    t.includes("integer") ||
    t.includes("long") ||
    t.includes("double") ||
    t.includes("float")
  )
    return "z.number()";
  if (t.includes("boolean") || t.includes("bool")) return "z.boolean()";
  if (t.includes("array") || t.includes("list") || t.includes("jsonarray"))
    return "z.array(z.unknown())";
  if (t.includes("object") || t.includes("jsonobject") || t.includes("map"))
    return "z.record(z.unknown())";
  return "z.unknown()";
}

function mapDocTypeToTs(typeText) {
  const t = String(typeText ?? "")
    .trim()
    .toLowerCase();
  if (!t) return "unknown";
  if (t.includes("string")) return "string";
  if (
    t.includes("int") ||
    t.includes("integer") ||
    t.includes("long") ||
    t.includes("double") ||
    t.includes("float")
  )
    return "number";
  if (t.includes("boolean") || t.includes("bool")) return "boolean";
  if (t.includes("array") || t.includes("list") || t.includes("jsonarray")) return "unknown[]";
  if (t.includes("object") || t.includes("jsonobject") || t.includes("map"))
    return "Record<string, unknown>";
  return "unknown";
}

function inferRetryCategory(entry) {
  const title = String(entry.title ?? "");
  const pathText = String(entry.path ?? "");
  if (String(entry.method).toUpperCase() === "GET") return "safe";
  if (/^\/(get|query|download|init)/i.test(pathText)) return "safe";
  if (/(获取|查询|下载|初始化)/.test(title)) return "safe";
  return "side_effect";
}

function normalizeParamRow(row) {
  const name = row["参数名"] ?? row["参数"] ?? row["字段"] ?? row.name;
  const required = row["必选"] ?? row["必填"] ?? row.required;
  const type = row["类型"] ?? row["数据类型"] ?? row.type;
  const desc = row["说明"] ?? row["描述"] ?? row.desc;
  return {
    name: String(name ?? "").trim(),
    required: normalizeRequired(required),
    type: String(type ?? "").trim(),
    desc: String(desc ?? "").trim(),
  };
}

function chooseMethodName(entry) {
  const p = String(entry.path ?? "").trim();
  if (p) {
    const segments = p
      .split("/")
      .filter(Boolean)
      .map((s) => s.replace(/[^a-zA-Z0-9_]+/g, "_"))
      .filter(Boolean);
    if (segments.length) return toCamelCase(segments.join("_"));
  }

  const modulePrefix = String(entry.module ?? "").replace(/-/g, "_");
  const prefix = modulePrefix ? `${modulePrefix}_` : "";
  const op = String(entry.operationId);
  const rest = prefix && op.startsWith(prefix) ? op.slice(prefix.length) : op;
  return snakeToCamel(rest);
}

async function main() {
  const raw = JSON.parse(await fs.readFile(catalogPath, "utf8"));
  const catalog = raw.catalog ?? [];
  const endpoints = catalog.filter((e) => e.kind === "endpoint").slice();
  endpoints.sort((a, b) => {
    const ma = String(a.module ?? "");
    const mb = String(b.module ?? "");
    if (ma !== mb) return ma.localeCompare(mb);
    return String(a.operationId).localeCompare(String(b.operationId));
  });

  await fs.mkdir(outDir, { recursive: true });

  const endpointDefs = endpoints.map((e) => {
    const requiresAuth = Array.isArray(e.headers)
      ? e.headers.some((h) => String(h.name ?? "").toLowerCase() === "authorization")
      : true;
    const params = Array.isArray(e.params)
      ? e.params.map(normalizeParamRow).filter((p) => p.name)
      : [];
    return {
      operationId: e.operationId,
      title: e.title,
      module: e.module,
      method: e.method,
      path: e.path,
      doc: e.doc,
      requiresAuth,
      retryCategory: inferRetryCategory(e),
      params,
    };
  });

  const endpointsTs = `/* eslint-disable */
// @generated by tools/generate_sdk.mjs - DO NOT EDIT

export type RetryCategory = "safe" | "side_effect";

export type EndpointDef = {
  operationId: string;
  title: string;
  module: string;
  method: string;
  path: string;
  doc: string;
  requiresAuth: boolean;
  retryCategory: RetryCategory;
  params: Array<{ name: string; required: boolean; type: string; desc: string }>;
};

export const endpointDefs: ReadonlyArray<EndpointDef> = ${JSON.stringify(endpointDefs, null, 2)} as const;
`;

  const validatorsLines = [];
  const typesLines = [];
  for (const def of endpointDefs) {
    const typeName = safeIdentifier(`Params_${def.operationId}`);
    const fields = def.params
      .map((p) => {
        const tsType = mapDocTypeToTs(p.type);
        const optional = p.required ? "" : "?";
        const doc = p.desc ? `/** ${p.desc} */\n  ` : "";
        return `${doc}${JSON.stringify(p.name)}${optional}: ${tsType};`;
      })
      .join("\n  ");

    typesLines.push(
      `export type ${typeName} = {\n  ${fields || ""}\n  [k: string]: unknown;\n};\n`,
    );

    const zodShape = def.params
      .filter((p) => p.name)
      .map((p) => {
        const base = mapDocTypeToZod(p.type);
        const zod = p.required ? base : `${base}.optional()`;
        return `  ${JSON.stringify(p.name)}: ${zod},`;
      })
      .join("\n");

    validatorsLines.push(
      `  ${JSON.stringify(def.operationId)}: z.object({\n${zodShape}\n  }).passthrough(),`,
    );
  }

  const validatorsTs = `/* eslint-disable */
// @generated by tools/generate_sdk.mjs - DO NOT EDIT

import { z } from "zod";

export const validators = {
${validatorsLines.join("\n")}
} as const;
`;

  const manifestTs = `/* eslint-disable */
// @generated by tools/generate_sdk.mjs - DO NOT EDIT

export const operationIds = ${JSON.stringify(
    endpointDefs.map((d) => d.operationId),
    null,
    2,
  )} as const;
export type OperationId = (typeof operationIds)[number];
`;

  // modules + api tree
  const modules = new Map();
  for (const def of endpointDefs) {
    const moduleKey = safeIdentifier(toCamelCase(def.module));
    const methodName = safeIdentifier(chooseMethodName(def));
    if (!modules.has(moduleKey)) modules.set(moduleKey, []);
    modules.get(moduleKey).push({ def, methodName });
  }

  // collision handling (same moduleKey + methodName)
  for (const [moduleKey, items] of modules.entries()) {
    const used = new Map();
    for (const item of items) {
      const current = used.get(item.methodName) ?? 0;
      used.set(item.methodName, current + 1);
    }
    for (const item of items) {
      if ((used.get(item.methodName) ?? 0) > 1) {
        item.methodName = safeIdentifier(snakeToCamel(item.def.operationId));
      }
    }
  }

  const apiModuleBlocks = [];
  for (const [moduleKey, items] of [...modules.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const methodBlocks = items
      .sort((a, b) => a.def.operationId.localeCompare(b.def.operationId))
      .map(({ def, methodName }) => {
        const paramsTypeName = safeIdentifier(`Params_${def.operationId}`);
        return `      /**
       * ${def.title}
       *
       * - method: ${def.method}
       * - path: ${def.path}
       * - doc: ${def.doc}
       */
      ${methodName}: async (params, options) => {
        const parsed = validators[${JSON.stringify(def.operationId)}].safeParse(params ?? {});
        if (!parsed.success) {
          const rid = options?.requestId ?? \`validation_\${Date.now()}\`;
          const issues = parsed.error.issues
            .slice(0, 5)
            .map((i) => \`\${i.path.join(".") || "<root>"}: \${i.message}\`)
            .join("; ");
          throw new WkteamValidationError(\`参数校验失败: \${issues}\`, {
            requestId: rid,
            operationId: ${JSON.stringify(def.operationId)},
          });
        }
        return client.call({
          operationId: ${JSON.stringify(def.operationId)},
          method: ${JSON.stringify(def.method)},
          path: ${JSON.stringify(def.path)},
          params: parsed.data,
          requiresAuth: ${def.requiresAuth ? "true" : "false"},
          retryCategory: ${JSON.stringify(def.retryCategory)},
          options,
        });
      },`;
      })
      .join("\n\n");

    apiModuleBlocks.push(`    ${moduleKey}: {\n${methodBlocks}\n    },`);
  }

  const apiTypeBlocks = [];
  const operationIndex = {};
  for (const [moduleKey, items] of [...modules.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const methodsType = items
      .sort((a, b) => a.def.operationId.localeCompare(b.def.operationId))
      .map(({ def, methodName }) => {
        const paramsTypeName = safeIdentifier(`Params_${def.operationId}`);
        operationIndex[def.operationId] = { moduleKey, methodName };
        return `      ${methodName}: (params: ${paramsTypeName}, options?: EndpointCallOptions) => Promise<unknown>;`;
      })
      .join("\n");
    apiTypeBlocks.push(`  ${moduleKey}: {\n${methodsType}\n  };`);
  }

  const apiTs = `/* eslint-disable */
// @generated by tools/generate_sdk.mjs - DO NOT EDIT

import type { EndpointCallOptions } from "../sdk/config.js";
import { WkteamValidationError } from "../sdk/errors.js";
import type { WkteamCoreClient } from "../sdk/core-client.js";
import { validators } from "./validators.js";

${typesLines.join("\n")}

export type WkteamApi = {
${apiTypeBlocks.join("\n")}
};

export function createApi(client: WkteamCoreClient): WkteamApi {
  return {
${apiModuleBlocks.join("\n")}
  };
}
`;

  await fs.writeFile(path.join(outDir, "endpoints.ts"), endpointsTs, "utf8");
  await fs.writeFile(path.join(outDir, "validators.ts"), validatorsTs, "utf8");
  await fs.writeFile(path.join(outDir, "manifest.ts"), manifestTs, "utf8");
  await fs.writeFile(path.join(outDir, "api.ts"), apiTs, "utf8");
  await fs.writeFile(
    path.join(outDir, "operation-index.ts"),
    `/* eslint-disable */
// @generated by tools/generate_sdk.mjs - DO NOT EDIT

export const operationIndex = ${JSON.stringify(operationIndex, null, 2)} as const;
`,
    "utf8",
  );

  console.log(`Wrote generated SDK files to: ${path.relative(packageRoot, outDir)}`);
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
