import { describe, expect, it } from "vitest";

import type { Block } from "@/lib/viewModels/blockstore";

import { buildSpecMap } from "./useBlockTypeSpec";

const WS = "00000000-0000-0000-0000-000000000001";
const OTHER_WS = "00000000-0000-0000-0000-000000000002";

function typeDef(id: string, data: Record<string, unknown>, ws = WS): Block {
  return {
    id,
    workspace_id: ws,
    type: "block_type_def",
    data,
    meta: {},
    created_by: 1,
    created_at: "",
    updated_at: "",
  } as Block;
}

describe("buildSpecMap", () => {
  it("returns empty map when no type_def blocks exist", () => {
    expect(buildSpecMap({}, WS)).toEqual({});
  });

  it("decodes a single type_def into a spec", () => {
    const blocks = {
      a: typeDef("a", {
        type_key: "okr",
        revision: 1,
        label: "OKR",
        columns: [{ key: "title", type: "text", required: true }],
      }),
    };
    const specs = buildSpecMap(blocks, WS);
    expect(specs.okr.type).toBe("okr");
    expect(specs.okr.label).toBe("OKR");
    expect(specs.okr.revision).toBe(1);
    expect(specs.okr.columns).toHaveLength(1);
  });

  it("picks the highest revision when multiple type_defs share a type_key", () => {
    const blocks = {
      a: typeDef("a", { type_key: "okr", revision: 1, columns: [{ key: "v1", type: "text" }] }),
      b: typeDef("b", { type_key: "okr", revision: 5, columns: [{ key: "v5", type: "text" }] }),
      c: typeDef("c", { type_key: "okr", revision: 3, columns: [{ key: "v3", type: "text" }] }),
    };
    const specs = buildSpecMap(blocks, WS);
    expect(specs.okr.revision).toBe(5);
    expect(specs.okr.columns?.[0].key).toBe("v5");
  });

  it("ignores type_defs from other workspaces", () => {
    const blocks = {
      local: typeDef("local", { type_key: "here", revision: 1, columns: [] }),
      foreign: typeDef("foreign", { type_key: "there", revision: 1, columns: [] }, OTHER_WS),
    };
    const specs = buildSpecMap(blocks, WS);
    expect(specs.here).toBeDefined();
    expect(specs.there).toBeUndefined();
  });

  it("filters malformed columns", () => {
    const blocks = {
      a: typeDef("a", {
        type_key: "thing",
        columns: [
          { key: "ok", type: "text" },
          { key: "bad_no_type" },        // missing type
          { type: "text" },              // missing key
          "not_an_object",
          null,
        ],
      }),
    };
    const specs = buildSpecMap(blocks, WS);
    expect(specs.thing.columns).toHaveLength(1);
    expect(specs.thing.columns?.[0].key).toBe("ok");
  });

  it("skips blocks without a type_key", () => {
    const blocks = { a: typeDef("a", { revision: 1, columns: [] }) };
    expect(buildSpecMap(blocks, WS)).toEqual({});
  });
});
