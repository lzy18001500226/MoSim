import { getApiBaseUrl, TEST_USER, TEST_ORG_SLUG } from "./env";

/**
 * Terminate ALL active pods via API.
 * Used in test cleanup to prevent quota exhaustion.
 *
 * Migrated R5+: REST endpoints (/api/v1/auth/login, /api/v1/orgs/{slug}/pods,
 * /pods/{key}/terminate) were removed by the Connect-RPC migration. The
 * helper now talks Connect-RPC JSON (application/json + Connect-Protocol-Version
 * header) for a self-contained pre-test reset.
 */
const CONNECT_HEADERS = {
  "Content-Type": "application/json",
  "Connect-Protocol-Version": "1",
};

export async function terminateAllPods(): Promise<number> {
  const baseUrl = getApiBaseUrl();
  try {
    const loginRes = await fetch(`${baseUrl}/proto.auth.v1.AuthService/Login`, {
      method: "POST",
      headers: CONNECT_HEADERS,
      body: JSON.stringify({ email: TEST_USER.email, password: TEST_USER.password }),
    });
    if (!loginRes.ok) return 0;
    const { token } = (await loginRes.json()) as { token: string };
    if (!token) return 0;
    const authedHeaders = { ...CONNECT_HEADERS, Authorization: `Bearer ${token}` };

    const podsRes = await fetch(`${baseUrl}/proto.pod.v1.PodService/ListPods`, {
      method: "POST",
      headers: authedHeaders,
      // No status filter — terminate any in-flight pod regardless of state
      // (running, initializing, paused, disconnected) so the next spec
      // starts from a clean quota.
      body: JSON.stringify({ orgSlug: TEST_ORG_SLUG }),
    });
    if (!podsRes.ok) return 0;
    const { items = [], pods = [] } = (await podsRes.json()) as {
      items?: Array<{ podKey?: string; status?: string }>;
      pods?: Array<{ podKey?: string; status?: string }>;
    };
    const list = items.length ? items : pods;

    const live = list.filter((p) =>
      ["running", "initializing", "paused", "disconnected"].includes(p.status ?? ""),
    );

    let count = 0;
    for (const pod of live) {
      if (!pod.podKey) continue;
      await fetch(`${baseUrl}/proto.pod.v1.PodService/TerminatePod`, {
        method: "POST",
        headers: {
          ...authedHeaders,
          // Tag this call so the backend TerminatePod handler's
          // caller-info slog line reveals it's the test helper.
          // Anything else hitting that endpoint within ~500 ms of
          // a create_pod is a flaky-race smoking gun.
          "X-E2E-Caller": "terminateAllPods",
        },
        body: JSON.stringify({ orgSlug: TEST_ORG_SLUG, podKey: pod.podKey }),
      }).catch(() => {});
      count++;
    }
    // Wait for pods to fully terminate and release runner capacity.
    if (count > 0) {
      await new Promise((r) => setTimeout(r, 5000));
    }
    return count;
  } catch {
    return 0;
  }
}
