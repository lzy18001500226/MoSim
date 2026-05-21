# Tools

## `generate_api_artifacts.mjs`

从 `docs/api/api-wen-dang2/**/*.md` 自动提取 endpoint 信息，生成：

- `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`
- `docs/specs/engineering-spec/00_Overview/API_DOC_COVERAGE.generated.md`
- `docs/specs/engineering-spec/02_Technical_Design/API_SPEC.md`

运行：

```bash
cd src/typescript-sdk
npm run generate:api
```

## `generate_sdk.mjs`

从 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json` 生成 SDK 的 `src/generated/**`（全量 127 endpoint wrapper、参数校验器、manifest 等）。

生成：
- `src/generated/endpoints.ts`
- `src/generated/validators.ts`
- `src/generated/manifest.ts`
- `src/generated/operation-index.ts`
- `src/generated/api.ts`

运行：

```bash
cd src/typescript-sdk
npm run generate:sdk
```
