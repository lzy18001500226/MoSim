// E2E API fixture. Connect-RPC only — REST is dead (R5 series complete).
//
// Specs talk to the backend through the typed Connect client:
//
//     test("foo", async ({ api }) => {
//       const cc = api.connect();
//       const { items } = await cc.channel.ListChannels({ orgSlug: TEST_ORG_SLUG });
//       expect(items.length).toBeGreaterThan(0);
//     });
//
// `api.connect()` lazily authenticates and returns a token-bound client.
// For multi-user flows (`loginAs`) ask for a second client from a fresh
// token; the same fixture keeps the primary user's token cached.

import { TEST_USER, getApiBaseUrl } from "../helpers/env";
import { makeConnectClient, type ConnectClient } from "../helpers/connect-client";

export class ApiFixture {
  private baseUrl: string;
  private token: string | null = null;
  private cachedClient: ConnectClient | null = null;

  constructor() {
    this.baseUrl = getApiBaseUrl();
  }

  /**
   * Authenticate with the default test user (or `(email, password)`) and cache
   * the JWT. Subsequent `connect()` calls reuse the same token.
   *
   * Returns the raw login envelope so existing specs that read `data.token`
   * / `data.user` still compile while the migration is in progress.
   */
  async login(
    email: string = TEST_USER.email,
    password: string = TEST_USER.password,
  ): Promise<{ token: string; refresh_token: string; user: unknown }> {
    const res = await this.fetchWithRetry(
      `${this.baseUrl}/proto.auth.v1.AuthService/Login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Connect-Protocol-Version": "1",
        },
        body: JSON.stringify({ email, password }),
      },
    );
    if (!res.ok) throw new Error(`Login failed: ${res.status}`);
    const data = await res.json();
    this.token = data.token;
    this.cachedClient = null;
    return {
      token: data.token,
      refresh_token: data.refreshToken ?? data.refresh_token,
      user: data.user,
    };
  }

  /** Switch the cached token to a different user — returns the new token. */
  async loginAs(email: string, password: string): Promise<string> {
    const data = await this.login(email, password);
    return data.token;
  }

  /**
   * Lazily build (or return cached) Connect client bound to the current token.
   * First call triggers default-user login if no `login()` happened yet.
   */
  async connect(): Promise<ConnectClient> {
    await this.ensureToken();
    if (!this.cachedClient) this.cachedClient = makeConnectClient(this.token);
    return this.cachedClient;
  }

  /** Build a connect client from an externally-issued token (for multi-user tests). */
  connectWithToken(token: string): ConnectClient {
    return makeConnectClient(token);
  }

  /** Return the current JWT (null when no login has happened yet). */
  getToken(): string | null {
    return this.token;
  }

  /** Returns the configured baseUrl for the rare spec that builds URLs by hand. */
  getBaseUrl(): string {
    return this.baseUrl;
  }

  // REST helpers — a handful of specs (envbundle / personal-agents-credentials)
  // still call legacy `/api/v1/...` REST endpoints for setup/teardown because
  // their Connect-RPC counterparts haven't landed yet. Keep these alive on the
  // fixture so specs don't reach for `fetch` directly with bespoke auth wiring.

  /** GET request with authentication. */
  async get(path: string): Promise<Response> {
    await this.ensureToken();
    return fetch(`${this.baseUrl}${path}`, {
      headers: { Authorization: `Bearer ${this.token}` },
    });
  }

  /** POST request with authentication. */
  async post(path: string, body?: unknown): Promise<Response> {
    await this.ensureToken();
    return fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /** PUT request with authentication. */
  async put(path: string, body: unknown): Promise<Response> {
    await this.ensureToken();
    return fetch(`${this.baseUrl}${path}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(body),
    });
  }

  /** PATCH request with authentication. */
  async patch(path: string, body: unknown): Promise<Response> {
    await this.ensureToken();
    return fetch(`${this.baseUrl}${path}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(body),
    });
  }

  /** DELETE request with authentication. */
  async delete(path: string): Promise<Response> {
    await this.ensureToken();
    return fetch(`${this.baseUrl}${path}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${this.token}` },
    });
  }

  /** POST without authentication. Used by specs that exercise the
   *  runner CLI bootstrap endpoint (/api/v1/runners/grpc/auth-url) and
   *  legacy REST setup that hasn't been Connect-migrated yet. */
  async postPublic(path: string, body: unknown): Promise<Response> {
    return this.fetchWithRetry(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }

  /** POST with a caller-supplied bearer token (multi-user / fresh-token flows). */
  async postWithToken(path: string, body: unknown, token: string): Promise<Response> {
    return this.fetchWithRetry(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /** GET with a caller-supplied bearer token. */
  async getWithToken(path: string, token: string): Promise<Response> {
    return fetch(`${this.baseUrl}${path}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  }

  /**
   * Retry-aware fetch: automatically retries on 429 (rate limited).
   * Exposed because a few specs build their own auth flows.
   */
  async fetchWithRetry(url: string, init: RequestInit, maxRetries = 3): Promise<Response> {
    for (let i = 0; i <= maxRetries; i++) {
      const res = await fetch(url, init);
      if (res.status !== 429 || i === maxRetries) return res;
      const delay = Math.min(1000 * 2 ** i, 5000);
      await new Promise((r) => setTimeout(r, delay));
    }
    return fetch(url, init); // unreachable, satisfies TS
  }

  private async ensureToken(): Promise<void> {
    if (!this.token) await this.login();
  }
}
