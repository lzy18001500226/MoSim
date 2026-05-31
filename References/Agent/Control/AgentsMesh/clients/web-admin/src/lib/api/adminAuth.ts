// Connect-RPC adapter for proto.admin.v1.AdminAuthService.Login (PUBLIC)
// and AdminAuthSessionService.GetMe (auth-required). Replaces the
// previous REST POST /admin/auth/login + GET /admin/me calls.
import {
  AdminAuthService,
  AdminAuthSessionService,
  AdminLoginRequestSchema,
  AdminLoginResponseSchema,
  AdminUserSchema,
  GetMeRequestSchema,
  type AdminLoginResponse as ProtoAdminLoginResponse,
  type AdminUser as ProtoAdminUser,
} from "@proto/admin/v1/admin_pb";

import { callConnect } from "@/lib/connect/transport";
import { AdminUser } from "@/stores/auth";
import type { LoginRequest, LoginResponse } from "./adminTypesExtended";

void AdminAuthService;
void AdminAuthSessionService;

const LOGIN_SERVICE = "proto.admin.v1.AdminAuthService";
const SESSION_SERVICE = "proto.admin.v1.AdminAuthSessionService";

function fromProtoAdminUser(p: ProtoAdminUser): AdminUser {
  return {
    id: Number(p.id),
    email: p.email,
    username: p.username,
    name: p.name ?? null,
    avatar_url: p.avatarUrl ?? null,
    is_system_admin: p.isSystemAdmin,
  };
}

export async function login(req: LoginRequest): Promise<LoginResponse> {
  const resp = (await callConnect(
    LOGIN_SERVICE,
    "Login",
    AdminLoginRequestSchema,
    AdminLoginResponseSchema,
    { email: req.email, password: req.password },
  )) as ProtoAdminLoginResponse;
  return {
    token: resp.token,
    refresh_token: resp.refreshToken,
    user: resp.user
      ? fromProtoAdminUser(resp.user)
      : ({ id: 0, email: "", username: "", name: null, avatar_url: null, is_system_admin: false }),
  };
}

export async function getCurrentAdmin(): Promise<AdminUser> {
  const resp = (await callConnect(
    SESSION_SERVICE,
    "GetMe",
    GetMeRequestSchema,
    AdminUserSchema,
    {},
  )) as ProtoAdminUser;
  return fromProtoAdminUser(resp);
}
