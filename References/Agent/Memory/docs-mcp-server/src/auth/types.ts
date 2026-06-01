/**
 * OAuth2/OIDC authentication types and interfaces for MCP Authorization spec compliance.
 * Simplified to use binary authentication (authenticated vs not authenticated).
 */

/** OAuth2/OIDC authentication configuration */
export interface AuthConfig {
  /** Enable OAuth2/OIDC authentication */
  enabled: boolean;
  /** Issuer/discovery URL for the OAuth2/OIDC provider */
  issuerUrl?: string;
  /** JWT audience claim (identifies this protected resource) */
  audience?: string;
  /** Standard OAuth2 scopes (e.g., "openid", "profile", "email") */
  scopes: string[];
}

/** Authentication context for requests */
export interface AuthContext {
  /** Whether the request is authenticated */
  authenticated: boolean;
  /** Effective scopes for the authenticated user (always "*" for authenticated users) */
  scopes: Set<"*">;
  /** Subject identifier from the token */
  subject?: string;
}
