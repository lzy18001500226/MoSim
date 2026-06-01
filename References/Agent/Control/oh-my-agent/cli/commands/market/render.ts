/**
 * `oma market render` — Produce a market research brief from ClusterOutput.
 *
 * Architecture: runRender (CLI) → render (business logic) → LAW self-check → write file
 *
 * LAW execution order (output-laws.md):
 *   1. LAW 8  badge        — prepend if missing (auto-fix)
 *   2. LAW 2  body opener  — verify "What we learned:" (violation if absent)
 *   3. LAW 4  forbidden ## — flag unfixable headers (violation)
 *   4. LAW 6  evidence dump — flag raw cluster pattern (violation)
 *   5. LAW 7  citations    — rewrite bare URLs, unwrap empty links (auto-fix)
 *   6. LAW 3  em-dash      — replace outside code blocks (auto-fix)
 *   7. LAW 1  Sources block — strip trailing sources list (auto-fix)
 *   8. LAW 5  footer       — verify ENGINE FOOTER present (auto-fix if missing)
 */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  renderFrameworkSkeleton,
  resolveFrameworks,
} from "./shared/frameworks.js";
import type { Cluster } from "./shared/schema.js";
import { ClusterOutputSchema } from "./shared/schema.js";
import { cleanSnippet } from "./shared/text.js";

// ---------------------------------------------------------------------------
// Module-scope constants
// ---------------------------------------------------------------------------

const __filename = fileURLToPath(import.meta.url);
const PKG_JSON_PATH = join(__filename, "../../../package.json");

let _cachedVersion: string | undefined;

function getPackageVersion(): string {
  if (_cachedVersion !== undefined) return _cachedVersion;
  try {
    const raw = readFileSync(PKG_JSON_PATH, "utf8");
    const pkg = JSON.parse(raw) as { version?: string };
    _cachedVersion = pkg.version ?? "0.0.0";
  } catch {
    _cachedVersion = "0.0.0";
  }
  return _cachedVersion;
}

const DEFAULT_OUTPUT_DIR = ".agents/results/market/";

// Allowed ## headers for COMPARISON layout
const COMPARISON_ALLOWED_HEADERS = new Set([
  "Quick Verdict",
  "Head-to-Head",
  "The Bottom Line",
]);

// Allowed ## headers for framework sections + cluster bank
const FRAMEWORK_HEADERS = new Set([
  "SWOT",
  "Strengths",
  "Weaknesses",
  "Opportunities",
  "Threats",
  "Porter's 5 Forces",
  "PESTEL",
  "Cluster Bank",
]);

// `### C1`, `### C2` ... cluster-bank IDs are also allowed structurally.
const CLUSTER_ID_HEADER_RE = /^C\d+\b/;

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface RenderOptions {
  topic: string;
  intent: "pain" | "trend" | "competitor" | "discovery";
  format?: "md" | "json";
  frameworks?: "auto" | "none" | string;
  vs?: string | null;
  minTrust?: "verified" | "community" | "external";
  selfCheck?: boolean;
  outputDir?: string;
  nowMs?: number;
  version?: string;
  sourcesUsed?: string[];
  sourcesFailed?: string[];
  cacheHit?: boolean;
  latencyMs?: number;
}

