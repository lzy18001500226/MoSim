import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const REPOSITORY_URL = "https://github.com/first-fluke/oh-my-agent";
const scriptDir = dirname(fileURLToPath(import.meta.url));
const cliDir = resolve(scriptDir, "..");
const rootReadmePath = resolve(cliDir, "..", "README.md");
const cliReadmePath = resolve(cliDir, "README.md");

function rewriteRelativeMarkdownLinks(markdown) {
  return markdown.replace(
    /(!?\[[^\]]*]\()(\.\/[^)\s]+)(\))/g,
    (_, prefix, target, suffix) => {
      const relativeTarget = target.slice(2);
      const [path, fragment] = relativeTarget.split("#");
      const base = prefix.startsWith("![")
        ? `${REPOSITORY_URL}/raw/main/${path}`
        : `${REPOSITORY_URL}/blob/main/${path}`;
      const nextTarget = fragment ? `${base}#${fragment}` : base;

      return `${prefix}${nextTarget}${suffix}`;
    },
  );
}

const rootReadme = readFileSync(rootReadmePath, "utf-8");
const cliReadme = rewriteRelativeMarkdownLinks(rootReadme);

mkdirSync(dirname(cliReadmePath), { recursive: true });
writeFileSync(cliReadmePath, cliReadme);
