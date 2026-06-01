/**
 * Strategic-framework section emitter for `oma market render`.
 *
 * Architecture: the CLI never performs SWOT / Porter's 5 Forces / PESTEL
 * classification. Hard-coded keyword classifiers cannot generalize across
 * domains, languages, or context (positive vs negative use of the same
 * word). Instead the CLI emits:
 *   1. A **Cluster Bank** (raw cluster dump — see render.ts).
 *   2. **Framework skeletons** with empty slots and an analyst prompt
 *      that points at `.agents/skills/oma-market/resources/frameworks/<name>.md`.
 *
 * The host LLM (Claude / Codex / Gemini) reads the brief, applies the
 * classification prompt, and fills in the slots — same pattern as
 * last30days `--plan`: the model owns semantic work, the CLI owns
 * deterministic compute.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type FrameworkName = "swot" | "5f" | "pestel";

export interface FrameworkSpec {
  name: FrameworkName;
  applies: boolean;
  /** Relative path used by render to reference the analyst prompt. */
  promptRef: string;
}

// ---------------------------------------------------------------------------
// Intent → framework map
// ---------------------------------------------------------------------------

export const FRAMEWORK_INTENT_MAP: Record<
  "pain" | "trend" | "competitor" | "discovery",
  FrameworkName[]
> = {
  pain: ["swot"],
  trend: ["swot"],
  competitor: ["swot", "5f"],
  discovery: ["swot", "pestel"],
};

const VALID_FRAMEWORKS = new Set<FrameworkName>(["swot", "5f", "pestel"]);

const PROMPT_REF: Record<FrameworkName, string> = {
  swot: ".agents/skills/oma-market/resources/frameworks/swot.md",
  "5f": ".agents/skills/oma-market/resources/frameworks/porters-5f.md",
  pestel: ".agents/skills/oma-market/resources/frameworks/pestel.md",
};

const DISPLAY_NAME: Record<FrameworkName, string> = {
  swot: "SWOT",
  "5f": "Porter's 5 Forces",
  pestel: "PESTEL",
};

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Resolve which frameworks to emit for the given intent and CLI override.
 * `override`:
 *   - "auto" → use FRAMEWORK_INTENT_MAP
 *   - "none" → empty array (skip all framework sections)
 *   - csv list of names → those frameworks (filtered to VALID_FRAMEWORKS)
 */
export function resolveFrameworks(
  intent: "pain" | "trend" | "competitor" | "discovery",
  override: "auto" | "none" | string,
): FrameworkSpec[] {
  if (override === "none") return [];

  let names: FrameworkName[];
  if (override === "auto") {
    names = FRAMEWORK_INTENT_MAP[intent];
  } else {
    names = override
      .split(",")
      .map((s) => s.trim() as FrameworkName)
      .filter((n) => VALID_FRAMEWORKS.has(n));
  }

  return names.map((name) => ({
    name,
    applies: true,
    promptRef: PROMPT_REF[name],
  }));
}

/**
 * Emit a framework section as a SKELETON. The slots are explicitly empty so
 * the host LLM filling the brief can detect them and apply the analyst
 * prompt referenced in the section header.
 */
export function renderFrameworkSkeleton(fw: FrameworkSpec): string {
  switch (fw.name) {
    case "swot":
      return renderSwotSkeleton(fw);
    case "5f":
      return render5fSkeleton(fw);
    case "pestel":
      return renderPestelSkeleton(fw);
  }
}

// ---------------------------------------------------------------------------
// Skeleton emitters
// ---------------------------------------------------------------------------

const ANALYST_NOTE = (fw: FrameworkSpec): string =>
  `> _Analyst input required._ Classify clusters from the Cluster Bank above ` +
  `into the slots below per \`${fw.promptRef}\`. ` +
  `Every bullet cites a cluster representative as \`[name](url)\`. ` +
  `Empty quadrants → write \`_(no signal)_\`.`;

function renderSwotSkeleton(fw: FrameworkSpec): string {
  return [
    `## ${DISPLAY_NAME.swot}`,
    "",
    ANALYST_NOTE(fw),
    "",
    "**Strengths**",
    "- _(fill from cluster bank)_",
    "",
    "**Weaknesses**",
    "- _(fill from cluster bank)_",
    "",
    "**Opportunities**",
    "- _(fill from cluster bank)_",
    "",
    "**Threats**",
    "- _(fill from cluster bank)_",
    "",
  ].join("\n");
}

function render5fSkeleton(fw: FrameworkSpec): string {
  return [
    `## ${DISPLAY_NAME["5f"]}`,
    "",
    ANALYST_NOTE(fw),
    "",
    "**Threat of new entrants** — _(fill: barriers / capital / regulation signals)_",
    "",
    "**Bargaining power of suppliers** — _(fill: vendor lock-in / single-source signals)_",
    "",
    "**Bargaining power of buyers** — _(fill: price sensitivity / switching cost / churn signals)_",
    "",
    "**Threat of substitutes** — _(fill: alternative / migration signals)_",
    "",
    "**Industry rivalry** — _(fill: head-to-head / market-share / intensity signals)_",
    "",
  ].join("\n");
}

function renderPestelSkeleton(fw: FrameworkSpec): string {
  return [
    `## ${DISPLAY_NAME.pestel}`,
    "",
    ANALYST_NOTE(fw),
    "",
    "**Political** — _(fill: government / policy / sanctions signals)_",
    "",
    "**Economic** — _(fill: demand / supply / macro signals)_",
    "",
    "**Social** — _(fill: demographics / sentiment / lifestyle signals)_",
    "",
    "**Technological** — _(fill: platform / AI / automation signals)_",
    "",
    "**Environmental** — _(fill: sustainability / climate signals)_",
    "",
    "**Legal** — _(fill: IP / compliance / litigation signals)_",
    "",
  ].join("\n");
}
