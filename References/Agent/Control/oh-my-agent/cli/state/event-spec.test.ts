import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = join(__dirname, "../..");

describe("L1 event spec document", () => {
  it("publishes a JSON Schema with required common and decision fields", () => {
    const spec = readFileSync(
      join(
        repoRoot,
        ".agents",
        "skills",
        "_shared",
        "runtime",
        "event-spec.md",
      ),
      "utf-8",
    );
    const blocks = [...spec.matchAll(/```json\n([\s\S]*?)\n```/g)];
    const schemaBlock = blocks
      .map((block) => block[1])
      .find(
        (block): block is string => block?.includes("OMA L1 Event") === true,
      );
    expect(schemaBlock).toBeTruthy();

    const schema = JSON.parse(schemaBlock ?? "{}") as {
      required: string[];
      properties: Record<string, unknown>;
      allOf: unknown[];
    };

    expect(schema.required).toEqual([
      "eventId",
      "ts",
      "sid",
      "kind",
      "writerPid",
    ]);
    expect(schema.properties).toHaveProperty("payload");
    expect(JSON.stringify(schema.allOf)).toContain("decision.made");
    expect(JSON.stringify(schema.allOf)).toContain("rationale");
  });
});
