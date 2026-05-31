import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
  lightGetRunnerAuthStatus,
  lightAuthorizeRunner,
  lightCreateRunnerToken,
  lightListRunners,
} from "./runners";
import { writeLightSession, resolveLightBaseUrl } from "@/lib/light-session";

const ORIGIN = resolveLightBaseUrl();

function primeAuth() {
  writeLightSession({
    accessToken: "tok",
    refreshToken: "r",
    expiresAt: Math.floor(Date.now() / 1000) + 3600,
    baseUrl: ORIGIN,
  });
}

describe("lightGetRunnerAuthStatus", () => {
  let originalFetch: typeof fetch;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
    window.localStorage.clear();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    window.localStorage.clear();
  });

  it("POSTs authKey body to RunnerPublicService/GetRunnerAuthStatus and returns the status payload", async () => {
    const fetchSpy = vi.fn<typeof fetch>(async () =>
      new Response(
        JSON.stringify({
          status: "authorized",
          nodeId: "node-1",
          expiresAt: "2026-12-31T00:00:00Z",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    globalThis.fetch = fetchSpy as typeof fetch;

    const status = await lightGetRunnerAuthStatus("abc+key/with space");

    expect(status.status).toBe("authorized");
    expect(status.node_id).toBe("node-1");
    const [url, init] = fetchSpy.mock.calls[0];
    expect(String(url)).toBe(
      `${ORIGIN}/proto.runner_api.v1.RunnerPublicService/GetRunnerAuthStatus`,
    );
    expect((init as RequestInit).method).toBe("POST");
    expect((init as RequestInit).body).toBe(
      JSON.stringify({ authKey: "abc+key/with space" }),
    );
  });
});

describe("lightAuthorizeRunner", () => {
  let originalFetch: typeof fetch;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
    window.localStorage.clear();
    primeAuth();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    window.localStorage.clear();
  });

  it("POSTs to RunnerService/AuthorizeRunner with orgSlug + authKey + nodeId (camelCase)", async () => {
    const fetchSpy = vi.fn<typeof fetch>(async () =>
      new Response(
        JSON.stringify({ runnerId: 42, nodeId: "node-42", message: "ok" }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    globalThis.fetch = fetchSpy as typeof fetch;

    const resp = await lightAuthorizeRunner({
      organizationSlug: "dev-org",
      authKey: "key-1",
      nodeId: "node-42",
    });

    expect(resp.runner_id).toBe(42);
    const [url, init] = fetchSpy.mock.calls[0];
    expect(String(url)).toBe(
      `${ORIGIN}/proto.runner_api.v1.RunnerService/AuthorizeRunner`,
    );
    expect((init as RequestInit).method).toBe("POST");
    expect((init as RequestInit).body).toBe(
      JSON.stringify({ orgSlug: "dev-org", authKey: "key-1", nodeId: "node-42" }),
    );
    const headers = (init as RequestInit).headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer tok");
  });

  it("sends org slug as part of JSON body (Connect-RPC, no URL encoding)", async () => {
    const fetchSpy = vi.fn<typeof fetch>(async () =>
      new Response(JSON.stringify({ runnerId: 1 }), { status: 200 }),
    );
    globalThis.fetch = fetchSpy as typeof fetch;

    await lightAuthorizeRunner({
      organizationSlug: "ns/dev",
      authKey: "k",
    });

    const [url, init] = fetchSpy.mock.calls[0];
    expect(String(url)).toBe(
      `${ORIGIN}/proto.runner_api.v1.RunnerService/AuthorizeRunner`,
    );
    const bodyJson = JSON.parse((init as RequestInit).body as string);
    expect(bodyJson.orgSlug).toBe("ns/dev");
  });

  it("defaults nodeId to empty string when not provided", async () => {
    const fetchSpy = vi.fn<typeof fetch>(async () =>
      new Response(JSON.stringify({ runnerId: 1 }), { status: 200 }),
    );
    globalThis.fetch = fetchSpy as typeof fetch;

    await lightAuthorizeRunner({ organizationSlug: "dev", authKey: "k" });

    const [, init] = fetchSpy.mock.calls[0];
    expect((init as RequestInit).body).toBe(
      JSON.stringify({ orgSlug: "dev", authKey: "k", nodeId: "" }),
    );
  });
});

describe("lightCreateRunnerToken", () => {
  let originalFetch: typeof fetch;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
    window.localStorage.clear();
    primeAuth();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    window.localStorage.clear();
  });

  it("POSTs to RunnerService/CreateRunnerToken and returns the token", async () => {
    const fetchSpy = vi.fn<typeof fetch>(async () =>
      new Response(
        JSON.stringify({ token: "reg-token-xyz", expiresAt: "..." }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    globalThis.fetch = fetchSpy as typeof fetch;

    const tok = await lightCreateRunnerToken("dev-org");

    expect(tok).toBe("reg-token-xyz");
    const [url, init] = fetchSpy.mock.calls[0];
    expect(String(url)).toBe(
      `${ORIGIN}/proto.runner_api.v1.RunnerService/CreateRunnerToken`,
    );
    expect((init as RequestInit).method).toBe("POST");
    expect((init as RequestInit).body).toBe(
      JSON.stringify({ orgSlug: "dev-org", labels: [] }),
    );
  });

  it("returns null when token field is missing", async () => {
    globalThis.fetch = vi.fn<typeof fetch>(async () =>
      new Response("{}", { status: 200 }),
    ) as typeof fetch;
    const tok = await lightCreateRunnerToken("dev-org");
    expect(tok).toBeNull();
  });
});

describe("lightListRunners", () => {
  let originalFetch: typeof fetch;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
    window.localStorage.clear();
    primeAuth();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    window.localStorage.clear();
  });

  it("returns the runners array from RunnerService/ListRunners", async () => {
    const fetchSpy = vi.fn<typeof fetch>(async () =>
      new Response(
        JSON.stringify({
          items: [
            {
              id: 1,
              nodeId: "n1",
              status: "online",
              currentPods: 0,
              maxConcurrentPods: 4,
              isEnabled: true,
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    globalThis.fetch = fetchSpy as typeof fetch;

    const runners = await lightListRunners("dev-org");

    expect(runners).toHaveLength(1);
    expect(runners[0].node_id).toBe("n1");
    const [url, init] = fetchSpy.mock.calls[0];
    expect(String(url)).toBe(
      `${ORIGIN}/proto.runner_api.v1.RunnerService/ListRunners`,
    );
    expect((init as RequestInit).method).toBe("POST");
    expect((init as RequestInit).body).toBe(JSON.stringify({ orgSlug: "dev-org" }));
    const headers = (init as RequestInit).headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer tok");
  });

  it("returns empty array when items field is missing", async () => {
    globalThis.fetch = vi.fn<typeof fetch>(async () =>
      new Response("{}", { status: 200 }),
    ) as typeof fetch;
    const runners = await lightListRunners("dev-org");
    expect(runners).toEqual([]);
  });
});
