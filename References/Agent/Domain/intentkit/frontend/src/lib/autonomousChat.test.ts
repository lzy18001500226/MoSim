import { describe, expect, it } from "vitest";

import {
  buildChatThreadPath,
  buildTaskLogsPath,
  getAutonomousChatId,
} from "./autonomousChat";
import { isUserAuthoredMessage } from "../types/chat";
import { cacheAgentAvatar, getCachedAgentAvatar } from "./utils";

describe("autonomous chat helpers", () => {
  it("builds autonomous chat id from task id", () => {
    expect(getAutonomousChatId("task-123")).toBe("autonomous-task-123");
  });

  it("builds logs path from agent and task id", () => {
    expect(buildTaskLogsPath("agent-1", "task-1")).toBe(
      "/agent/agent-1/tasks/task-1/logs",
    );
  });

  it("builds chat path without thread id", () => {
    expect(buildChatThreadPath("agent-1", null)).toBe("/agent/agent-1");
  });

  it("builds chat path with thread id", () => {
    expect(buildChatThreadPath("agent-1", "thread-123")).toBe(
      "/agent/agent-1?thread=thread-123",
    );
  });

  it("treats trigger messages as user-authored", () => {
    expect(isUserAuthoredMessage("trigger")).toBe(true);
    expect(isUserAuthoredMessage("web")).toBe(true);
    expect(isUserAuthoredMessage("api")).toBe(true);
    expect(isUserAuthoredMessage("agent")).toBe(false);
  });

  it("caches agent avatar URLs by agent id", () => {
    cacheAgentAvatar("agent-1", "https://example.com/avatar.png");
    expect(getCachedAgentAvatar("agent-1")).toBe(
      "https://example.com/avatar.png",
    );

    cacheAgentAvatar("agent-1", null);
    expect(getCachedAgentAvatar("agent-1")).toBe(null);
  });
});
