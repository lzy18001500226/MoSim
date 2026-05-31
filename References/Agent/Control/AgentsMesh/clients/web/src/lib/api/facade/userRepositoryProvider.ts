// Connect-RPC adapter for proto.user_credential.v1.UserRepositoryProviderService.
//
// Wire layer is proto-SSOT: returns and consumes `@proto/user_credential/v1`
// types directly. No adapter DTO layer.

import {
  CreateRepositoryProviderRequestSchema,
  DeleteRepositoryProviderRequestSchema,
  DeleteRepositoryProviderResponseSchema,
  GetRepositoryProviderRequestSchema,
  ListProviderRepositoriesRequestSchema,
  ListProviderRepositoriesResponseSchema,
  ListRepositoryProvidersRequestSchema,
  ListRepositoryProvidersResponseSchema,
  RepositoryProviderSchema,
  SetDefaultRepositoryProviderRequestSchema,
  SetDefaultRepositoryProviderResponseSchema,
  TestRepositoryProviderConnectionRequestSchema,
  TestRepositoryProviderConnectionResponseSchema,
  UpdateRepositoryProviderRequestSchema,
  type ProviderRepository,
  type RepositoryProvider,
} from "@proto/user_credential/v1/user_credential_pb";
import { create, toBinary, fromBinary, type MessageInitShape } from "@bufbuild/protobuf";
import { getUserCredentialService } from "@/lib/wasm-core";

export type { RepositoryProvider, ProviderRepository } from "@proto/user_credential/v1/user_credential_pb";

export async function listRepositoryProviders(): Promise<{
  items: RepositoryProvider[];
  total: number;
}> {
  const req = create(ListRepositoryProvidersRequestSchema, {});
  const bytes = toBinary(ListRepositoryProvidersRequestSchema, req);
  const respBytes = await getUserCredentialService().listRepositoryProvidersConnect(bytes);
  const resp = fromBinary(ListRepositoryProvidersResponseSchema, new Uint8Array(respBytes));
  return { items: resp.items, total: Number(resp.total) };
}

export async function getRepositoryProvider(id: number): Promise<RepositoryProvider> {
  const req = create(GetRepositoryProviderRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(GetRepositoryProviderRequestSchema, req);
  const respBytes = await getUserCredentialService().getRepositoryProviderConnect(bytes);
  return fromBinary(RepositoryProviderSchema, new Uint8Array(respBytes));
}

export async function createRepositoryProvider(
  input: MessageInitShape<typeof CreateRepositoryProviderRequestSchema>,
): Promise<RepositoryProvider> {
  const req = create(CreateRepositoryProviderRequestSchema, input);
  const bytes = toBinary(CreateRepositoryProviderRequestSchema, req);
  const respBytes = await getUserCredentialService().createRepositoryProviderConnect(bytes);
  return fromBinary(RepositoryProviderSchema, new Uint8Array(respBytes));
}

export async function updateRepositoryProvider(
  id: number,
  input: Omit<MessageInitShape<typeof UpdateRepositoryProviderRequestSchema>, "id">,
): Promise<RepositoryProvider> {
  const req = create(UpdateRepositoryProviderRequestSchema, { id: BigInt(id), ...input });
  const bytes = toBinary(UpdateRepositoryProviderRequestSchema, req);
  const respBytes = await getUserCredentialService().updateRepositoryProviderConnect(bytes);
  return fromBinary(RepositoryProviderSchema, new Uint8Array(respBytes));
}

export async function deleteRepositoryProvider(id: number): Promise<void> {
  const req = create(DeleteRepositoryProviderRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(DeleteRepositoryProviderRequestSchema, req);
  const respBytes = await getUserCredentialService().deleteRepositoryProviderConnect(bytes);
  fromBinary(DeleteRepositoryProviderResponseSchema, new Uint8Array(respBytes));
}

export async function setDefaultRepositoryProvider(id: number): Promise<void> {
  const req = create(SetDefaultRepositoryProviderRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(SetDefaultRepositoryProviderRequestSchema, req);
  const respBytes = await getUserCredentialService().setDefaultRepositoryProviderConnect(bytes);
  fromBinary(SetDefaultRepositoryProviderResponseSchema, new Uint8Array(respBytes));
}

export async function testRepositoryProviderConnection(id: number): Promise<{ success: boolean; message: string }> {
  const req = create(TestRepositoryProviderConnectionRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(TestRepositoryProviderConnectionRequestSchema, req);
  const respBytes = await getUserCredentialService().testRepositoryProviderConnectionConnect(bytes);
  const resp = fromBinary(TestRepositoryProviderConnectionResponseSchema, new Uint8Array(respBytes));
  return { success: resp.success, message: resp.message };
}

export async function listProviderRepositories(opts: {
  id: number; page?: number; per_page?: number; search?: string;
}): Promise<{ items: ProviderRepository[]; total: number }> {
  const req = create(ListProviderRepositoriesRequestSchema, {
    id: BigInt(opts.id),
    page: opts.page,
    perPage: opts.per_page,
    search: opts.search,
  });
  const bytes = toBinary(ListProviderRepositoriesRequestSchema, req);
  const respBytes = await getUserCredentialService().listProviderRepositoriesConnect(bytes);
  const resp = fromBinary(ListProviderRepositoriesResponseSchema, new Uint8Array(respBytes));
  return { items: resp.items, total: Number(resp.total) };
}
