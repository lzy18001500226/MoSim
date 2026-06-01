import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  detectI18nDrift,
  type I18nDriftPair,
  summarizeDrift,
} from "./i18n-drift.js";

function mkrepo(): string {
  const root = mkdtempSync(join(tmpdir(), "oma-i18n-drift-"));
  return root;
}

function writeFile(root: string, rel: string, content: string): void {
  const abs = join(root, rel);
  mkdirSync(join(abs, ".."), { recursive: true });
  writeFileSync(abs, content);
}

describe("detectI18nDrift", () => {
  it("returns empty when no docs exist", () => {
    const root = mkrepo();
    try {
      const pairs = detectI18nDrift({ repoRoot: root });
      expect(pairs).toEqual([]);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("flags missing translation as CRITICAL", () => {
    const root = mkrepo();
    try {
      writeFile(
        root,
        "web/docs/getting-started.md",
        "# Getting Started\n\nHello.\n",
      );
      // ko locale exists but no translation file
      mkdirSync(
        join(root, "web/i18n/ko/docusaurus-plugin-content-docs/current"),
        { recursive: true },
      );
      const pairs = detectI18nDrift({ repoRoot: root, minSeverity: "LOW" });
      expect(pairs).toHaveLength(1);
      expect(pairs[0]?.severity).toBe("CRITICAL");
      expect(pairs[0]?.tgtLines).toBe(-1);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("flags large line drift as HIGH", () => {
    const root = mkrepo();
    try {
      const enContent = `# T\n\n${"line\n".repeat(100)}`;
      const koContent = `# T\n\nline\n`;
      writeFile(root, "web/docs/a.md", enContent);
      writeFile(
        root,
        "web/i18n/ko/docusaurus-plugin-content-docs/current/a.md",
        koContent,
      );
      const pairs = detectI18nDrift({ repoRoot: root, minSeverity: "LOW" });
      expect(pairs).toHaveLength(1);
      expect(pairs[0]?.severity).toBe("HIGH");
      expect(pairs[0]?.linesDiffPct).toBeGreaterThanOrEqual(15);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("classifies in-sync content as LOW", () => {
    const root = mkrepo();
    try {
      const content = "# Title\n\n## Section\n\nbody.\n";
      writeFile(root, "web/docs/a.md", content);
      writeFile(
        root,
        "web/i18n/ko/docusaurus-plugin-content-docs/current/a.md",
        content,
      );
      const pairs = detectI18nDrift({ repoRoot: root, minSeverity: "LOW" });
      expect(pairs).toHaveLength(1);
      expect(pairs[0]?.severity).toBe("LOW");
      expect(pairs[0]?.linesDiff).toBe(0);
      expect(pairs[0]?.headingCountDiff).toBe(0);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("filters by minSeverity", () => {
    const root = mkrepo();
    try {
      const content = "# Same\n\nbody.\n";
      writeFile(root, "web/docs/a.md", content);
      writeFile(
        root,
        "web/i18n/ko/docusaurus-plugin-content-docs/current/a.md",
        content,
      );
      const pairs = detectI18nDrift({ repoRoot: root, minSeverity: "HIGH" });
      // LOW-severity pair filtered out
      expect(pairs).toHaveLength(0);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("scans nested doc directories", () => {
    const root = mkrepo();
    try {
      writeFile(root, "web/docs/getting-started/install.md", "# Install\n");
      writeFile(root, "web/docs/guide/usage.md", "# Usage\n");
      writeFile(
        root,
        "web/i18n/ko/docusaurus-plugin-content-docs/current/getting-started/install.md",
        "# 설치\n",
      );
      writeFile(
        root,
        "web/i18n/ko/docusaurus-plugin-content-docs/current/guide/usage.md",
        "# 사용\n",
      );
      const pairs = detectI18nDrift({ repoRoot: root, minSeverity: "LOW" });
      expect(pairs).toHaveLength(2);
      expect(pairs.map((p) => p.source).sort()).toEqual([
        "web/docs/getting-started/install.md",
        "web/docs/guide/usage.md",
      ]);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("emits one pair per (doc, locale) combination", () => {
    const root = mkrepo();
    try {
      writeFile(root, "web/docs/a.md", "# A\n");
      writeFile(
        root,
        "web/i18n/ko/docusaurus-plugin-content-docs/current/a.md",
        "# A\n",
      );
      writeFile(
        root,
        "web/i18n/ja/docusaurus-plugin-content-docs/current/a.md",
        "# A\n",
      );
      writeFile(
        root,
        "web/i18n/zh/docusaurus-plugin-content-docs/current/a.md",
        "# A\n",
      );
      const pairs = detectI18nDrift({ repoRoot: root, minSeverity: "LOW" });
      expect(pairs).toHaveLength(3);
      expect(pairs.map((p) => p.lang).sort()).toEqual(["ja", "ko", "zh"]);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("orders pairs by severity descending", () => {
    const root = mkrepo();
    try {
      writeFile(root, "web/docs/big.md", `${"x\n".repeat(100)}`);
      writeFile(root, "web/docs/small.md", "x\n");
      writeFile(
        root,
        "web/i18n/ko/docusaurus-plugin-content-docs/current/big.md",
        "x\n",
      );
      writeFile(
        root,
        "web/i18n/ko/docusaurus-plugin-content-docs/current/small.md",
        "x\n",
      );
      const pairs = detectI18nDrift({ repoRoot: root, minSeverity: "LOW" });
      expect(pairs[0]?.source).toBe("web/docs/big.md");
      expect(pairs[0]?.severity).toBe("HIGH");
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });
});

describe("summarizeDrift", () => {
  it("aggregates by severity", () => {
    const pairs = [
      { severity: "HIGH" },
      { severity: "HIGH" },
      { severity: "MEDIUM" },
      { severity: "LOW" },
    ] as unknown as I18nDriftPair[];
    const s = summarizeDrift(pairs);
    expect(s.total).toBe(4);
    expect(s.bySeverity.HIGH).toBe(2);
    expect(s.bySeverity.MEDIUM).toBe(1);
    expect(s.bySeverity.LOW).toBe(1);
    expect(s.bySeverity.CRITICAL).toBe(0);
  });

  it("limits topPairs to 10", () => {
    const pairs = Array.from({ length: 20 }, () => ({
      severity: "LOW",
    })) as unknown as I18nDriftPair[];
    const s = summarizeDrift(pairs);
    expect(s.topPairs).toHaveLength(10);
  });
});
