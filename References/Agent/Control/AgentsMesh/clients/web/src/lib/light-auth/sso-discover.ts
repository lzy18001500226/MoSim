// SSO discovery (find configured providers for an email domain) and the
// LDAP password flow. Discovery returns a list of provider configs that the
// login page renders as either redirect buttons (OIDC/SAML) or an LDAP
// username/password form. The login page wires the redirect buttons against
// getOAuthBaseUrl()/api/v1/auth/sso/<domain>/<protocol> separately — those
// are GET browser-redirect endpoints (HTML, not JSON), so they stay on
// REST permanently.

import { lightConnect } from "./api-fetch";
import { persistLoginResponse, type AuthLoginResponse } from "./persist";
import type { SSODiscoverConfig } from "@/lib/api/connect/ssoConnect";

interface ConnectDiscoverResponse {
  items?: SSODiscoverConfig[];
}

export async function lightDiscoverSSO(email: string): Promise<SSODiscoverConfig[]> {
  if (!email || !email.includes("@")) return [];
  try {
    const resp = await lightConnect<{ email: string }, ConnectDiscoverResponse>(
      "proto.sso.v1.SSOService",
      "Discover",
      { email },
    );
    return resp?.items ?? [];
  } catch {
    return [];
  }
}

export interface LightLdapAuthInput {
  domain: string;
  username: string;
  password: string;
}

interface ConnectLdapAuthResponse {
  token: string;
  refreshToken: string;
  expiresAt?: string;
  tokenType?: string;
  user?: {
    id: number | string;
    email: string;
    username: string;
    name?: string;
  };
}

export async function lightLdapAuth(input: LightLdapAuthInput): Promise<AuthLoginResponse> {
  const resp = await lightConnect<LightLdapAuthInput, ConnectLdapAuthResponse>(
    "proto.sso.v1.SSOService",
    "LdapAuth",
    input,
  );
  // expires_at is an RFC3339 timestamp; convert to "seconds until expiry"
  // so persistLoginResponse can compute the absolute expires_at downstream.
  const now = Math.floor(Date.now() / 1000);
  const expiresAtSec = resp.expiresAt ? Math.floor(new Date(resp.expiresAt).getTime() / 1000) : 0;
  const expiresIn = expiresAtSec > now ? expiresAtSec - now : 3600;
  const u = resp.user;
  const adapted: AuthLoginResponse = {
    token: resp.token,
    refresh_token: resp.refreshToken,
    expires_in: expiresIn,
    user: u && {
      id: Number(u.id),
      email: u.email,
      username: u.username,
      name: u.name,
    },
  };
  persistLoginResponse(adapted);
  return adapted;
}