export interface RenderResult {
  markdown: string;
  outputPath: string;
  selfCheckPassed: boolean;
  violations: string[];
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function slugify(text: string): string {
  // Lowercase, replace non-alphanumeric and non-Korean with hyphen
  const slug = text
    .toLowerCase()
    .replace(/[^\w가-힣가-힣]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
  return slug.slice(0, 60);
}

function utcDate(nowMs: number): string {
  const d = new Date(nowMs);
  const yyyy = d.getUTCFullYear();
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function utcDateCompact(nowMs: number): string {
  return utcDate(nowMs).replace(/-/g, "");
}

function isComparisonIntent(opts: RenderOptions): boolean {
  if (opts.intent === "competitor") return true;
  if (opts.vs != null && opts.vs.trim().length > 0) return true;
  // require " vs " / " versus " surrounded by whitespace, avoiding "VS Code"
  // and similar prefixed brand names.
  if (/\s+vs\.?\s+|\s+versus\s+/i.test(opts.topic)) return true;
  return false;
}

function extractVsEntities(
  topic: string,
  vs: string | null | undefined,
): [string, string] {
  // entity A and B for COMPARISON layout
  const vsMatch = /^(.+?)\s+(?:vs\.?|versus)\s+(.+)$/i.exec(topic);
  if (vsMatch?.[1] != null && vsMatch[2] != null) {
    return [vsMatch[1].trim(), vsMatch[2].trim()];
  }
  if (vs != null && vs.trim().length > 0) {
    return [topic, vs.trim()];
  }
  return [topic, "Competitor"];
}

// ---------------------------------------------------------------------------
// Body builders
// ---------------------------------------------------------------------------

/**
 * Build a human-readable lead-in from a cluster's primary representative.
 *
 * Prefer the first sentence of the title (truncated), falling back to a
 * compact slice of the snippet. Strip markdown control chars and entity
 * artefacts. Caps roughly at 80 chars for English / 40 for Korean (no
 * spaces — count syllables more conservatively).
 */
function makeLeadIn(cluster: Cluster, intent: string): string {
  const rep = cluster.representatives[0];
  const fallback = intent === "pain" ? "Notable signal" : "Recent activity";
  const raw = cleanSnippet(rep?.title ?? rep?.snippet ?? "");
  if (!raw) return fallback;

  // First sentence (or first clause if no period)
  const firstSentence = raw.split(/(?<=[.!?。!?])\s/)[0] ?? raw;
  const containsHangul = /[가-힣]/.test(firstSentence);
  const maxChars = containsHangul ? 40 : 80;

  let trimmed = firstSentence.slice(0, maxChars);
  if (firstSentence.length > maxChars) trimmed += "…";
  return trimmed;
}

function buildPainTrendBody(clusters: Cluster[], intent: string): string {
  const lines: string[] = [];
  lines.push("What we learned:\n");

  // Top clusters by rrf_score descending
  const sorted = [...clusters].sort((a, b) => {
    const aScore = a.representatives[0]?.rrf_score ?? 0;
    const bScore = b.representatives[0]?.rrf_score ?? 0;
    return bScore - aScore;
  });

  const topClusters = sorted.slice(0, 5);

  for (const cluster of topClusters) {
    const reps = cluster.representatives.slice(0, 3);
    const leadIn = makeLeadIn(cluster, intent);
    const citations = reps
      .map((r) => {
        const label = cleanSnippet(r.author ?? r.title ?? r.source);
        return `[${label}](${r.url})`;
      })
      .join(", ");
    const snippetSource = reps[0]?.snippet ?? reps[0]?.body ?? reps[0]?.title;
    const snippet = cleanSnippet(snippetSource).slice(0, 280);
    lines.push(`**${leadIn}** ${snippet} - cited by ${citations}.\n`);
  }

  lines.push("\nKEY PATTERNS from the research:\n");

  const patternClusters = sorted.slice(0, 7);
  patternClusters.forEach((cluster, i) => {
    const rep = cluster.representatives[0];
    if (!rep) return;
    const title = makeLeadIn(cluster, intent);
    const summary = cleanSnippet(rep.snippet ?? rep.body ?? rep.title).slice(
      0,
      220,
    );
    lines.push(`${i + 1}. ${title} - ${summary} ([source](${rep.url}))`);
  });

  lines.push("");
  return lines.join("\n");
}

function buildComparisonBody(
  clusters: Cluster[],
  entityA: string,
  entityB: string,
): string {
  const lines: string[] = [];

  lines.push(`# ${entityA} vs ${entityB}: 시장 신호\n`);
  lines.push("## Quick Verdict\n");

  const topRep = clusters[0]?.representatives[0];
  const verdictRaw =
    topRep?.snippet ??
    topRep?.title ??
    "신호 수집 중 - 더 많은 데이터가 필요합니다.";
  lines.push(`${cleanSnippet(verdictRaw)}\n`);

  // Filter clusters per entity by metadata label or split half-half
  const aLabel = `vs-entity:${entityA}`;
  const bLabel = `vs-entity:${entityB}`;

  const aClusters = clusters.filter((c) =>
    c.representatives.some((r) => (r.metadata?.labels ?? []).includes(aLabel)),
  );
  const bClusters = clusters.filter((c) =>
    c.representatives.some((r) => (r.metadata?.labels ?? []).includes(bLabel)),
  );

  // Fallback: split half-half if no label-based filtering
  const useLabels = aClusters.length > 0 || bClusters.length > 0;
  const half = Math.ceil(clusters.length / 2);
  const clusterA = useLabels ? aClusters : clusters.slice(0, half);
  const clusterB = useLabels ? bClusters : clusters.slice(half);

  const renderEntitySection = (name: string, entityClusters: Cluster[]) => {
    lines.push(`## ${name}\n`);
    const top = entityClusters.slice(0, 4);
    for (const c of top) {
      const reps = c.representatives.slice(0, 2);
      const leadIn = makeLeadIn(c, "competitor");
      const citations = reps
        .map(
          (r) => `[${cleanSnippet(r.author ?? r.title ?? r.source)}](${r.url})`,
        )
        .join(", ");
      const snippet = cleanSnippet(
        reps[0]?.snippet ?? reps[0]?.body ?? reps[0]?.title,
      ).slice(0, 280);
      lines.push(`**${leadIn}** ${snippet} - ${citations}.\n`);
    }
    if (top.length === 0) {
      lines.push("_(no signal)_\n");
    }
  };

  renderEntitySection(entityA, clusterA);
  renderEntitySection(entityB, clusterB);

  lines.push("## Head-to-Head\n");
  // Summarize comparing both
  const aSignals = clusterA.flatMap((c) => c.entity_signature).slice(0, 4);
  const bSignals = clusterB.flatMap((c) => c.entity_signature).slice(0, 4);
  lines.push(`${entityA}: ${aSignals.join(", ") || "_(signals emerging)_"}\n`);
  lines.push(`${entityB}: ${bSignals.join(", ") || "_(signals emerging)_"}\n`);

  lines.push("## The Bottom Line\n");
  const count = clusters.length;
  lines.push(
    `Analysis based on ${count} cluster${count !== 1 ? "s" : ""} across sources.\n`,
  );

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Cluster Bank builder — raw evidence dump for analyst (host LLM)
// ---------------------------------------------------------------------------

/**
 * Cluster Bank: every cluster, sorted by (cross_source_count, member count,
 * top rrf_score), with each representative's [name](url) + short snippet.
 *
 * Purpose: give the host LLM filling SWOT/5F/PESTEL slots a citation-ready
 * material list. The bank never claims any quadrant assignment.
 */
function buildClusterBank(clusters: Cluster[]): string {
  if (clusters.length === 0) {
    return "## Cluster Bank\n\n_(corpus too thin — no clusters)_\n";
  }
  const sorted = [...clusters].sort((a, b) => {
    if (b.cross_source_count !== a.cross_source_count) {
      return b.cross_source_count - a.cross_source_count;
    }
    if (b.members.length !== a.members.length) {
      return b.members.length - a.members.length;
    }
    const aScore = a.representatives[0]?.rrf_score ?? 0;
    const bScore = b.representatives[0]?.rrf_score ?? 0;
    return bScore - aScore;
  });

  const lines: string[] = [
    "## Cluster Bank",
    "",
    "> Raw evidence for the analyst. Use these clusters when filling any " +
      "framework section below. Cite as `[name](url)`.",
    "",
  ];
  sorted.forEach((c, i) => {
    const id = `C${i + 1}`;
    const ts =
      c.cross_source_count === 1
        ? "1 source"
        : `${c.cross_source_count} sources`;
    const ms = `${c.members.length} member${c.members.length === 1 ? "" : "s"}`;
    lines.push(`### ${id} - ${ts}, ${ms}`);
    const reps = c.representatives.slice(0, 3);
    if (reps.length === 0) {
      lines.push("- _(no representatives)_");
    } else {
      for (const rep of reps) {
        const label = cleanSnippet(rep.author ?? rep.title ?? rep.source).slice(
          0,
          60,
        );
        const url = rep.url;
        const snippet = cleanSnippet(
          rep.snippet ?? rep.body ?? rep.title,
        ).slice(0, 200);
        const tail = snippet ? ` - ${snippet}` : "";
        lines.push(`- [${label}](${url})${tail}`);
      }
    }
    lines.push("");
  });
  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Engine footer builder
// ---------------------------------------------------------------------------

function buildFooter(clusters: Cluster[], opts: RenderOptions): string {
  const sourcesUsed = opts.sourcesUsed ?? [];
  const sourcesFailed = opts.sourcesFailed ?? [];
  const totalItems = clusters.reduce(
    (n, c) => n + c.members.length + c.representatives.length,
    0,
  );
  const N = sourcesUsed.length + sourcesFailed.length;

  return [
    "<!-- ENGINE FOOTER -->",
    "---",
    `✅ market research footer:`,
    `  - sources used: ${sourcesUsed.join(", ")} (${sourcesUsed.length}/${N} requested)`,
    `  - sources failed: ${sourcesFailed.length ? sourcesFailed.join(", ") : "none"}`,
    `  - clusters: ${clusters.length}`,
    `  - items: ${totalItems}`,
    `  - cache: ${opts.cacheHit ? "hit" : "miss"}`,
    `  - latency: ${opts.latencyMs ?? 0}ms`,
    "---",
    "<!-- END ENGINE FOOTER -->",
  ].join("\n");
}

// ---------------------------------------------------------------------------
// LAW self-check helpers
// ---------------------------------------------------------------------------

const BADGE_RE = /^🔎 oma-market v[\w.-]+ · synced \d{4}-\d{2}-\d{2}$/;

function applyLaw3EmDash(text: string): string {
  // Replace em-dash and en-dash outside code blocks
  // Split on fenced code blocks and process only non-code parts
  const segments = text.split(/(```[\s\S]*?```|`[^`]*`)/g);
  return segments
    .map((seg, i) => {
      if (i % 2 === 1) return seg; // code block — skip
      return seg.replace(/\s+[—–]\s+/g, " - ").replace(/[—–]/g, "-");
    })
    .join("");
}

function applyLaw7Citations(text: string): string {
  // Split on fenced code blocks and process only non-code parts
  const segments = text.split(/(```[\s\S]*?```|`[^`]*`)/g);
  return segments
    .map((seg, i) => {
      if (i % 2 === 1) return seg; // code block — skip

      // Rewrite bare URLs not already inside [text](url) or (url)
      let out = seg.replace(/(?<!\()(?<!\]\()https?:\/\/[^\s)<>]+/g, (url) => {
        try {
          const host = new URL(url).hostname;
          return `[${host}](${url})`;
        } catch {
          return url;
        }
      });

      // Unwrap empty links [text]() -> text
      out = out.replace(/\[([^\]]+)\]\(\s*\)/g, "$1");

      return out;
    })
    .join("");
}

function applyLaw1StripSources(text: string): string {
  const lines = text.split("\n");
  const last30 = lines.slice(Math.max(0, lines.length - 30));

  const sourceHeaderRe =
    /^(Sources|References|Further reading|Citations):\s*$/i;
  let sourceBlockStart = -1;

  for (let i = 0; i < last30.length; i++) {
    const line = last30[i];
    if (line !== undefined && sourceHeaderRe.test(line)) {
      // Check if followed by a bullet list
      const nextLine = last30[i + 1];
      if (nextLine !== undefined && /^[-*]/.test(nextLine)) {
        sourceBlockStart = lines.length - last30.length + i;
        break;
      }
    }
  }

  if (sourceBlockStart !== -1) {
    return lines.slice(0, sourceBlockStart).join("\n");
  }
  return text;
}

// ---------------------------------------------------------------------------
// LAW self-check
// ---------------------------------------------------------------------------

interface SelfCheckResult {
  body: string;
  violations: string[];
}

function runSelfCheck(
  rawBody: string,
  isComparison: boolean,
  entityA: string,
  entityB: string,
  badge: string,
): SelfCheckResult {
  const violations: string[] = [];
  let body = rawBody;

  // --- LAW 8: Badge ---
  const bodyLines = body.split("\n");
  const firstLine = bodyLines[0] ?? "";
  if (!BADGE_RE.test(firstLine)) {
    body = `${badge}\n\n${body}`;
  }

  // --- LAW 2: Body opener ---
  const updatedLines = body.split("\n");
  // Find first non-empty line after badge + blank
  let bodyStart = 0;
  if (BADGE_RE.test(updatedLines[0] ?? "")) {
    // Skip badge line and blank
    bodyStart = 2;
  }
  const firstBodyLine = updatedLines[bodyStart] ?? "";
  if (!isComparison) {
    if (!firstBodyLine.startsWith("What we learned:")) {
      violations.push(
        "LAW 2: body opener missing 'What we learned:' - regeneration required",
      );
    }
  } else {
    const expectedPrefix = `# ${entityA} vs ${entityB}`;
    if (!firstBodyLine.startsWith(expectedPrefix)) {
      violations.push(
        `LAW 2: COMPARISON body opener missing '${expectedPrefix}:' - regeneration required`,
      );
    }
  }

  // --- LAW 4: Forbidden headers ---
  const allowedHeaders = new Set([
    ...FRAMEWORK_HEADERS,
    ...(isComparison ? COMPARISON_ALLOWED_HEADERS : []),
    ...(isComparison ? [entityA, entityB] : []),
  ]);

  const headerRe = /^#{2,3}\s+(.+)$/gm;
  for (const match of body.matchAll(headerRe)) {
    const headerText = match[1]?.trim() ?? "";
    if (allowedHeaders.has(headerText)) continue;
    // Cluster Bank emits `### C1`, `### C2`, etc. as structural anchors —
    // allow any header that starts with the cluster-ID pattern.
    if (CLUSTER_ID_HEADER_RE.test(headerText)) continue;
    violations.push(
      `LAW 4: forbidden header '## ${headerText}' - regeneration required`,
    );
  }

  // --- LAW 6: Evidence dump ---
  if (/^### \d+\. .* \(score \d+,/m.test(body)) {
    violations.push(
      "LAW 6: raw evidence dump pattern found - regeneration required",
    );
  }

  // --- LAW 7: Citation format (auto-fix) ---
  body = applyLaw7Citations(body);

  // --- LAW 3: Em-dash (auto-fix) ---
  body = applyLaw3EmDash(body);

  // --- LAW 1: Trailing Sources block (auto-fix) ---
  body = applyLaw1StripSources(body);

  // --- LAW 5: Footer ---
  if (
    !body.includes("<!-- ENGINE FOOTER -->") ||
    !body.includes("<!-- END ENGINE FOOTER -->")
  ) {
    violations.push("LAW 5: ENGINE FOOTER missing");
  }

  return { body, violations };
}

// ---------------------------------------------------------------------------
// Core render function
// ---------------------------------------------------------------------------

export async function render(
  clusters: Cluster[],
  opts: RenderOptions,
  repoRoot: string,
): Promise<RenderResult> {
  const nowMs = opts.nowMs ?? Date.now();
  const version = opts.version ?? getPackageVersion();
  const selfCheck = opts.selfCheck !== false;
  const isComparison = isComparisonIntent(opts);
  const [entityA, entityB] = isComparison
    ? extractVsEntities(opts.topic, opts.vs)
    : [opts.topic, ""];

  // Build badge
  const badge = `🔎 oma-market v${version} · synced ${utcDate(nowMs)}`;

  // Build body
  let bodyContent: string;
  if (isComparison) {
    bodyContent = buildComparisonBody(clusters, entityA, entityB);
  } else {
    bodyContent = buildPainTrendBody(clusters, opts.intent);
  }

  // Cluster Bank: raw evidence dump for the analyst (host LLM) to consume
  // when filling SWOT / 5F / PESTEL slots. Sorted by (cross_source_count DESC,
  // member count DESC, top representative rrf_score DESC).
  const clusterBank = buildClusterBank(clusters);

  // Resolve framework sections (skeletons only — no auto-classification)
  const frameworkOverride = opts.frameworks ?? "auto";
  const specs = resolveFrameworks(opts.intent, frameworkOverride);
  const frameworkSections = specs.map((spec) => renderFrameworkSkeleton(spec));

  // Append cluster bank + framework skeletons at the right position
  const analystBlock = [clusterBank, ...frameworkSections].join("\n");
  if (isComparison) {
    const marker = "## The Bottom Line";
    const markerIdx = bodyContent.lastIndexOf(marker);
    if (markerIdx !== -1) {
      const afterMarker = bodyContent.indexOf(
        "\n\n",
        markerIdx + marker.length,
      );
      const insertAt =
        afterMarker !== -1 ? afterMarker + 2 : bodyContent.length;
      bodyContent = `${bodyContent.slice(0, insertAt)}${analystBlock}\n${bodyContent.slice(insertAt)}`;
    } else {
      bodyContent += `\n${analystBlock}`;
    }
  } else {
    bodyContent += `\n${analystBlock}`;
  }

  // Build footer
  const footer = buildFooter(clusters, opts);

  // Assemble full document
  let fullDoc = `${badge}\n\n${bodyContent}\n${footer}`;

  // LAW self-check
  let violations: string[] = [];
  let selfCheckPassed = true;

  if (selfCheck) {
    const result = runSelfCheck(fullDoc, isComparison, entityA, entityB, badge);
    fullDoc = result.body;
    violations = result.violations;
    selfCheckPassed = violations.length === 0;

    if (!selfCheckPassed) {
      // Append LAW VIOLATIONS comment before closing footer
      const footerMarker = "<!-- ENGINE FOOTER -->";
      const footerIdx = fullDoc.lastIndexOf(footerMarker);
      const violationComment = `<!-- LAW VIOLATIONS: ${violations.join(" | ")} -->`;
      if (footerIdx !== -1) {
        fullDoc =
          fullDoc.slice(0, footerIdx) +
          violationComment +
          "\n" +
          fullDoc.slice(footerIdx);
      } else {
        fullDoc += `\n${violationComment}`;
      }
    }
  }

  // Write output file (markdown). JSON format is emitted by the CLI runner
  // from the returned `markdown`/`clusters` payload, so skip the file here.
  const slug = slugify(opts.topic);
  const dateCompact = utcDateCompact(nowMs);
  const filename = `${slug}-${dateCompact}.md`;

  const outputDir = resolve(repoRoot, opts.outputDir ?? DEFAULT_OUTPUT_DIR);
  let outputPath = "";
  if (opts.format !== "json") {
    mkdirSync(outputDir, { recursive: true });
    outputPath = join(outputDir, filename);
    writeFileSync(outputPath, fullDoc, "utf8");
  }

  return {
    markdown: fullDoc,
    outputPath,
    selfCheckPassed,
    violations,
  };
}

// ---------------------------------------------------------------------------
// CLI flag parser
// ---------------------------------------------------------------------------

function parseFlag(argv: string[], flag: string): string | undefined {
  const idx = argv.indexOf(flag);
  if (idx !== -1 && idx + 1 < argv.length) return argv[idx + 1];
  return undefined;
}

function hasFlag(argv: string[], flag: string): boolean {
  return argv.includes(flag);
}

function packArgv(opts: Record<string, unknown>): string[] {
  const argv: string[] = [];
  if (opts.topic) argv.push("--topic", String(opts.topic));
  if (opts.intent) argv.push("--intent", String(opts.intent));
  if (opts.format) argv.push("--format", String(opts.format));
  if (opts.frameworks) argv.push("--frameworks", String(opts.frameworks));
  if (opts.vs) argv.push("--vs", String(opts.vs));
  if (opts.minTrust) argv.push("--min-trust", String(opts.minTrust));
  if (opts.selfCheck === false) argv.push("--no-self-check");
  if (opts.outputDir) argv.push("--output-dir", String(opts.outputDir));
  if (opts.nowMs) argv.push("--now-ms", String(opts.nowMs));
  if (opts.versionOverride)
    argv.push("--version-override", String(opts.versionOverride));
  return argv;
}

export { packArgv };

// ---------------------------------------------------------------------------
// CLI runner
// ---------------------------------------------------------------------------

export async function runRender(argv: string[]): Promise<number> {
  try {
    // Read stdin
    const chunks: Uint8Array[] = [];
    for await (const chunk of process.stdin) {
      chunks.push(chunk as Uint8Array);
    }
    const rawInput = Buffer.concat(chunks).toString("utf8");

    let stdinJson: Record<string, unknown>;
    try {
      stdinJson = JSON.parse(rawInput) as Record<string, unknown>;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      process.stderr.write(
        `[oma market render] invalid JSON on stdin: ${msg}\n`,
      );
      return 4;
    }

    // Validate with ClusterOutput schema (loosely - allow extra metadata fields)
    let parsed: ReturnType<typeof ClusterOutputSchema.parse>;
    try {
      parsed = ClusterOutputSchema.parse(stdinJson);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      process.stderr.write(
        `[oma market render] schema validation error: ${msg}\n`,
      );
      return 4;
    }

    // Flags override stdin values
    const topicFlag = parseFlag(argv, "--topic");
    const intentFlag = parseFlag(argv, "--intent");
    const formatFlag = parseFlag(argv, "--format") as "md" | "json" | undefined;
    const frameworksFlag = parseFlag(argv, "--frameworks");
    const vsFlag = parseFlag(argv, "--vs");
    const minTrustFlag = parseFlag(argv, "--min-trust") as
      | "verified"
      | "community"
      | "external"
      | undefined;
    const selfCheck = !hasFlag(argv, "--no-self-check");
    const outputDir = parseFlag(argv, "--output-dir");
    const nowMsStr = parseFlag(argv, "--now-ms");
    const versionOverride = parseFlag(argv, "--version-override");

    const topic = topicFlag ?? parsed.topic;
    const rawIntent = intentFlag ?? parsed.intent;

    const validIntents = ["pain", "trend", "competitor", "discovery"] as const;
    type IntentType = (typeof validIntents)[number];
    if (!validIntents.includes(rawIntent as IntentType)) {
      process.stderr.write(
        `[oma market render] invalid intent: '${rawIntent}'. Use pain|trend|competitor|discovery.\n`,
      );
      return 4;
    }
    const intent = rawIntent as IntentType;

    if (!topic) {
      process.stderr.write(
        "[oma market render] --topic required (or provide topic in stdin JSON)\n",
      );
      return 4;
    }

    const opts: RenderOptions = {
      topic,
      intent,
      format: formatFlag,
      frameworks: frameworksFlag,
      vs: vsFlag ?? null,
      minTrust: minTrustFlag,
      selfCheck,
      outputDir,
      nowMs: nowMsStr != null ? parseInt(nowMsStr, 10) : undefined,
      version: versionOverride,
      sourcesUsed: parsed.sources_used,
      sourcesFailed: parsed.sources_failed,
      cacheHit: false,
      latencyMs: 0,
    };

    // Walk up looking for the skill marker. Robust across source-tree runs
    // and the bundled cli/bin/cli.js binary.
    const { findRepoRoot } = await import("./shared/repo-root.js");
    const repoRoot = findRepoRoot();

    const result = await render(parsed.clusters, opts, repoRoot);

    if (opts.format === "json") {
      // Emit structured JSON to stdout; do not write the markdown brief.
      const payload = {
        topic: opts.topic,
        intent: opts.intent,
        vs: opts.vs ?? null,
        version: opts.version,
        clusters: parsed.clusters,
        markdown: result.markdown,
        violations: result.violations,
        self_check_passed: result.selfCheckPassed,
      };
      process.stdout.write(`${JSON.stringify(payload)}\n`);
    } else {
      // Stdout: first 50 lines preview of markdown brief
      const previewLines = result.markdown.split("\n").slice(0, 50).join("\n");
      process.stdout.write(`${previewLines}\n`);
      process.stderr.write(
        `[oma market render] written: ${result.outputPath}\n`,
      );
    }

    if (result.violations.length > 0) {
      process.stderr.write(
        `[oma market render] LAW violations:\n${result.violations.map((v) => `  - ${v}`).join("\n")}\n`,
      );
    }

    return result.selfCheckPassed ? 0 : 1;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    process.stderr.write(`[oma market render] error: ${msg}\n`);
    return 4;
  }
}
