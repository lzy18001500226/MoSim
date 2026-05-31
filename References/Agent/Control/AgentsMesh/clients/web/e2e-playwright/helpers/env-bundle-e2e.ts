import type { Page } from "@playwright/test";
import { execSync } from "node:child_process";
import { TEST_ORG_SLUG, getComposeProject } from "./env";
import { pollUntil } from "./retry";
import { CreatePodModal } from "../pages/modals/create-pod.modal";
import type { ApiFixture } from "../fixtures/api.fixture";

// Dev compose has TWO runner services (runner-1 + runner-2 — see
// deploy/dev/docker-compose.yml). The pod scheduler picks one via
// least-loaded affinity, so we can't hard-code which container holds the
// dump file. Discover candidates at runtime via `docker ps`; reads happen
// against all of them and the first non-empty wins.
//
// docker-compose name suffix differs per service: `runner-1` has the
// short form, `runner-2` has `runner-2-1` (compose appends an instance
// index when the service name itself contains a digit). Filter by prefix
// and trust docker to list them all.
function listRunnerContainers(): string[] {
  const prefix = `${getComposeProject()}-runner`;
  try {
    const out = execSync(
      `docker ps --filter "name=${prefix}" --format "{{.Names}}"`,
      { encoding: "utf-8" },
    ).trim();
    return out.length ? out.split("\n") : [];
  } catch {
    return [];
  }
}
// PodService.CreatePod is org-scoped, lives on the Connect-RPC wire after R5.
const CREATE_POD_RPC = "/proto.pod.v1.PodService/CreatePod";

/**
 * Drive the Pod create dialog end-to-end and return the new pod's key.
 *
 * Owns the boilerplate that's identical across EnvBundle e2e specs:
 *   - navigate to /workspace (so the New-Pod button is mountable)
 *   - intercept the Connect-RPC CreatePod (binary proto, response carries
 *     pod_key in the typed envelope)
 *   - open dialog, select agent, expand advanced, apply bundle selection,
 *     submit, wait for close
 *   - poll backend until pod status reaches "running"
 *
 * Throws if the RPC returns non-2xx so the caller doesn't have to check
 * an error-state flag.
 */
export async function createPodAndWaitRunning(args: {
  page: Page;
  api: ApiFixture;
  agentSlug: string;
  /** Empty string = "Use Agent default auth"; undefined = leave picker alone. */
  selectCredentialName?: string;
  selectRuntimeBundleNames?: string[];
  /**
   * Optional escape hatch: run extra interactions against the modal after
   * the default credential/runtime picks but before submit. Useful for
   * exercising switch-paths (e.g. picking credential A then credential B).
   */
  customizeModal?: (modal: CreatePodModal) => Promise<void>;
  /** Status-poll timeout (default 30s). */
  statusTimeoutMs?: number;
}): Promise<string> {
  const {
    page,
    api,
    agentSlug,
    selectCredentialName,
    selectRuntimeBundleNames,
    customizeModal,
    statusTimeoutMs = 30_000,
  } = args;

  await page.goto(`/${TEST_ORG_SLUG}/workspace`);
  await page.waitForLoadState("domcontentloaded");

  // waitForResponse filters by URL+method so unrelated traffic doesn't
  // burn the listener. The frontend issues a Connect-RPC binary POST
  // against PodService.CreatePod — we wait on that path now.
  const podCreatePromise = page.waitForResponse(
    (r) => r.request().method() === "POST" && r.url().endsWith(CREATE_POD_RPC),
    { timeout: 20_000 },
  );

  const newPodBtn = page
    .getByRole("button", { name: /new pod|create new pod|新建 pod/i })
    .first();
  await newPodBtn.click();

  const modal = new CreatePodModal(page);
  await modal.waitForOpen();
  await modal.selectAgent(agentSlug);
  await modal.expandAdvancedOptions();
  if (selectCredentialName !== undefined) {
    await modal.selectCredential(selectCredentialName);
  }
  if (selectRuntimeBundleNames !== undefined) {
    await modal.selectRuntimeBundles(selectRuntimeBundleNames);
  }
  if (customizeModal) {
    await customizeModal(modal);
  }
  await modal.submit();

  const podRes = await podCreatePromise;
  if (!podRes.ok()) {
    const text = await podRes.text().catch(() => "");
    throw new Error(`Pod create failed: HTTP ${podRes.status()}: ${text}`);
  }

  await modal.waitForClosed(15_000);

  // The binary Connect response is awkward to decode here, so we resolve
  // the freshly-created pod by polling the org's most-recent running pod
  // via the typed Connect client. The previous pod was terminated by the
  // spec's `terminateAllPods` so the first running pod we see is ours.
  const cc = await api.connect();
  let createdPodKey: string | undefined;
  await pollUntil(
    async () => {
      const { items } = (await cc.pod.listPods({
        orgSlug: TEST_ORG_SLUG,
      })) as { items: Array<{ podKey?: string; status?: string }> };
      const fresh = items?.find((p) => p.status === "running" && p.podKey);
      if (fresh?.podKey) {
        createdPodKey = fresh.podKey;
        return true;
      }
      return false;
    },
    {
      maxAttempts: Math.ceil(statusTimeoutMs / 1000),
      intervalMs: 1000,
      label: "pod-running-key",
    },
  );

  if (!createdPodKey) {
    throw new Error("pollUntil resolved without capturing a pod key");
  }
  return createdPodKey;
}

/**
 * Read the env dump file that the e2e-echo agent writes on startup
 * (`/tmp/e2e-echo-env-dump-<pid>`). Polls every runner container until
 * one returns non-empty content or the timeout fires.
 *
 * 60s timeout (was 30s): the full chain is runner.gRPC stream →
 * create_pod RPC → PTY spawn → bash → `echo ready; env > /tmp/dump`,
 * which on a cold self-hosted runner with docker.io pulls + mTLS
 * cert exchange routinely takes 30-45s. PR #410's per-shard backend
 * isolation removed the cross-shard `terminateAllPods` race; what
 * remains is genuine cold-start latency, not a race.
 */
export async function readEnvDumpFromRunner(timeoutMs = 60_000): Promise<string> {
  const deadline = Date.now() + timeoutMs;
  let lastErr: string | undefined;
  const containers = listRunnerContainers();
  if (containers.length === 0) {
    throw new Error(
      `no runner containers found matching ${getComposeProject()}-runner — is the dev environment up?`,
    );
  }
  while (true) {
    for (const container of containers) {
      try {
        const out = execSync(
          `docker exec ${container} sh -c 'cat /tmp/e2e-echo-env-dump-* 2>/dev/null || true'`,
          { encoding: "utf-8" },
        ).trim();
        if (out.length > 0) return out;
      } catch (err) {
        lastErr = (err as Error).message;
      }
    }
    if (Date.now() >= deadline) break;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(
    `env dump file did not appear in any of [${containers.join(", ")}] within ${timeoutMs}ms` +
      (lastErr ? ` (last error: ${lastErr})` : ""),
  );
}

/** Wipe any stale dump files from prior runs across every runner container. */
export function clearRunnerDumps(): void {
  for (const container of listRunnerContainers()) {
    try {
      execSync(
        `docker exec ${container} sh -c 'rm -f /tmp/e2e-echo-env-dump-* 2>/dev/null || true'`,
        { encoding: "utf-8" },
      );
    } catch {
      // Container may not be up yet — best effort.
    }
  }
}
