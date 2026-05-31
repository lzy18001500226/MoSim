import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  // Playwright fixture files use a `use()` callback that the React Hooks
  // plugin mistakes for React 19's `use()` hook. The naming collision is
  // in Playwright's public API, not something we can rename in our code.
  {
    files: ["e2e-playwright/**/*.ts", "e2e/**/*.ts"],
    rules: {
      "react-hooks/rules-of-hooks": "off",
    },
  },
  // (auth) route group is wasm-zero by design — the whole point of the
  // light-auth rollout is keeping 40MB of wasm off the critical path to
  // /login. Wasm helpers may sneak back in via the dashboard's import
  // graph; this rule fails CI before the regression lands.
  {
    files: ["src/app/(auth)/**/*.ts", "src/app/(auth)/**/*.tsx"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          paths: [
            { name: "@/lib/wasm-core", message: "(auth) routes must stay wasm-zero. Use @/lib/light-auth instead." },
            { name: "@/lib/wasm-getters", message: "(auth) routes must stay wasm-zero. Use @/lib/light-auth instead." },
            { name: "@/stores/auth", message: "(auth) routes must stay wasm-zero. Use useLightSession + @/lib/light-auth instead." },
            { name: "@/providers/WasmProvider", message: "(auth) routes must stay wasm-zero." },
            { name: "@/components/auth/AuthBootstrap", message: "(auth) routes must stay wasm-zero." },
            { name: "agentsmesh-wasm", message: "(auth) routes must stay wasm-zero." },
            { name: "@agentsmesh/service-runtime", message: "(auth) routes must stay wasm-zero." },
          ],
        },
      ],
    },
  },
  // Business code (components / stores / hooks) must not deep-import Connect
  // adapters or wire-shape converters — those are internal to the facade
  // layer. Going through @/lib/api or @/lib/api/facade keeps the proto types
  // contained so we can swap the wire (e.g. Connect → REST fallback) without
  // touching call sites.
  //
  // Phase 10 baseline cleanup complete (2026-05-24): all 53 pre-existing
  // direct-Connect imports under components/stores/hooks rewritten to use
  // facade siblings. Rule flipped to "error" to prevent regressions.
  {
    files: [
      "src/components/**/*.ts",
      "src/components/**/*.tsx",
      "src/stores/**/*.ts",
      "src/stores/**/*.tsx",
      "src/hooks/**/*.ts",
      "src/hooks/**/*.tsx",
    ],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["@/lib/api/connect/*"],
              message: "Business code must go through the facade — use `@/lib/api` barrel or `@/lib/api/facade/*` instead of importing Connect adapters directly.",
            },
            {
              group: ["@/lib/api/shapes/*"],
              message: "Wire shape converters are internal to the facade layer — use `@/lib/api` barrel or `@/lib/api/facade/*` instead.",
            },
            {
              group: [
                "**/credentialForms/e2e-echo",
                "**/credentialForms/e2e-echo.ts",
              ],
              message:
                "e2e-echo is a test-only credential form. Production code must not import it directly — the form is registered conditionally via `require()` inside credentialForms/index.ts gated on NEXT_PUBLIC_E2E. See ADR 2026-05-26-test-fixture-isolation.",
            },
          ],
        },
      ],
    },
  },
]);

export default eslintConfig;
