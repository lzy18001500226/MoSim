// Typed Connect-RPC client for the e2e suite.
//
// The legacy ApiFixture used REST-shaped `api.get(path)` calls that the R5
// refactor turned into Connect RPCs behind the scenes (via a transparent
// path-mapping adapter). That layer keeps old specs running but encodes
// the historical wire format in 50+ ad-hoc mapping rules. New specs (and
// rewrites of legacy ones) go through this typed wrapper directly:
//
//     const cc = makeConnectClient(token);
//     const { items } = await cc.channel.listChannels({ orgSlug: "dev-org" });
//
// Modeled after web-admin/src/lib/connect/transport.ts. Binary wire
// (application/proto) — same as the production clients use, so this
// suite asserts on what real users hit.
import {
  create,
  toBinary,
  fromBinary,
  type DescMessage,
  type MessageInitShape,
  type MessageShape,
} from "@bufbuild/protobuf";

import { getApiBaseUrl } from "./env";

import { ChannelService } from "../../../../proto/gen/ts/channel/v1/channel_pb";
import { TicketService } from "../../../../proto/gen/ts/ticket/v1/ticket_pb";
import { TicketRelationsService } from "../../../../proto/gen/ts/ticket_relations/v1/ticket_relations_pb";
import { RunnerService } from "../../../../proto/gen/ts/runner_api/v1/runner_pb";
import { AgentService, UserAgentConfigService } from "../../../../proto/gen/ts/agent/v1/agent_pb";
import { PodService } from "../../../../proto/gen/ts/pod/v1/pod_pb";
import { AgentPodSettingsService } from "../../../../proto/gen/ts/pod/v1/agentpod_settings_pb";
import { RepositoryService } from "../../../../proto/gen/ts/repository/v1/repository_pb";
import { BlockstoreService } from "../../../../proto/gen/ts/blockstore/v1/blockstore_pb";
import { BindingService } from "../../../../proto/gen/ts/binding/v1/binding_pb";
import { LoopService } from "../../../../proto/gen/ts/loop/v1/loop_pb";
import { BillingService } from "../../../../proto/gen/ts/billing/v1/billing_pb";
import { EnvBundleService } from "../../../../proto/gen/ts/env_bundle/v1/env_bundle_pb";
import { ApiKeyService } from "../../../../proto/gen/ts/apikey/v1/api_key_pb";
import { NotificationService } from "../../../../proto/gen/ts/notification/v1/notification_pb";
import { AuthService, AuthSessionService } from "../../../../proto/gen/ts/auth/v1/auth_pb";
import { OrgService } from "../../../../proto/gen/ts/org/v1/org_pb";
import { UserService } from "../../../../proto/gen/ts/user/v1/user_pb";
import {
  InvitationService,
  UserInvitationService,
  PublicInvitationService,
} from "../../../../proto/gen/ts/invitation/v1/invitation_pb";
import {
  UserGitCredentialService,
  UserAgentCredentialService,
  UserRepositoryProviderService,
} from "../../../../proto/gen/ts/user_credential/v1/user_credential_pb";
import { MeshService } from "../../../../proto/gen/ts/mesh/v1/mesh_pb";
import { AutopilotControllerService } from "../../../../proto/gen/ts/autopilot/v1/autopilot_pb";
import { TokenUsageService } from "../../../../proto/gen/ts/token_usage/v1/token_usage_pb";
import { MarketService } from "../../../../proto/gen/ts/extension/v1/market_pb";
import { SkillRegistryService } from "../../../../proto/gen/ts/extension/v1/skill_registry_pb";
import { RepoSkillService } from "../../../../proto/gen/ts/extension/v1/repo_skill_pb";
import { RepoMcpService } from "../../../../proto/gen/ts/extension/v1/repo_mcp_pb";
import { SupportTicketService } from "../../../../proto/gen/ts/support_ticket/v1/support_ticket_pb";
import { AdminService } from "../../../../proto/gen/ts/admin/v1/admin_pb";
import { PromoCodeService } from "../../../../proto/gen/ts/promocode/v1/promocode_pb";
import { FileService } from "../../../../proto/gen/ts/file/v1/file_pb";
import { SSOService } from "../../../../proto/gen/ts/sso/v1/sso_pb";
import { SSOAdminService } from "../../../../proto/gen/ts/sso/v1/sso_admin_pb";

