// Email/password login via Connect-RPC JSON (proto.auth.v1.AuthService/Login).
// Persists the session blob so dashboard's wasm bootstrap can hydrate the rest
// of the state on the next navigation. SSO-enforced domains surface as a
// Connect `permission_denied` code with a message that contains "SSO" — login
// page maps that to its SSO discovery flow.

import { lightConnect } from "./api-fetch";
import { persistLoginResponse, type AuthLoginResponse } from "./persist";

export interface LightLoginInput {
  email: string;
  password: string;
}

interface ConnectLoginResponse {
  token: string;
  refreshToken: string;
  expiresIn: string | number;
  user?: AuthLoginResponse["user"] & { isEmailVerified?: boolean };
}

function toAuthLoginResponse(resp: ConnectLoginResponse): AuthLoginResponse {
  const u = resp.user;
  return {
    token: resp.token,
    refresh_token: resp.refreshToken,
    expires_in: Number(resp.expiresIn ?? 0) || 0,
    user: u && {
      id: Number(u.id),
      email: u.email,
      username: u.username,
      name: u.name,
      avatar_url: u.avatar_url,
      is_email_verified: u.isEmailVerified ?? u.is_email_verified,
    },
  };
}

export async function lightLogin(input: LightLoginInput): Promise<AuthLoginResponse> {
  const resp = await lightConnect<LightLoginInput, ConnectLoginResponse>(
    "proto.auth.v1.AuthService",
    "Login",
    { email: input.email, password: input.password },
  );
  const adapted = toAuthLoginResponse(resp);
  persistLoginResponse(adapted);
  return adapted;
}
