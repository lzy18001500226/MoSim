package v1

import (
	"net/http"
	"strconv"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	runner "github.com/anthropics/agentsmesh/backend/internal/service/runner"
	"github.com/anthropics/agentsmesh/backend/pkg/apierr"
	"github.com/anthropics/agentsmesh/backend/pkg/policy"
	"github.com/gin-gonic/gin"
)

// ListRunners lists runners in organization
// GET /api/v1/organizations/:slug/runners
func (h *RunnerHandler) ListRunners(c *gin.Context) {
	tenant := middleware.GetTenant(c)

	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	filter := policy.RunnerPolicy.ListFilter(sub)
	runners, err := h.runnerService.ListRunners(c.Request.Context(), tenant.OrganizationID, filter.VisibilityUserID)
	if err != nil {
		apierr.InternalError(c, "Failed to list runners")
		return
	}

	resp := gin.H{"runners": runners}
	if h.versionChecker != nil {
		if latestVersion := h.versionChecker.GetLatestVersion(c.Request.Context()); latestVersion != "" {
			resp["latest_runner_version"] = latestVersion
		}
	}
	c.JSON(http.StatusOK, resp)
}

// GetRunner returns runner by ID
// GET /api/v1/organizations/:slug/runners/:id
func (h *RunnerHandler) GetRunner(c *gin.Context) {
	runnerID, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		apierr.InvalidInput(c, "Invalid runner ID")
		return
	}

	r, err := h.runnerService.GetRunner(c.Request.Context(), runnerID)
	if err != nil {
		apierr.ResourceNotFound(c, "Runner not found")
		return
	}

	tenant := middleware.GetTenant(c)
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.RunnerPolicy.AllowRead(sub, h.runnerResourceWithGrants(
		c.Request.Context(), runnerID, r.OrganizationID, r.RegisteredByUserID, r.Visibility,
	)) {
		apierr.ForbiddenAccess(c)
		return
	}

	var relayConnections []runner.RelayConnectionInfo
	if h.podCoordinator != nil {
		relayConnections = h.podCoordinator.GetRelayConnections(runnerID)
	}

	resp := gin.H{
		"runner":            r,
		"relay_connections": relayConnections,
	}
	if h.versionChecker != nil {
		if latestVersion := h.versionChecker.GetLatestVersion(c.Request.Context()); latestVersion != "" {
			resp["latest_runner_version"] = latestVersion
		}
	}
	c.JSON(http.StatusOK, resp)
}
