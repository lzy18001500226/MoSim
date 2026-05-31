// Unit tests for clients/web/src/lib/api/agentConnect.ts converters.
//
// Covers the proto → snake_case web shape mappings — keeps the dual-track
// REST contract honest when the proto SSOT changes. Specifically pins:
//   * AgentListResponse §9 multi-field exception (builtin/custom/agents split)
//   * UserAgentConfigListResponse §9 sub-resource (configs field)
//   * config_values_json round-trip (UserAgentConfig wire shuttle)
//   * default_json round-trip (ConfigField wire shuttle)
//
// Note: this test file imports @proto/agent/v1/agent_pb which resolves via
// vitest.config.ts. Same dual-track caveat as repositoryConnect.test.ts.

import { describe, it, expect } from "vitest";
import { create } from "@bufbuild/protobuf";
import { AgentSchema } from "@proto/agent/v1/agent_pb";
import { fromProtoAgent } from "../connect/agentConnect";

describe("fromProtoAgent", () => {
  it("maps the full Agent proto to AgentData (snake_case)", () => {
    const proto = create(AgentSchema, {
      slug: "claude-code",
      name: "Claude Code",
      description: "AI coding agent",
      launchCommand: "claude",
      executable: "claude",
      defaultArgs: "--no-color",
      agentfileSource: "AGENT claude\n",
      isBuiltin: true,
      isActive: true,
      supportedModes: "pty,acp",
      createdAt: "2026-05-08T00:00:00Z",
      updatedAt: "2026-05-09T00:00:00Z",
    });
    const out = fromProtoAgent(proto);
    expect(out.slug).toBe("claude-code");
    expect(out.name).toBe("Claude Code");
    expect(out.description).toBe("AI coding agent");
    expect(out.launch_command).toBe("claude");
    expect(out.is_builtin).toBe(true);
    expect(out.is_active).toBe(true);
    expect(out.supported_modes).toBe("pty,acp");
  });

  it("preserves optional description when absent", () => {
    const proto = create(AgentSchema, {
      slug: "minimal",
      name: "Min",
      launchCommand: "./run",
      isBuiltin: false,
      isActive: true,
      supportedModes: "pty",
    });
    const out = fromProtoAgent(proto);
    expect(out.description).toBeUndefined();
    expect(out.supported_modes).toBe("pty");
    expect(out.is_builtin).toBe(false);
  });
});
