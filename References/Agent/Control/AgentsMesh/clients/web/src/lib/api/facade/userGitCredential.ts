// Connect-RPC adapter for proto.user_credential.v1.UserGitCredentialService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out — conventions §2.5), and
// decodes responses via .fromBinary(). No JSON intermediate.
//
// The adapter maps proto camelCase + BigInt → web snake_case + number so
// existing UI call sites consuming the legacy JSON shape don't need to
// change. User-scoped service: no orgSlug parameter required.

import {
  ClearDefaultGitCredentialRequestSchema,
  ClearDefaultGitCredentialResponseSchema,
  CreateGitCredentialRequestSchema,
  DeleteGitCredentialRequestSchema,
  DeleteGitCredentialResponseSchema,
  GetDefaultGitCredentialRequestSchema,
  GetDefaultGitCredentialResponseSchema,
  GetGitCredentialRequestSchema,
  GitCredentialSchema,
  ListGitCredentialsRequestSchema,
  ListGitCredentialsResponseSchema,
  SetDefaultGitCredentialRequestSchema,
  SetDefaultGitCredentialResponseSchema,
  UpdateGitCredentialRequestSchema,
  type GitCredential as ProtoGitCredential,
} from "@proto/user_credential/v1/user_credential_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getUserCredentialService } from "@/lib/wasm-core";
import type { GitCredentialData, CredentialTypeValue } from "@/lib/viewModels/userGitCredential";

function fromProto(c: ProtoGitCredential): GitCredentialData {
  return {
    id: Number(c.id),
    name: c.name,
    credential_type: c.credentialType as CredentialTypeValue,
    repository_provider_id: c.repositoryProviderId !== undefined
      ? Number(c.repositoryProviderId) : undefined,
    provider_name: c.providerName,
    public_key: c.publicKey,
    fingerprint: c.fingerprint,
    host_pattern: c.hostPattern,
    is_default: c.isDefault,
    created_at: c.createdAt,
    updated_at: c.updatedAt,
  };
}

export async function listGitCredentials(): Promise<{
  items: GitCredentialData[];
  total: number;
  runner_local_is_default: boolean;
}> {
  const req = create(ListGitCredentialsRequestSchema, {});
  const bytes = toBinary(ListGitCredentialsRequestSchema, req);
  const respBytes = await getUserCredentialService().listGitCredentialsConnect(bytes);
  const resp = fromBinary(ListGitCredentialsResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProto),
    total: Number(resp.total),
    runner_local_is_default: resp.runnerLocalIsDefault,
  };
}

export async function getGitCredential(id: number): Promise<GitCredentialData> {
  const req = create(GetGitCredentialRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(GetGitCredentialRequestSchema, req);
  const respBytes = await getUserCredentialService().getGitCredentialConnect(bytes);
  return fromProto(fromBinary(GitCredentialSchema, new Uint8Array(respBytes)));
}

export interface CreateGitCredentialInput {
  name: string;
  credential_type: string;
  repository_provider_id?: number;
  pat?: string;
  private_key?: string;
  host_pattern?: string;
}

export async function createGitCredential(input: CreateGitCredentialInput): Promise<GitCredentialData> {
  const req = create(CreateGitCredentialRequestSchema, {
    name: input.name,
    credentialType: input.credential_type,
    repositoryProviderId: input.repository_provider_id !== undefined
      ? BigInt(input.repository_provider_id) : undefined,
    pat: input.pat,
    privateKey: input.private_key,
    hostPattern: input.host_pattern,
  });
  const bytes = toBinary(CreateGitCredentialRequestSchema, req);
  const respBytes = await getUserCredentialService().createGitCredentialConnect(bytes);
  return fromProto(fromBinary(GitCredentialSchema, new Uint8Array(respBytes)));
}

export interface UpdateGitCredentialInput {
  name?: string;
  pat?: string;
  private_key?: string;
  host_pattern?: string;
}

export async function updateGitCredential(id: number, input: UpdateGitCredentialInput): Promise<GitCredentialData> {
  const req = create(UpdateGitCredentialRequestSchema, {
    id: BigInt(id),
    name: input.name,
    pat: input.pat,
    privateKey: input.private_key,
    hostPattern: input.host_pattern,
  });
  const bytes = toBinary(UpdateGitCredentialRequestSchema, req);
  const respBytes = await getUserCredentialService().updateGitCredentialConnect(bytes);
  return fromProto(fromBinary(GitCredentialSchema, new Uint8Array(respBytes)));
}

export async function deleteGitCredential(id: number): Promise<void> {
  const req = create(DeleteGitCredentialRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(DeleteGitCredentialRequestSchema, req);
  const respBytes = await getUserCredentialService().deleteGitCredentialConnect(bytes);
  fromBinary(DeleteGitCredentialResponseSchema, new Uint8Array(respBytes));
}

export async function getDefaultGitCredential(): Promise<{
  credential?: GitCredentialData;
  is_runner_local: boolean;
}> {
  const req = create(GetDefaultGitCredentialRequestSchema, {});
  const bytes = toBinary(GetDefaultGitCredentialRequestSchema, req);
  const respBytes = await getUserCredentialService().getDefaultGitCredentialConnect(bytes);
  const resp = fromBinary(GetDefaultGitCredentialResponseSchema, new Uint8Array(respBytes));
  return {
    credential: resp.credential ? fromProto(resp.credential) : undefined,
    is_runner_local: resp.isRunnerLocal,
  };
}

// credentialId === undefined → server sets runner_local as default.
export async function setDefaultGitCredential(credentialId?: number): Promise<{ is_runner_local: boolean }> {
  const req = create(SetDefaultGitCredentialRequestSchema, {
    credentialId: credentialId !== undefined ? BigInt(credentialId) : undefined,
  });
  const bytes = toBinary(SetDefaultGitCredentialRequestSchema, req);
  const respBytes = await getUserCredentialService().setDefaultGitCredentialConnect(bytes);
  const resp = fromBinary(SetDefaultGitCredentialResponseSchema, new Uint8Array(respBytes));
  return { is_runner_local: resp.isRunnerLocal };
}

export async function clearDefaultGitCredential(): Promise<void> {
  const req = create(ClearDefaultGitCredentialRequestSchema, {});
  const bytes = toBinary(ClearDefaultGitCredentialRequestSchema, req);
  const respBytes = await getUserCredentialService().clearDefaultGitCredentialConnect(bytes);
  fromBinary(ClearDefaultGitCredentialResponseSchema, new Uint8Array(respBytes));
}
