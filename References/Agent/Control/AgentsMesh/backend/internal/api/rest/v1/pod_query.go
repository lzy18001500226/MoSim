package v1

import (
	"net/http"
	"strings"

	"github.com/anthropics/agentsmesh/backend/internal/domain/agentpod"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/pkg/apierr"
	"github.com/anthropics/agentsmesh/backend/pkg/policy"
	"github.com/gin-gonic/gin"
)

// ListPodsRequest represents pod list request
type ListPodsRequest struct {
	Status      string `form:"status"`
	CreatedByID int64  `form:"created_by_id"`
	Limit       int    `form:"limit"`
	Offset      int    `form:"offset"`
}

// ListPods lists pods
// GET /api/v1/organizations/:slug/pods
func (h *PodHandler) ListPods(c *gin.Context) {
	var req ListPodsRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		apierr.ValidationError(c, err.Error())
		return
	}

	tenant := middleware.GetTenant(c)

	limit := req.Limit
	if limit == 0 {
		limit = 20
	}

	var statuses []string
	if req.Status != "" {
		statuses = strings.Split(req.Status, ",")
	}

	// Members can only list their own pods; override any user-supplied created_by_id.
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	filter := policy.PodPolicy.ListFilter(sub)
	if filter.OwnerOnly > 0 {
		req.CreatedByID = filter.OwnerOnly
	}

	pods, total, err := h.podService.ListPods(
		c.Request.Context(),
		tenant.OrganizationID,
		agentpod.PodListQuery{
			Statuses:      statuses,
			CreatedByID:   req.CreatedByID,
			GrantedUserID: filter.GrantUserID,
			Limit:         limit,
			Offset:        req.Offset,
		},
	)
	if err != nil {
		apierr.InternalError(c, "Failed to list pods")
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"pods":   pods,
		"total":  total,
		"limit":  limit,
		"offset": req.Offset,
	})
}

// GetPod returns pod by key
// GET /api/v1/organizations/:slug/pods/:key
func (h *PodHandler) GetPod(c *gin.Context) {
	podKey := c.Param("key")

	pod, err := h.podService.GetPod(c.Request.Context(), podKey)
	if err != nil {
		apierr.ResourceNotFound(c, "Pod not found")
		return
	}

	tenant := middleware.GetTenant(c)
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.PodPolicy.AllowRead(sub, h.podResourceWithGrants(c.Request.Context(), podKey, pod.OrganizationID, pod.CreatedByID)) {
		apierr.ForbiddenAccess(c)
		return
	}

	c.JSON(http.StatusOK, gin.H{"pod": pod})
}
