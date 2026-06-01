import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // setupFiles: "./test/setup.ts",
    globals: true, // 使测试环境支持 `describe`, `it`, `expect` 等全局函数
    environment: "node", // 使用 Node 环境进行测试
  },
});
