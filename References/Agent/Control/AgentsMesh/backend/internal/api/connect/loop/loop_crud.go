package loopconnect

import (
	"context"
	"encoding/json"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	loopsvc "github.com/anthropics/agentsmesh/backend/internal/service/loop"
	loopv1 "github.com/anthropics/agentsmesh/proto/gen/go/loop/v1"
)

func jsonRawFromString(s string) json.RawMessage {
	if s == "" {
		return json.RawMessage("{}")
	}
	return json.RawMessage(s)
}

// CreateLoop — REST analogue: POST /loops.
func (s *Server) CreateLoop(
	ctx context.Context, req *connect.Request[loopv1.CreateLoopRequest],
) (*connect.Response[loopv1.Loop], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if s.svc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("loop service not configured"))
	}
	tenant := middleware.GetTenant(ctx)
	m := req.Msg

	maxConcurrent := 1
	if v := m.GetMaxConcurrentRuns(); m.MaxConcurrentRuns != nil {
		maxConcurrent = int(v)
	}
	if maxConcurrent < 1 || maxConcurrent > 10 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("max_concurrent_runs must be between 1 and 10"))
	}
	maxRetained := 0
	if m.MaxRetainedRuns != nil {
		maxRetained = int(m.GetMaxRetainedRuns())
	}
	if maxRetained < 0 || maxRetained > 10000 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("max_retained_runs must be between 0 and 10000"))
	}
	timeoutMin := 60
	if m.TimeoutMinutes != nil {
		timeoutMin = int(m.GetTimeoutMinutes())
	}
	if timeoutMin < 1 || timeoutMin > 1440 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("timeout_minutes must be between 1 and 1440"))
	}
	sessionPersist := true
	if m.SessionPersistence != nil {
		sessionPersist = m.GetSessionPersistence()
	}
	idleTimeout := 30
	if m.IdleTimeoutSec != nil {
		idleTimeout = int(m.GetIdleTimeoutSec())
	}
	if idleTimeout < 0 || idleTimeout > 3600 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("idle_timeout_sec must be between 0 and 3600"))
	}

	svcReq := &loopsvc.CreateLoopRequest{
		OrganizationID:      tenant.OrganizationID,
		CreatedByID:         tenant.UserID,
		Name:                m.GetName(),
		Slug:                m.GetSlug(),
		AgentSlug:           m.GetAgentSlug(),
		PermissionMode:      m.GetPermissionMode(),
		PromptTemplate:      m.GetPromptTemplate(),
		PromptVariables:     jsonRawFromString(m.GetPromptVariablesJson()),
		ConfigOverrides:     jsonRawFromString(m.GetConfigOverridesJson()),
		AutopilotConfig:     jsonRawFromString(m.GetAutopilotConfigJson()),
		RepositoryID:        m.RepositoryId,
		RunnerID:            m.RunnerId,
		TicketID:            m.TicketId,
		UsedEnvBundles:      m.GetUsedEnvBundles(),
		ExecutionMode:       m.GetExecutionMode(),
		SandboxStrategy:     m.GetSandboxStrategy(),
		SessionPersistence:  sessionPersist,
		ConcurrencyPolicy:   m.GetConcurrencyPolicy(),
		MaxConcurrentRuns:   maxConcurrent,
		MaxRetainedRuns:     maxRetained,
		TimeoutMinutes:      timeoutMin,
		IdleTimeoutSec:      idleTimeout,
	}
	if v := m.GetDescription(); v != "" {
		svcReq.Description = &v
	}
	if v := m.GetBranchName(); v != "" {
		svcReq.BranchName = &v
	}
	if v := m.GetCronExpression(); v != "" {
		svcReq.CronExpression = &v
	}
	if v := m.GetCallbackUrl(); v != "" {
		svcReq.CallbackURL = &v
	}

	loop, err := s.svc.Create(ctx, svcReq)
	if err != nil {
		switch {
		case errors.Is(err, loopsvc.ErrDuplicateSlug):
			return nil, connect.NewError(connect.CodeAlreadyExists, errors.New("loop slug already exists"))
		case errors.Is(err, loopsvc.ErrInvalidSlug):
			return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid slug format"))
		case errors.Is(err, loopsvc.ErrInvalidCron):
			return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid cron expression"))
		case errors.Is(err, loopsvc.ErrInvalidCallbackURL),
			errors.Is(err, loopsvc.ErrInvalidEnumValue):
			return nil, connect.NewError(connect.CodeInvalidArgument, err)
		default:
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	}
	return connect.NewResponse(toProtoLoop(loop)), nil
}

