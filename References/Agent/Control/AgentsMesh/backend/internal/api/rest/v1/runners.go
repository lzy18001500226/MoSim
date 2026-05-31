package v1

import (
	"github.com/anthropics/agentsmesh/backend/internal/service/agentpod"
	grantservice "github.com/anthropics/agentsmesh/backend/internal/service/grant"
	runner "github.com/anthropics/agentsmesh/backend/internal/service/runner"
)

// RunnerHandler handles runner-related requests.
// Connect-RPC owns the org-scoped RunnerService surface (CRUD, Upgrade,
// Logs, QuerySandboxes, tokens). The remaining REST handlers here back
// routes_ext.go (third-party API key callers reading runners / available
// runners / runner pods) and the runners_grpc*.go registration flow.
type RunnerHandler struct {
	runnerService  *runner.Service
	podService     *agentpod.PodService
	podCoordinator *runner.PodCoordinator
	versionChecker *runner.VersionChecker
	grantService   *grantservice.Service
}

// NewRunnerHandler creates a new runner handler
func NewRunnerHandler(runnerService *runner.Service, opts ...RunnerHandlerOption) *RunnerHandler {
	h := &RunnerHandler{
		runnerService: runnerService,
	}
	for _, opt := range opts {
		opt(h)
	}
	return h
}

// RunnerHandlerOption is a functional option for configuring RunnerHandler
type RunnerHandlerOption func(*RunnerHandler)

// WithPodServiceForRunner sets the pod service for runner handler
func WithPodServiceForRunner(ps *agentpod.PodService) RunnerHandlerOption {
	return func(h *RunnerHandler) {
		h.podService = ps
	}
}

// WithPodCoordinatorForRunner sets the pod coordinator for runner handler
func WithPodCoordinatorForRunner(pc *runner.PodCoordinator) RunnerHandlerOption {
	return func(h *RunnerHandler) {
		h.podCoordinator = pc
	}
}

// WithVersionChecker sets the version checker for runner handler
func WithVersionChecker(vc *runner.VersionChecker) RunnerHandlerOption {
	return func(h *RunnerHandler) {
		h.versionChecker = vc
	}
}

// WithGrantServiceForRunner sets the grant service for resource sharing
func WithGrantServiceForRunner(gs *grantservice.Service) RunnerHandlerOption {
	return func(h *RunnerHandler) {
		h.grantService = gs
	}
}

// ListRunnerPodsRequest represents request for listing runner pods
type ListRunnerPodsRequest struct {
	Status string `form:"status"`
	Limit  int    `form:"limit"`
	Offset int    `form:"offset"`
}
