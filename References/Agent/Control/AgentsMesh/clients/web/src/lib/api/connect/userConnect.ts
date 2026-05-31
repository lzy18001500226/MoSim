// Connect-RPC adapter for proto.user.v1 (UserService).
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out per conventions §2.5), decodes
// responses via .fromBinary(). No JSON intermediate.
//
// Returns snake_case web shapes (User, Identity, UserSummary) so existing
// call sites don't need to flip off camelCase + BigInt. Same dual-track
// pattern as invitationConnect.ts during the migration window.

import {
  ChangePasswordRequestSchema,
  ChangePasswordResponseSchema,
  DeleteIdentityRequestSchema,
  DeleteIdentityResponseSchema,
  GetMeRequestSchema,
  ListIdentitiesRequestSchema,
  ListIdentitiesResponseSchema,
  SearchUsersRequestSchema,
  SearchUsersResponseSchema,
  UpdateMeRequestSchema,
  UserSchema,
  type Identity as ProtoIdentity,
  type User as ProtoUser,
  type UserSummary as ProtoUserSummary,
} from "@proto/user/v1/user_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getUserApiService } from "@/lib/wasm-core";

// ============== Snake-case web shapes (call-site facing) ==============

export interface User {
  id: number;
  email: string;
  username: string;
  name?: string;
  avatar_url?: string;
  is_active: boolean;
  is_system_admin: boolean;
  is_email_verified: boolean;
  last_login_at?: string;
  default_git_credential_id?: number;
  created_at: string;
  updated_at: string;
}

export interface Identity {
  id: number;
  user_id: number;
  provider: string;
  provider_user_id: string;
  provider_username?: string;
  token_expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface UserSummary {
  id: number;
  email: string;
  username: string;
  name?: string;
  avatar_url?: string;
}

// ============== Wire conversion (proto -> snake_case web shape) ==============

export function fromProtoUser(p: ProtoUser): User {
  return {
    id: Number(p.id),
    email: p.email,
    username: p.username,
    name: p.name,
    avatar_url: p.avatarUrl,
    is_active: p.isActive,
    is_system_admin: p.isSystemAdmin,
    is_email_verified: p.isEmailVerified,
    last_login_at: p.lastLoginAt,
    default_git_credential_id:
      p.defaultGitCredentialId !== undefined
        ? Number(p.defaultGitCredentialId)
        : undefined,
    created_at: p.createdAt,
    updated_at: p.updatedAt,
  };
}

export function fromProtoIdentity(p: ProtoIdentity): Identity {
  return {
    id: Number(p.id),
    user_id: Number(p.userId),
    provider: p.provider,
    provider_user_id: p.providerUserId,
    provider_username: p.providerUsername,
    token_expires_at: p.tokenExpiresAt,
    created_at: p.createdAt,
    updated_at: p.updatedAt,
  };
}

export function fromProtoUserSummary(p: ProtoUserSummary): UserSummary {
  return {
    id: Number(p.id),
    email: p.email,
    username: p.username,
    name: p.name,
    avatar_url: p.avatarUrl,
  };
}

// ============== UserService — /me ==============

export async function getMe(): Promise<User> {
  const req = create(GetMeRequestSchema, {});
  const bytes = toBinary(GetMeRequestSchema, req);
  const respBytes = await getUserApiService().getMeConnect(bytes);
  return fromProtoUser(fromBinary(UserSchema, new Uint8Array(respBytes)));
}

export async function updateMe(input: {
  name?: string;
  avatar_url?: string;
}): Promise<User> {
  const req = create(UpdateMeRequestSchema, {
    name: input.name,
    avatarUrl: input.avatar_url,
  });
  const bytes = toBinary(UpdateMeRequestSchema, req);
  const respBytes = await getUserApiService().updateMeConnect(bytes);
  return fromProtoUser(fromBinary(UserSchema, new Uint8Array(respBytes)));
}

export async function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<{ message: string }> {
  const req = create(ChangePasswordRequestSchema, {
    currentPassword,
    newPassword,
  });
  const bytes = toBinary(ChangePasswordRequestSchema, req);
  const respBytes = await getUserApiService().changePasswordConnect(bytes);
  const resp = fromBinary(ChangePasswordResponseSchema, new Uint8Array(respBytes));
  return { message: resp.message };
}

// ============== UserService — /me/identities ==============

export async function listIdentities(): Promise<{
  items: Identity[];
  total: number;
  limit: number;
  offset: number;
}> {
  const req = create(ListIdentitiesRequestSchema, {});
  const bytes = toBinary(ListIdentitiesRequestSchema, req);
  const respBytes = await getUserApiService().listIdentitiesConnect(bytes);
  const resp = fromBinary(ListIdentitiesResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProtoIdentity),
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

export async function deleteIdentity(provider: string): Promise<{ message: string }> {
  const req = create(DeleteIdentityRequestSchema, { provider });
  const bytes = toBinary(DeleteIdentityRequestSchema, req);
  const respBytes = await getUserApiService().deleteIdentityConnect(bytes);
  const resp = fromBinary(DeleteIdentityResponseSchema, new Uint8Array(respBytes));
  return { message: resp.message };
}

// ============== UserService — /search ==============

export async function searchUsers(
  q: string,
  limit = 10,
): Promise<{ items: UserSummary[]; total: number; limit: number; offset: number }> {
  const req = create(SearchUsersRequestSchema, { q, limit });
  const bytes = toBinary(SearchUsersRequestSchema, req);
  const respBytes = await getUserApiService().searchUsersConnect(bytes);
  const resp = fromBinary(SearchUsersResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProtoUserSummary),
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}
