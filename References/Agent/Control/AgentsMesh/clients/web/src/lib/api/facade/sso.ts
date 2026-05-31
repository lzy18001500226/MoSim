// SSO API surface — migrated to Connect-RPC (proto.sso.v1.SSOService).
//
// Returns proto types directly — no DTO mapping.

import { discover, ldapAuth } from "../connect/ssoConnect";
export type { SSODiscoverConfig, LdapAuthResponse } from "../connect/ssoConnect";

export const ssoApi = {
  discover: async (email: string) => discover(email),
  ldapAuth: async (
    domain: string,
    data: { username: string; password: string },
  ) => ldapAuth(domain, data.username, data.password),
};

export function getSSOAuthURL(config: { protocol: string; domain: string; provider_url?: string }, redirectUrl?: string): string {
  const base = config.provider_url || "";
  return redirectUrl ? `${base}?redirect=${encodeURIComponent(redirectUrl)}` : base;
}
