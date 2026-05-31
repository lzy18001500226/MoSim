// /verify-email and /resend-verification over Connect-RPC JSON. VerifyEmail
// returns a fresh token pair (so the user is logged in after confirming);
// ResendVerification returns a status message only.

import { lightConnect } from "./api-fetch";
import { persistLoginResponse, type AuthLoginResponse } from "./persist";

interface ConnectVerifyEmailResponse {
  token: string;
  refreshToken: string;
  expiresIn: string | number;
  user?: {
    id: number | string;
    email: string;
    username: string;
    name?: string;
    avatar_url?: string;
    isEmailVerified?: boolean;
  };
}

export async function lightVerifyEmail(token: string): Promise<AuthLoginResponse> {
  const resp = await lightConnect<{ token: string }, ConnectVerifyEmailResponse>(
    "proto.auth.v1.AuthService",
    "VerifyEmail",
    { token },
  );
  const u = resp.user;
  const adapted: AuthLoginResponse = {
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
  persistLoginResponse(adapted);
  return adapted;
}

export async function lightResendVerification(email: string): Promise<void> {
  await lightConnect<{ email: string }, unknown>(
    "proto.auth.v1.AuthService",
    "ResendVerification",
    { email },
  );
}
