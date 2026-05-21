# wkteam-api-sdk（TypeScript / Node.js）

本目录交付 `wkteam api-wen-dang2` 的 **TypeScript SDK**（Node.js 优先）。

权威输入：
- 离线 API 文档：`docs/api/api-wen-dang2/`
- catalog：`docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`

SDK 目标：接口全覆盖（当前 127 endpoints）、可离线回归、可配置鉴权/超时/重试/并发限制、日志脱敏与 hook。

## 安装（开发态）

在仓库根目录执行：

```bash
cd src/typescript-sdk
npm i
```

## 使用示例

```ts
import { createClient } from "wkteam-api-sdk";

const client = createClient({
  baseUrl: "https://你的域名或网关前缀",
  authorization: "你的 Authorization（平台登录返回）",
  // authorizationPrefix: "Bearer ", // 如果平台需要前缀才打开
});

const result = await client.api.dengLu.memberLogin({
  account: "xxx",
  password: "xxx",
});
console.log(result);
```

## 开发命令

在 `src/typescript-sdk/` 目录执行：

```bash
# 从离线文档生成 catalog + API_SPEC（维护文档用）
npm run generate:api

# 从 catalog 生成 SDK 的 src/generated（实现依赖）
npm run generate:sdk

# 离线回归（必须）
npm test

# 构建产物（ESM/CJS/types）
npm run build
```
