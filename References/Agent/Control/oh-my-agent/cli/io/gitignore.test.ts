import { execFileSync } from "node:child_process";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  ensureGitignored,
  isGitRepo,
  isInIgnoredSet,
  isPathGitIgnored,
  listGitIgnoredPaths,
} from "./gitignore.js";

function makeRepo(prefix: string): string {
  const dir = mkdtempSync(join(tmpdir(), prefix));
  execFileSync("git", ["init", "--quiet", "-b", "main"], {
    cwd: dir,
    stdio: ["ignore", "ignore", "ignore"],
  });
  return dir;
}

describe("isGitRepo", () => {
  let repo: string;
  let plain: string;

  beforeEach(() => {
    repo = makeRepo("oma-gitignore-isrepo-");
    plain = mkdtempSync(join(tmpdir(), "oma-gitignore-plain-"));
  });

  afterEach(() => {
    rmSync(repo, { recursive: true, force: true });
    rmSync(plain, { recursive: true, force: true });
  });

  it("returns true inside a git work tree", () => {
    expect(isGitRepo(repo)).toBe(true);
  });

  it("returns false in a plain directory", () => {
    expect(isGitRepo(plain)).toBe(false);
  });
});

describe("ensureGitignored", () => {
  let repo: string;

  beforeEach(() => {
    repo = makeRepo("oma-gitignore-ensure-");
  });

  afterEach(() => {
    rmSync(repo, { recursive: true, force: true });
  });

  it("creates .gitignore when missing and writes the patterns", () => {
    const result = ensureGitignored(repo, ["docs/generated/"]);

    expect(result.skipped).toBe(false);
    expect(result.added).toEqual(["docs/generated/"]);
    expect(result.alreadyPresent).toEqual([]);

    const content = readFileSync(join(repo, ".gitignore"), "utf-8");
    expect(content).toContain("docs/generated/");
  });

  it("appends patterns when .gitignore already exists", () => {
    writeFileSync(join(repo, ".gitignore"), "node_modules\n");

    const result = ensureGitignored(repo, ["docs/generated/"]);

    expect(result.added).toEqual(["docs/generated/"]);
    const content = readFileSync(join(repo, ".gitignore"), "utf-8");
    expect(content).toContain("node_modules");
    expect(content).toContain("docs/generated/");
  });

  it("does not duplicate exact-match patterns", () => {
    writeFileSync(join(repo, ".gitignore"), "docs/generated/\n");

    const result = ensureGitignored(repo, ["docs/generated/"]);

    expect(result.added).toEqual([]);
    expect(result.alreadyPresent).toEqual(["docs/generated/"]);

    const content = readFileSync(join(repo, ".gitignore"), "utf-8");
    expect(content.match(/docs\/generated\//g)?.length).toBe(1);
  });

  it("ignores comments and blanks when checking for duplicates", () => {
    writeFileSync(
      join(repo, ".gitignore"),
      "# generated artifacts\n\ndocs/generated/\n",
    );

    const result = ensureGitignored(repo, ["docs/generated/"]);
    expect(result.added).toEqual([]);
    expect(result.alreadyPresent).toEqual(["docs/generated/"]);
  });

  it("writes header once and skips it on the second run", () => {
    const opts = { header: "# oma docs generated" };

    const first = ensureGitignored(repo, ["docs/generated/"], opts);
    expect(first.added).toEqual(["docs/generated/"]);

    const second = ensureGitignored(repo, ["other/path/"], opts);
    expect(second.added).toEqual(["other/path/"]);

    const content = readFileSync(join(repo, ".gitignore"), "utf-8");
    expect(content.match(/# oma docs generated/g)?.length).toBe(1);
    expect(content).toContain("docs/generated/");
    expect(content).toContain("other/path/");
  });

  it("normalises missing trailing newline before appending", () => {
    writeFileSync(join(repo, ".gitignore"), "node_modules");

    ensureGitignored(repo, ["docs/generated/"]);

    const content = readFileSync(join(repo, ".gitignore"), "utf-8");
    const lines = content.split("\n");
    expect(lines).toContain("node_modules");
    expect(lines).toContain("docs/generated/");
  });

  it("returns skipped: true outside a git repo", () => {
    const plain = mkdtempSync(join(tmpdir(), "oma-gitignore-noop-"));
    try {
      const result = ensureGitignored(plain, ["docs/generated/"]);
      expect(result).toEqual({
        added: [],
        alreadyPresent: [],
        skipped: true,
      });
    } finally {
      rmSync(plain, { recursive: true, force: true });
    }
  });

  it("treats trimmed patterns as identical to existing ones", () => {
    writeFileSync(join(repo, ".gitignore"), "docs/generated/\n");

    const result = ensureGitignored(repo, ["  docs/generated/  "]);
    expect(result.added).toEqual([]);
    expect(result.alreadyPresent).toEqual(["docs/generated/"]);
  });
});

describe("isPathGitIgnored", () => {
  let repo: string;

  beforeEach(() => {
    repo = makeRepo("oma-gitignore-check-");
    writeFileSync(join(repo, ".gitignore"), "build/\n*.log\n");
    mkdirSync(join(repo, "build"), { recursive: true });
    writeFileSync(join(repo, "build", "out.txt"), "x");
    writeFileSync(join(repo, "app.log"), "y");
    writeFileSync(join(repo, "src.ts"), "z");
  });

  afterEach(() => {
    rmSync(repo, { recursive: true, force: true });
  });

  it("returns true for a path covered by .gitignore", () => {
    expect(isPathGitIgnored(join(repo, "build", "out.txt"), repo)).toBe(true);
    expect(isPathGitIgnored(join(repo, "app.log"), repo)).toBe(true);
  });

  it("returns false for a tracked-eligible path", () => {
    expect(isPathGitIgnored(join(repo, "src.ts"), repo)).toBe(false);
  });

  it("returns false outside a git repo", () => {
    const plain = mkdtempSync(join(tmpdir(), "oma-gitignore-plain-"));
    try {
      expect(isPathGitIgnored(join(plain, "anything.log"), plain)).toBe(false);
    } finally {
      rmSync(plain, { recursive: true, force: true });
    }
  });
});

describe("listGitIgnoredPaths + isInIgnoredSet", () => {
  let repo: string;

  beforeEach(() => {
    repo = makeRepo("oma-gitignore-list-");
    writeFileSync(join(repo, ".gitignore"), "build/\n*.log\n");
    mkdirSync(join(repo, "build"), { recursive: true });
    writeFileSync(join(repo, "build", "out.txt"), "x");
    writeFileSync(join(repo, "build", "nested.log"), "x");
    writeFileSync(join(repo, "root.log"), "y");
    writeFileSync(join(repo, "src.ts"), "z");
  });

  afterEach(() => {
    rmSync(repo, { recursive: true, force: true });
  });

  it("collects ignored entries with absolute paths", () => {
    const set = listGitIgnoredPaths(repo);

    expect(isInIgnoredSet(join(repo, "root.log"), set)).toBe(true);
    expect(isInIgnoredSet(join(repo, "build", "out.txt"), set)).toBe(true);
    expect(isInIgnoredSet(join(repo, "src.ts"), set)).toBe(false);
  });

  it("returns an empty Set outside a git repo", () => {
    const plain = mkdtempSync(join(tmpdir(), "oma-gitignore-list-noop-"));
    try {
      expect(listGitIgnoredPaths(plain).size).toBe(0);
    } finally {
      rmSync(plain, { recursive: true, force: true });
    }
  });
});
