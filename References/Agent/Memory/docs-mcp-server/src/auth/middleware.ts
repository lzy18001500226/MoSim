/**
 * Fastify middleware for OAuth2/OIDC authentication using ProxyAuthManager.
 * Provides binary authentication (authenticated vs not authenticated) for MCP endpoints.
 */

import type { FastifyReply, FastifyRequest } from "fastify";
import { logger } from "../utils/logger";
import type { ProxyAuthManager } from "./ProxyAuthManager";
import type { AuthContext } from "./types";

// Type for Fastify request with auth context
type AuthenticatedRequest = FastifyRequest & { auth: AuthContext };

/**
 * Create authentication middleware that validates Bearer tokens using ProxyAuthManager.
 */
export function createAuthMiddleware(authManager: ProxyAuthManager) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const authContext = await authManager.createAuthContext(
        request.headers.authorization || "",
        request,
      );

      // Always set auth context on request
      (request as AuthenticatedRequest).auth = authContext;

      // Check if authentication is enabled by looking at the config
      const isAuthEnabled = authManager.authConfig.enabled;

      if (!isAuthEnabled) {
        // Auth is disabled - allow all requests through
        logger.debug("Authentication disabled, allowing request");
        return;
      }

      // Auth is enabled - validate authentication
      if (!authContext.authenticated) {
        const hasAuthHeader = !!request.headers.authorization;

        if (hasAuthHeader) {
          // Auth is enabled but token is invalid
          logger.debug("Token validation failed");
          reply
            .status(401)
            .header(
              "WWW-Authenticate",
              'Bearer realm="MCP Server", error="invalid_token"',
            )
            .send({
              error: "invalid_token",
              error_description: "The access token is invalid",
            });
          return;
        } else {
          // Auth is enabled but no authorization header provided
          logger.debug("Missing authorization header");
          reply.status(401).header("WWW-Authenticate", 'Bearer realm="MCP Server"').send({
            error: "unauthorized",
            error_description: "Authorization header required",
          });
          return;
        }
      }

      // Authentication successful
      logger.debug(
        `Authentication successful for subject: ${authContext.subject || "anonymous"}`,
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Authentication failed";
      logger.debug(`Authentication error: ${message}`);

      reply
        .status(401)
        .header("WWW-Authenticate", 'Bearer realm="MCP Server", error="invalid_token"')
        .send({
          error: "invalid_token",
          error_description: "Token validation failed",
        });
    }
  };
}
