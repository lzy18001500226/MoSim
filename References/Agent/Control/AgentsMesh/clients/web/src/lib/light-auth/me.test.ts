import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { lightFetchMe } from "./me";
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

describe("lightFetchMe", () => {
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

  it("returns the user on 200", async () => {
    const fetchSpy = vi.fn<typeof fetch>(async () =>
      new Response(
        JSON.stringify({
          id: 5,
          email: "me@b.c",
          username: "me",
          name: "Mr Me",
          avatarUrl: "https://cdn/a.png",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    globalThis.fetch = fetchSpy as typeof fetch;

    const user = await lightFetchMe();

    expect(user?.email).toBe("me@b.c");
    expect(user?.id).toBe(5);
    const [url, init] = fetchSpy.mock.calls[0];
    expect(String(url)).toBe(`${ORIGIN}/proto.user.v1.UserService/GetMe`);
    const headers = (init as RequestInit).headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer tok");
  });

  it("returns null on 401 instead of throwing (best-effort)", async () => {
    globalThis.fetch = vi.fn<typeof fetch>(async () =>
      new Response(JSON.stringify({ code: "UNAUTHORIZED" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }),
    ) as typeof fetch;

    const user = await lightFetchMe();
    expect(user).toBeNull();
  });

  it("returns null on network error instead of throwing", async () => {
    globalThis.fetch = vi.fn<typeof fetch>(async () => {
      throw new TypeError("network down");
    }) as typeof fetch;
    const user = await lightFetchMe();
    expect(user).toBeNull();
  });

  it("returns null when 200 response has no email/username fields", async () => {
    globalThis.fetch = vi.fn<typeof fetch>(async () =>
      new Response("{}", { status: 200 }),
    ) as typeof fetch;
    const user = await lightFetchMe();
    expect(user).toBeNull();
  });
});
