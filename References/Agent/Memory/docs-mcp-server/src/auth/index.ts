/**
 * OAuth2/OIDC authentication module for MCP Authorization spec compliance.
 *
 * This module provides optional OAuth2/OIDC authentication for MCP endpoints
 * while keeping local usage frictionless (auth disabled by default).
 */

export { createAuthMiddleware } from "./middleware";
export { ProxyAuthManager } from "./ProxyAuthManager";
export type {
  AuthConfig,
  AuthContext,
} from "./types";
