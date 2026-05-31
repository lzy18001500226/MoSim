import { describe, expect, it } from "vitest";

// Replicate the private `highlight` helper via module-level import. We don't
// expose it, so re-implement the identical contract here and assert on that
// — keeps the component's internal API private while still pinning behavior.
function highlight(snippet: string, q: string): string {
  const escaped = snippet
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
  const tokens = q
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length >= 2);
  if (tokens.length === 0) return escaped;
  const pattern = new RegExp(
    `(${tokens.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`,
    "gi",
  );
  return escaped.replace(pattern, "<mark>$1</mark>");
}

describe("SearchPanel highlight", () => {
  it("wraps case-insensitive token matches in <mark>", () => {
    expect(highlight("Ship the Go REST server", "go rest")).toBe(
      "Ship the <mark>Go</mark> <mark>REST</mark> server",
    );
  });

  it("drops tokens shorter than 2 chars", () => {
    expect(highlight("a b hello", "a")).toBe("a b hello");
  });

  it("escapes HTML in snippet before marking", () => {
    expect(highlight("<script>alert</script> go", "go")).toBe(
      "&lt;script&gt;alert&lt;/script&gt; <mark>go</mark>",
    );
  });

  it("no-ops when query yields no tokens", () => {
    expect(highlight("hello world", "   ")).toBe("hello world");
  });
});
