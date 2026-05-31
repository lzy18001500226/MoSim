package v1

import (
	"errors"
	"net/http"

	"github.com/anthropics/agentsmesh/backend/internal/service/runner"
	"github.com/anthropics/agentsmesh/backend/pkg/apierr"
	"github.com/gin-gonic/gin"
)

// ==================== Interactive Registration (Tailscale-style) ====================
//
// `GET /runners/grpc/auth-status` and `POST /orgs/:slug/runners/grpc/authorize`
// migrated to proto.runner_api.v1.RunnerPublicService.GetRunnerAuthStatus +
// proto.runner_api.v1.RunnerService.AuthorizeRunner (Connect). The
// `auth-url` bootstrap stays on REST — runner CLI can't embed wasm and
// initiates the handshake from outside the browser session.

// RequestAuthURL creates a pending auth request and returns an authorization URL.
// POST /api/v1/runners/grpc/auth-url
// No authentication required - Runner initiates registration.
func (h *GRPCRunnerHandler) RequestAuthURL(c *gin.Context) {
	var req RequestAuthURLRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		apierr.ValidationError(c, err.Error())
		return
	}

	// FrontendURL is derived from PrimaryDomain
	frontendURL := h.config.FrontendURL()

	resp, err := h.runnerService.RequestAuthURL(c.Request.Context(), &runner.RequestAuthURLRequest{
		MachineKey: req.MachineKey,
		NodeID:     req.NodeID,
		Labels:     req.Labels,
	}, frontendURL)
	if err != nil {
		apierr.InternalError(c, "Failed to create auth request")
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"auth_url":   resp.AuthURL,
		"auth_key":   resp.AuthKey,
		"expires_in": resp.ExpiresIn,
	})
}

// `unused` placeholder so callers of errors / runner pkg don't break when
// the migrated handlers above are no longer in this file. Both packages
// are still touched by RequestAuthURL above.
var (
	_ = errors.Is
	_ = runner.ErrAuthRequestNotFound
)
