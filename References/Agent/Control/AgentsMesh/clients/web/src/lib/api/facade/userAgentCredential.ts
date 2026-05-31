// Connect-RPC adapter for proto.user_credential.v1.UserAgentCredentialService.
//
// Adapter pattern matches userGitCredential.ts. User-scoped service.

import {
  AgentCredentialProfileSchema,
  CreateAgentCredentialProfileRequestSchema,
  DeleteAgentCredentialProfileRequestSchema,
  DeleteAgentCredentialProfileResponseSchema,
  GetAgentCredentialProfileRequestSchema,
  ListAgentCredentialProfilesForAgentRequestSchema,
  ListAgentCredentialProfilesForAgentResponseSchema,
  ListAgentCredentialProfilesRequestSchema,
  ListAgentCredentialProfilesResponseSchema,
  SetDefaultAgentCredentialProfileRequestSchema,
  UpdateAgentCredentialProfileRequestSchema,
  type AgentCredentialProfile as ProtoProfile,
  type CredentialProfilesByAgent as ProtoGroup,
} from "@proto/user_credential/v1/user_credential_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getUserCredentialService } from "@/lib/wasm-core";

export interface AgentCredentialProfileData {
  id: number;
  user_id: number;
  agent_slug: string;
  name: string;
  description?: string;
  is_runner_host: boolean;
  is_default: boolean;
  is_active: boolean;
  configured_fields: string[];
  configured_values: Record<string, string>;
  agent_name?: string;
  created_at: string;
  updated_at: string;
}

export interface CredentialProfilesByAgentData {
  agent_slug: string;
  agent_name: string;
  profiles: AgentCredentialProfileData[];
}

function fromProto(p: ProtoProfile): AgentCredentialProfileData {
  return {
    id: Number(p.id),
    user_id: Number(p.userId),
    agent_slug: p.agentSlug,
    name: p.name,
    description: p.description,
    is_runner_host: p.isRunnerHost,
    is_default: p.isDefault,
    is_active: p.isActive,
    configured_fields: p.configuredFields,
    configured_values: p.configuredValues,
    agent_name: p.agentName,
    created_at: p.createdAt,
    updated_at: p.updatedAt,
  };
}

function fromProtoGroup(g: ProtoGroup): CredentialProfilesByAgentData {
  return {
    agent_slug: g.agentSlug,
    agent_name: g.agentName,
    profiles: g.profiles.map(fromProto),
  };
}

export async function listAgentCredentialProfiles(): Promise<{
  items: CredentialProfilesByAgentData[]; total: number;
}> {
  const req = create(ListAgentCredentialProfilesRequestSchema, {});
  const bytes = toBinary(ListAgentCredentialProfilesRequestSchema, req);
  const respBytes = await getUserCredentialService().listAgentCredentialsConnect(bytes);
  const resp = fromBinary(ListAgentCredentialProfilesResponseSchema, new Uint8Array(respBytes));
  return { items: resp.items.map(fromProtoGroup), total: Number(resp.total) };
}

export async function listAgentCredentialProfilesForAgent(agentSlug: string): Promise<{
  items: AgentCredentialProfileData[]; total: number;
  runner_host: { available: boolean; description: string } | undefined;
}> {
  const req = create(ListAgentCredentialProfilesForAgentRequestSchema, { agentSlug });
  const bytes = toBinary(ListAgentCredentialProfilesForAgentRequestSchema, req);
  const respBytes = await getUserCredentialService().listAgentCredentialsForAgentConnect(bytes);
  const resp = fromBinary(ListAgentCredentialProfilesForAgentResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProto),
    total: Number(resp.total),
    runner_host: resp.runnerHost ?
      { available: resp.runnerHost.available, description: resp.runnerHost.description } :
      undefined,
  };
}

export async function getAgentCredentialProfile(id: number): Promise<AgentCredentialProfileData> {
  const req = create(GetAgentCredentialProfileRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(GetAgentCredentialProfileRequestSchema, req);
  const respBytes = await getUserCredentialService().getAgentCredentialConnect(bytes);
  return fromProto(fromBinary(AgentCredentialProfileSchema, new Uint8Array(respBytes)));
}

export interface CreateAgentCredentialProfileInput {
  agent_slug: string;
  name: string;
  description?: string;
  is_runner_host: boolean;
  credentials: Record<string, string>;
  is_default: boolean;
}

export async function createAgentCredentialProfile(input: CreateAgentCredentialProfileInput): Promise<AgentCredentialProfileData> {
  const req = create(CreateAgentCredentialProfileRequestSchema, {
    agentSlug: input.agent_slug,
    name: input.name,
    description: input.description,
    isRunnerHost: input.is_runner_host,
    credentials: input.credentials,
    isDefault: input.is_default,
  });
  const bytes = toBinary(CreateAgentCredentialProfileRequestSchema, req);
  const respBytes = await getUserCredentialService().createAgentCredentialConnect(bytes);
  return fromProto(fromBinary(AgentCredentialProfileSchema, new Uint8Array(respBytes)));
}

export interface UpdateAgentCredentialProfileInput {
  name?: string;
  description?: string;
  is_runner_host?: boolean;
  credentials?: Record<string, string>;
  is_default?: boolean;
  is_active?: boolean;
}

export async function updateAgentCredentialProfile(id: number, input: UpdateAgentCredentialProfileInput): Promise<AgentCredentialProfileData> {
  const req = create(UpdateAgentCredentialProfileRequestSchema, {
    id: BigInt(id),
    name: input.name,
    description: input.description,
    isRunnerHost: input.is_runner_host,
    credentials: input.credentials ?? {},
    isDefault: input.is_default,
    isActive: input.is_active,
  });
  const bytes = toBinary(UpdateAgentCredentialProfileRequestSchema, req);
  const respBytes = await getUserCredentialService().updateAgentCredentialConnect(bytes);
  return fromProto(fromBinary(AgentCredentialProfileSchema, new Uint8Array(respBytes)));
}

export async function deleteAgentCredentialProfile(id: number): Promise<void> {
  const req = create(DeleteAgentCredentialProfileRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(DeleteAgentCredentialProfileRequestSchema, req);
  const respBytes = await getUserCredentialService().deleteAgentCredentialConnect(bytes);
  fromBinary(DeleteAgentCredentialProfileResponseSchema, new Uint8Array(respBytes));
}

export async function setDefaultAgentCredentialProfile(id: number): Promise<AgentCredentialProfileData> {
  const req = create(SetDefaultAgentCredentialProfileRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(SetDefaultAgentCredentialProfileRequestSchema, req);
  const respBytes = await getUserCredentialService().setDefaultAgentCredentialConnect(bytes);
  return fromProto(fromBinary(AgentCredentialProfileSchema, new Uint8Array(respBytes)));
}
