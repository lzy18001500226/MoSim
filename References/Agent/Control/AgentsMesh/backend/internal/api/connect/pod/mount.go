package podconnect

import (
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/service/agentpod"
	"github.com/anthropics/agentsmesh/backend/internal/service/billing"
	"github.com/anthropics/agentsmesh/backend/internal/service/runner"
)

// Mount registers all PodService procedures on mux behind the auth
// interceptor supplied via opts (see cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListPodsProcedure, connect.NewUnaryHandler(
		ListPodsProcedure, srv.ListPods, opts...,
	))
	mux.Handle(GetPodProcedure, connect.NewUnaryHandler(
		GetPodProcedure, srv.GetPod, opts...,
	))
	mux.Handle(CreatePodProcedure, connect.NewUnaryHandler(
		CreatePodProcedure, srv.CreatePod, opts...,
	))
	mux.Handle(TerminatePodProcedure, connect.NewUnaryHandler(
		TerminatePodProcedure, srv.TerminatePod, opts...,
	))
	mux.Handle(UpdatePodAliasProcedure, connect.NewUnaryHandler(
		UpdatePodAliasProcedure, srv.UpdatePodAlias, opts...,
	))
	mux.Handle(UpdatePodPerpetualProcedure, connect.NewUnaryHandler(
		UpdatePodPerpetualProcedure, srv.UpdatePodPerpetual, opts...,
	))
	mux.Handle(GetPodConnectionProcedure, connect.NewUnaryHandler(
		GetPodConnectionProcedure, srv.GetPodConnection, opts...,
	))
	mux.Handle(SendPodPromptProcedure, connect.NewUnaryHandler(
		SendPodPromptProcedure, srv.SendPodPrompt, opts...,
	))
	mux.Handle(ListPodsByTicketProcedure, connect.NewUnaryHandler(
		ListPodsByTicketProcedure, srv.ListPodsByTicket, opts...,
	))
}

// mapServiceError translates agentpod / runner / billing sentinels to
// Connect codes per conventions §10. Mirrors mapOrchestratorErrorToHTTP in
// v1/pod_create.go and the apierr.* calls in v1/pod_*.go handlers.
func mapServiceError(err error) error {
	if err == nil {
		return nil
	}
	switch {
	// Validation → InvalidArgument
	case errors.Is(err, agentpod.ErrMissingRunnerID),
		errors.Is(err, agentpod.ErrMissingAgentSlug),
		errors.Is(err, agentpod.ErrSourcePodNotTerminated),
		errors.Is(err, agentpod.ErrResumeRunnerMismatch),
		errors.Is(err, agentpod.ErrUnsupportedInteractionMode),
		errors.Is(err, agentpod.ErrInvalidAgentfileLayer):
		return connect.NewError(connect.CodeInvalidArgument, err)

	// Billing → ResourceExhausted / FailedPrecondition
	case errors.Is(err, billing.ErrQuotaExceeded):
		return connect.NewError(connect.CodeResourceExhausted, err)
	case errors.Is(err, billing.ErrSubscriptionFrozen):
		return connect.NewError(connect.CodeFailedPrecondition, err)

	// Access → PermissionDenied
	case errors.Is(err, agentpod.ErrSourcePodAccessDenied):
		return connect.NewError(connect.CodePermissionDenied, err)

	// Not found → NotFound
	case errors.Is(err, agentpod.ErrPodNotFound),
		errors.Is(err, agentpod.ErrSourcePodNotFound):
		return connect.NewError(connect.CodeNotFound, err)

	// Conflict → AlreadyExists
	case errors.Is(err, agentpod.ErrSourcePodAlreadyResumed),
		errors.Is(err, agentpod.ErrSandboxAlreadyResumed):
		return connect.NewError(connect.CodeAlreadyExists, err)

	// Runner unavailability → Unavailable
	case errors.Is(err, agentpod.ErrNoAvailableRunner),
		errors.Is(err, agentpod.ErrRunnerDispatchFailed),
		errors.Is(err, runner.ErrPodAlreadyTerminated):
		return connect.NewError(connect.CodeUnavailable, err)

	// Config build failure → Internal
	case errors.Is(err, agentpod.ErrConfigBuildFailed):
		return connect.NewError(connect.CodeInternal, err)

	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
