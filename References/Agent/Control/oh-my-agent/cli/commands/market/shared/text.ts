/**
 * Shared text-cleaning helpers for the `oma market` pipeline.
 *
 * Render and normalizers route user-quoted snippets through `cleanSnippet`
 * to strip stray HTML, decode entities, and collapse whitespace. Keep this
 * minimal — losslessness matters more than fancy formatting.
 */

const NAMED_ENTITIES: Record<string, string> = {
  amp: "&",
  lt: "<",
  gt: ">",
  quot: '"',
  apos: "'",
  nbsp: " ",
  copy: "©",
  reg: "®",
  hellip: "…",
  mdash: "-",
  ndash: "-",
  lsquo: "'",
  rsquo: "'",
  ldquo: '"',
  rdquo: '"',
};

/**
 * Decode HTML entities (named + numeric). Lossless for the entities listed
 * in `NAMED_ENTITIES`; numeric (`&#NN;` and `&#xNN;`) decoded for full BMP
 * code points. Unknown entities pass through unchanged.
 */
export function decodeEntities(text: string): string {
  if (!text) return text;
  return text
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex: string) => {
      const code = Number.parseInt(hex, 16);
      return Number.isFinite(code) ? String.fromCodePoint(code) : `&#x${hex};`;
    })
    .replace(/&#(\d+);/g, (_, dec: string) => {
      const code = Number.parseInt(dec, 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : `&#${dec};`;
    })
    .replace(/&([a-zA-Z]+);/g, (m, name: string) => NAMED_ENTITIES[name] ?? m);
}

/** Strip HTML tags. Use for snippet/body normalization. */
export function stripTags(html: string): string {
  if (!html) return html;
  return html.replace(/<\s*\/?\s*[a-zA-Z][^>]*>/g, "");
}

/**
 * `decodeEntities` → strip tags → collapse repeated whitespace → trim.
 * Idempotent. Safe to call multiple times along the pipeline.
 */
export function cleanSnippet(text: string | null | undefined): string {
  if (!text) return "";
  return decodeEntities(stripTags(text))
    .replace(/[ \t ]+/g, " ")
    .replace(/\s*\n\s*/g, " ")
    .trim();
}