// UpdateLoop — REST analogue: PUT /loops/:slug.
func (s *Server) UpdateLoop(
	ctx context.Context, req *connect.Request[loopv1.UpdateLoopRequest],
) (*connect.Response[loopv1.Loop], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if s.svc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("loop service not configured"))
	}
	if req.Msg.GetLoopSlug() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("loop_slug is required"))
	}
	if err := validateUpdateBounds(req.Msg); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	svcReq := buildUpdateRequest(req.Msg)

	loop, err := s.svc.Update(ctx, tenant.OrganizationID, req.Msg.GetLoopSlug(), svcReq)
	if err != nil {
		switch {
		case errors.Is(err, loopsvc.ErrLoopNotFound):
			return nil, connect.NewError(connect.CodeNotFound, errors.New("loop not found"))
		case errors.Is(err, loopsvc.ErrInvalidCron):
			return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid cron expression"))
		case errors.Is(err, loopsvc.ErrInvalidCallbackURL),
			errors.Is(err, loopsvc.ErrInvalidEnumValue):
			return nil, connect.NewError(connect.CodeInvalidArgument, err)
		default:
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	}
	return connect.NewResponse(toProtoLoop(loop)), nil
}

func validateUpdateBounds(m *loopv1.UpdateLoopRequest) error {
	if m.MaxConcurrentRuns != nil {
		v := int(m.GetMaxConcurrentRuns())
		if v < 1 || v > 10 {
			return connect.NewError(connect.CodeInvalidArgument,
				errors.New("max_concurrent_runs must be between 1 and 10"))
		}
	}
	if m.TimeoutMinutes != nil {
		v := int(m.GetTimeoutMinutes())
		if v < 1 || v > 1440 {
			return connect.NewError(connect.CodeInvalidArgument,
				errors.New("timeout_minutes must be between 1 and 1440"))
		}
	}
	if m.MaxRetainedRuns != nil {
		v := int(m.GetMaxRetainedRuns())
		if v < 0 || v > 10000 {
			return connect.NewError(connect.CodeInvalidArgument,
				errors.New("max_retained_runs must be between 0 and 10000"))
		}
	}
	if m.IdleTimeoutSec != nil {
		v := int(m.GetIdleTimeoutSec())
		if v < 0 || v > 3600 {
			return connect.NewError(connect.CodeInvalidArgument,
				errors.New("idle_timeout_sec must be between 0 and 3600"))
		}
	}
	return nil
}

func buildUpdateRequest(m *loopv1.UpdateLoopRequest) *loopsvc.UpdateLoopRequest {
	r := &loopsvc.UpdateLoopRequest{
		AgentSlug:           m.GetAgentSlug(),
		Name:                m.Name,
		Description:         m.Description,
		PermissionMode:      m.PermissionMode,
		PromptTemplate:      m.PromptTemplate,
		ExecutionMode:       m.ExecutionMode,
		CronExpression:      m.CronExpression,
		CallbackURL:         m.CallbackUrl,
		SandboxStrategy:     m.SandboxStrategy,
		SessionPersistence:  m.SessionPersistence,
		ConcurrencyPolicy:   m.ConcurrencyPolicy,
		BranchName:          m.BranchName,
		RepositoryID:        m.RepositoryId,
		RunnerID:            m.RunnerId,
		TicketID:            m.TicketId,
	}
	if pv := m.GetPromptVariablesJson(); pv != "" {
		r.PromptVariables = jsonRawFromString(pv)
	}
	if co := m.GetConfigOverridesJson(); co != "" {
		r.ConfigOverrides = jsonRawFromString(co)
	}
	if ac := m.GetAutopilotConfigJson(); ac != "" {
		r.AutopilotConfig = jsonRawFromString(ac)
	}
	if m.MaxConcurrentRuns != nil {
		v := int(m.GetMaxConcurrentRuns())
		r.MaxConcurrentRuns = &v
	}
	if m.MaxRetainedRuns != nil {
		v := int(m.GetMaxRetainedRuns())
		r.MaxRetainedRuns = &v
	}
	if m.TimeoutMinutes != nil {
		v := int(m.GetTimeoutMinutes())
		r.TimeoutMinutes = &v
	}
	if m.IdleTimeoutSec != nil {
		v := int(m.GetIdleTimeoutSec())
		r.IdleTimeoutSec = &v
	}
	if m.UsedEnvBundles != nil {
		// Wrapper presence => caller intends to replace. Empty inner list clears.
		names := m.GetUsedEnvBundles().GetNames()
		if names == nil {
			names = []string{}
		}
		r.UsedEnvBundles = &names
	}
	return r
}
