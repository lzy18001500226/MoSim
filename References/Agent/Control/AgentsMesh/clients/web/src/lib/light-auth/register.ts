// Sign-up via Connect-RPC JSON (proto.auth.v1.AuthService/Register). Backend
// returns the same token+user shape as Login plus an optional `message`
// describing the verification-email outcome — the (auth) UI does not
// surface that today. Post-register flow redirects to /verify-email and
// waits for the link click before letting the user into the dashboard.

import { lightConnect } from "./api-fetch";
import { persistLoginResponse, type AuthLoginResponse } from "./persist";

export interface LightRegisterInput {
  email: string;
  username: string;
  password: string;
  name: string;
}

interface ConnectRegisterResponse {
  token: string;
  refreshToken: string;
  expiresIn: string | number;
  message?: string;
  user?: {
    id: number | string;
    email: string;
    username: string;
    name?: string;
    avatar_url?: string;
    isEmailVerified?: boolean;
  };
}

function toAuthLoginResponse(resp: ConnectRegisterResponse): AuthLoginResponse {
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
      is_email_verified: u.isEmailVerified,
    },
  };
}

export async function lightRegister(input: LightRegisterInput): Promise<AuthLoginResponse> {
  const resp = await lightConnect<LightRegisterInput, ConnectRegisterResponse>(
    "proto.auth.v1.AuthService",
    "Register",
    input,
  );
  const adapted = toAuthLoginResponse(resp);
  persistLoginResponse(adapted);
  return adapted;
}