export class ConnectError extends Error {
  readonly code: string;
  readonly status: number;
  constructor(message: string, code: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

interface CallOpts {
  token?: string | null;
}

/**
 * Low-level Connect call. Specs almost never need this directly — use the
 * service-typed client below (`makeConnectClient(token).channel.listChannels(...)`).
 * Kept exposed for rare paths the typed client doesn't yet cover.
 */
export async function callConnect<I extends DescMessage, O extends DescMessage>(
  service: string,
  method: string,
  inputSchema: I,
  outputSchema: O,
  input: MessageInitShape<I>,
  opts: CallOpts = {},
): Promise<MessageShape<O>> {
  const msg = create(inputSchema, input);
  const body = toBinary(inputSchema, msg);

  const headers: Record<string, string> = { "Content-Type": "application/proto" };
  if (opts.token) headers.Authorization = `Bearer ${opts.token}`;

  const url = `${getApiBaseUrl()}/${service}/${method}`;
  // Wrap body in Blob: Node 25's undici fetch has a detached-ArrayBuffer
  // bug when body is Uint8Array/ArrayBuffer AND the response is an HTTP
  // error (4xx/5xx) with a different content-type than the request.
  // Blob/string bodies don't trigger it. See manual reproduction:
  // {"Content-Type":"application/proto", body: Uint8Array} + 401 JSON
  // response → `Cannot perform ArrayBuffer.prototype.slice on a detached
  // ArrayBuffer`. Blob wrap is the cheapest workaround.
  const res = await fetch(url, {
    method: "POST",
    headers,
    body: new Blob([body], { type: "application/proto" }),
  });
  if (!res.ok) {
    const text = await res.text();
    let code = "unknown";
    let message = text;
    try {
      const j = JSON.parse(text) as { code?: string; message?: string };
      code = j.code ?? code;
      message = j.message ?? text;
    } catch {
      // Non-JSON error body — keep the raw text.
    }
    throw new ConnectError(`${service}/${method} → ${res.status} ${code}: ${message}`, code, res.status);
  }
  const buf = new Uint8Array(await res.arrayBuffer());
  return fromBinary(outputSchema, buf);
}

// Build a typed proxy for a single service from its generated descriptor.
// The proxy looks like `{ listChannels: (input) => Promise<Response>, ... }`
// — one method per RPC declared in the proto file. JS keys are camelCase
// (matching @bufbuild/protobuf v2 generated descriptors); the wire path
// uses PascalCase (matching the proto declaration), so we upper-case the
// first letter when issuing the call.
function makeServiceClient<S extends { typeName: string; method: Record<string, unknown> }>(
  svcDesc: S,
  token: string | null,
): Record<string, (input: unknown) => Promise<unknown>> {
  const out: Record<string, (input: unknown) => Promise<unknown>> = {};
  const methods = svcDesc.method as Record<string, { input: DescMessage; output: DescMessage }>;
  for (const [name, m] of Object.entries(methods)) {
    const wireName = name.charAt(0).toUpperCase() + name.slice(1);
    out[name] = (input: unknown) =>
      callConnect(svcDesc.typeName, wireName, m.input, m.output, input as MessageInitShape<DescMessage>, { token });
  }
  return out;
}

/**
 * Build a connect client bound to `token`. Each service property returns an
 * object whose keys are the RPC method names (PascalCase) and values are
 * `(input) => Promise<output>`. Input/output shapes come from the generated
 * TS — they are the proto-canonical camelCase shapes.
 */
export function makeConnectClient(token: string | null) {
  return {
    auth: makeServiceClient(AuthService, token),
    authSession: makeServiceClient(AuthSessionService, token),
    channel: makeServiceClient(ChannelService, token),
    ticket: makeServiceClient(TicketService, token),
    ticketRelations: makeServiceClient(TicketRelationsService, token),
    runner: makeServiceClient(RunnerService, token),
    agent: makeServiceClient(AgentService, token),
    userAgentConfig: makeServiceClient(UserAgentConfigService, token),
    pod: makeServiceClient(PodService, token),
    agentPodSettings: makeServiceClient(AgentPodSettingsService, token),
    repository: makeServiceClient(RepositoryService, token),
    blockstore: makeServiceClient(BlockstoreService, token),
    binding: makeServiceClient(BindingService, token),
    loop: makeServiceClient(LoopService, token),
    billing: makeServiceClient(BillingService, token),
    envBundle: makeServiceClient(EnvBundleService, token),
    apikey: makeServiceClient(ApiKeyService, token),
    notification: makeServiceClient(NotificationService, token),
    org: makeServiceClient(OrgService, token),
    user: makeServiceClient(UserService, token),
    invitation: makeServiceClient(InvitationService, token),
    userInvitation: makeServiceClient(UserInvitationService, token),
    publicInvitation: makeServiceClient(PublicInvitationService, token),
    userGitCredential: makeServiceClient(UserGitCredentialService, token),
    userAgentCredential: makeServiceClient(UserAgentCredentialService, token),
    userRepositoryProvider: makeServiceClient(UserRepositoryProviderService, token),
    mesh: makeServiceClient(MeshService, token),
    autopilot: makeServiceClient(AutopilotControllerService, token),
    tokenUsage: makeServiceClient(TokenUsageService, token),
    market: makeServiceClient(MarketService, token),
    skillRegistry: makeServiceClient(SkillRegistryService, token),
    repoSkill: makeServiceClient(RepoSkillService, token),
    repoMcp: makeServiceClient(RepoMcpService, token),
    supportTicket: makeServiceClient(SupportTicketService, token),
    admin: makeServiceClient(AdminService, token),
    promocode: makeServiceClient(PromoCodeService, token),
    file: makeServiceClient(FileService, token),
    sso: makeServiceClient(SSOService, token),
    ssoAdmin: makeServiceClient(SSOAdminService, token),
  };
}

export type ConnectClient = ReturnType<typeof makeConnectClient>;
