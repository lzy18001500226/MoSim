// Migrated R5+: Connect-RPC tenant isolation.
//
// The Connect interceptors enforce that a caller can only operate on
// workspaces owned by an organization they belong to. Validate the
// contract at the Connect call boundary — passing an `org_slug` for an
// org the caller is NOT a member of must produce a Connect error that
// maps to HTTP 403/404 (PermissionDenied / NotFound). This replaces the
// legacy REST cross-org probes that read X-Organization-Slug headers,
// which the Connect surface doesn't speak.
import { test, expect, orgSlug, apiBase } from "../../fixtures/blockstore.fixture";

test("non-member call to a foreign org's blockstore service is rejected", async () => {
  // Use the test user's token but ask about a workspace in a fabricated
  // org the user isn't a member of. The interceptor short-circuits with
  // PermissionDenied(403) or NotFound(404) — either is an acceptable
  // negative result; both deny information about the foreign org's data.
  const loginRes = await fetch(`${apiBase}/proto.auth.v1.AuthService/Login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Connect-Protocol-Version": "1" },
    body: JSON.stringify({ email: "dev@agentsmesh.local", password: "devpass123" }),
  });
  const { token } = (await loginRes.json()) as { token: string };

  const res = await fetch(`${apiBase}/proto.blockstore.v1.BlockstoreService/ListWorkspaces`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "Connect-Protocol-Version": "1",
    },
    body: JSON.stringify({ orgSlug: "definitely-not-a-real-org-12345" }),
  });
  expect([403, 404]).toContain(res.status);
});

test("matching org_slug on caller's own org returns workspaces", async () => {
  // Positive control to confirm the gate is *org-scoped*, not a blanket
  // denial — same wire path, the only difference is org_slug.
  const loginRes = await fetch(`${apiBase}/proto.auth.v1.AuthService/Login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Connect-Protocol-Version": "1" },
    body: JSON.stringify({ email: "dev@agentsmesh.local", password: "devpass123" }),
  });
  const { token } = (await loginRes.json()) as { token: string };

  const res = await fetch(`${apiBase}/proto.blockstore.v1.BlockstoreService/ListWorkspaces`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "Connect-Protocol-Version": "1",
    },
    body: JSON.stringify({ orgSlug }),
  });
  expect(res.status).toBe(200);
});
