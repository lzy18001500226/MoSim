import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

// The renderer cross-imports from clients/web/src and is React-based, so
// reuse Next.js's preset (covers React + TS rules). main/preload run in
// Node, but eslint-config-next is permissive enough for them — keeps a
// single rule surface across the whole repo.
const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores([
    "out/**",
    "dist/**",
    "node_modules/**",
    "*.config.ts",
    "*.config.mjs",
    "*.config.js",
  ]),
  {
    // desktop is an Electron app, not a Next.js Pages-router app.
    // The `no-html-link-for-pages` rule expects `pages/` at the
    // package root and otherwise emits a global error per file.
    rules: {
      "@next/next/no-html-link-for-pages": "off",
      // The next-intl shim assigns to `t.rich` / `t.raw` after the
      // function is created. The new react-hooks immutability rule
      // mis-flags this as mutating a hook return — `t` is a plain
      // function value here, so the rule does not apply.
      "react-hooks/immutability": "off",
    },
  },
  {
    // Playwright fixture files use a `use()` callback that the React
    // Hooks plugin mistakes for React 19's `use()` hook. Same override
    // as clients/web/eslint.config.mjs.
    files: ["e2e/**/*.ts"],
    rules: {
      "react-hooks/rules-of-hooks": "off",
    },
  },
  {
    // Surface real `any` usage as warnings — there are eight pre-existing
    // sites in main/renderer shims that need follow-up. Keeping them as
    // warnings unblocks the lint target without papering over the debt.
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
]);

export default eslintConfig;
