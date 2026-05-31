/* eslint-disable @typescript-eslint/no-explicit-any */

export const NOOP_PROXY = new Proxy({} as any, {
  get: (_target, prop) => {
    if (prop === "then") return undefined;
    return () => {
      if (typeof prop === "string" && (prop.endsWith("_json") || prop === "org_path")) return "[]";
      return undefined;
    };
  },
});

// Service registry storage. On the browser we promote the storage onto
// `globalThis` so it survives Next.js dev-chunk re-evaluations — multiple
// module instances of this file would otherwise each carry their own
// (empty) `i`/`ready`, and a chunk that did NOT receive `markServiceReady`
// would return NOOP_PROXY for wasm-backed reads (root block resolves to
// `null` → DocumentView wedges on "Loading workspace…"). On the server we
// keep module-scoped state — globalThis on the SSR side leaks between
// requests and we'd hand a half-initialised client store to the next
// renderer pass.
interface ServiceRegistry {
  ready: boolean;
  instances: Record<string, any>;
}

function makeRegistry(): ServiceRegistry { return { ready: false, instances: {} }; }

const isBrowser = typeof window !== "undefined";
const moduleRegistry: ServiceRegistry = makeRegistry();

function registry(): ServiceRegistry {
  if (!isBrowser) return moduleRegistry;
  const g = globalThis as unknown as { __amesh_svc_registry?: ServiceRegistry };
  if (!g.__amesh_svc_registry) g.__amesh_svc_registry = moduleRegistry;
  return g.__amesh_svc_registry;
}

export function isServiceReady(): boolean { return registry().ready; }
export function markServiceReady(): void { registry().ready = true; }

const g = <T>(k: string): T => {
  const reg = registry();
  return (reg.ready ? reg.instances[k] : NOOP_PROXY) as T;
};

export function registerServiceProvider(provider: Record<string, any>) {
  const reg = registry();
  for (const [key, value] of Object.entries(provider)) {
    reg.instances[key] = value;
  }
}

export function parseWasmAny<T>(val: unknown): T | null {
  if (!val) return null;
  return typeof val === "string" ? JSON.parse(val) : (val as T);
}

export const getApiClient = () => g<any>("apiClient");
export const getAuthManager = () => g<any>("authManager");
export const getPodState = () => g<any>("podState");
export const getPodService = () => g<any>("podService");
export const getTicketService = () => g<any>("ticketService");
export const getChannelService = () => g<any>("channelService");
export const getRunnerService = () => g<any>("runnerService");
export const getLoopService = () => g<any>("loopService");
export const getAutopilotService = () => g<any>("autopilotService");
export const getMeshService = () => g<any>("meshService");
export const getBillingService = () => g<any>("billingService");
export const getRepositoryService = () => g<any>("repositoryService");
export const getExtensionService = () => g<any>("extensionService");
export const getInvitationService = () => g<any>("invitationService");
export const getGrantService = () => g<any>("grantService");
export const getApiKeyService = () => g<any>("apiKeyService");
export const getBindingService = () => g<any>("bindingService");
export const getNotificationService = () => g<any>("notificationService");
export const getPromoCodeService = () => g<any>("promoCodeService");
export const getTokenUsageService = () => g<any>("tokenUsageService");
export const getSSOService = () => g<any>("ssoService");
export const getUserApiService = () => g<any>("userApiService");
export const getUserCredentialService = () => g<any>("userCredentialService");
export const getEnvBundleService = () => g<any>("envBundleService");
export const getOrgApiService = () => g<any>("orgApiService");
export const getAgentService = () => g<any>("agentService");
export const getTicketRelationsService = () => g<any>("ticketRelationsService");
export const getFileService = () => g<any>("fileService");
export const getSupportTicketService = () => g<any>("supportTicketService");
export const getAuthConnectService = () => g<any>("authConnectService");
export const getRunnerState = () => g<any>("runnerState");
export const getMeshState = () => g<any>("meshState");
export const getTicketState = () => g<any>("ticketState");
export const getChannelState = () => g<any>("channelState");
export const getLoopState = () => g<any>("loopState");
export const getAcpManager = () => g<any>("acpManager");
export const getRepoState = () => g<any>("repoState");
export const getAutopilotState = () => g<any>("autopilotState");
export const getRelayManager = () => g<any>("relayManager");
export const getBlockstoreService = () => g<any>("blockstoreService");

/**
 * Optional getter — returns undefined when no provider has registered a
 * local-runner service (web/iOS builds, where the desktop adapter is absent).
 * Renderer UI uses this to feature-detect and hide onboarding cards on
 * platforms that can't host a local runner.
 */
export const getLocalRunnerService = () => {
  const reg = registry();
  return reg.ready ? (reg.instances["localRunnerService"] as any | undefined) : undefined;
};
