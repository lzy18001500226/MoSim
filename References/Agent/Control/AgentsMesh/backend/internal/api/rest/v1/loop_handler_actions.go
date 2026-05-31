package v1

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"time"

	loopDomain "github.com/anthropics/agentsmesh/backend/internal/domain/loop"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	loopService "github.com/anthropics/agentsmesh/backend/internal/service/loop"
	"github.com/anthropics/agentsmesh/backend/pkg/apierr"
	"github.com/gin-gonic/gin"
)

// TriggerLoop manually triggers a loop run.
// POST /api/v1/orgs/:slug/loops/:loop_slug/trigger
func (h *LoopHandler) TriggerLoop(c *gin.Context) {
	tenant := middleware.GetTenant(c)
	loopSlug := c.Param("loop_slug")

	var body struct {
		Variables json.RawMessage `json:"variables"`
	}
	_ = c.ShouldBindJSON(&body)

	loop, err := h.loopService.GetBySlug(c.Request.Context(), tenant.OrganizationID, loopSlug)
	if err != nil {
		if errors.Is(err, loopService.ErrLoopNotFound) {
			apierr.ResourceNotFound(c, "Loop not found")
		} else {
			apierr.InternalError(c, "Failed to get loop")
		}
		return
	}

	result, err := h.orchestrator.TriggerRun(c.Request.Context(), &loopService.TriggerRunRequest{
		LoopID:        loop.ID,
		TriggerType:   loopDomain.RunTriggerManual,
		TriggerSource: "user:" + strconv.FormatInt(tenant.UserID, 10),
		TriggerParams: body.Variables,
	})
	if err != nil {
		if errors.Is(err, loopService.ErrLoopDisabled) {
			apierr.BadRequest(c, apierr.VALIDATION_FAILED, "Loop is disabled")
		} else {
			apierr.InternalError(c, "Failed to trigger loop")
		}
		return
	}

	if result.Skipped {
		c.JSON(http.StatusOK, gin.H{
			"run":     result.Run,
			"skipped": true,
			"reason":  result.Reason,
		})
		return
	}

	// Run start is async — orchestrator handles Pod creation + Autopilot setup.
	// Timeout prevents goroutine leak if Pod creation hangs indefinitely.
	startCtx, startCancel := context.WithTimeout(context.Background(), 5*time.Minute)
	go func() {
		defer startCancel()
		h.orchestrator.StartRun(startCtx, result.Loop, result.Run, tenant.UserID)
	}()

	c.JSON(http.StatusCreated, gin.H{"run": result.Run})
}
