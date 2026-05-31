package podconnect

import (
	"context"
	"errors"
	"strings"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/grant"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/internal/service/agentpod"
	"github.com/anthropics/agentsmesh/backend/pkg/policy"
	podv1 "github.com/anthropics/agentsmesh/proto/gen/go/pod/v1"
)

// CreatePod — REST analogue: POST /api/v1/organizations/:slug/pods.
// Returns the multi-field {pod, warning?} envelope locked by 986a38ca6.
// The warning surfaces quota-near limits without blocking pod creation.
func (s *Server) CreatePod(
	ctx context.Context, req *connect.Request[podv1.CreatePodRequest],
) (*connect.Response[podv1.CreatePodResponse], error) {
	if s.orchestrator == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("pod orchestrator not configured"))
	}
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	alias := normalizeAlias(req.Msg.Alias)
	if err := validateAlias(alias); err != nil {
		return nil, err
	}

	orchReq := &agentpod.OrchestrateCreatePodRequest{
		OrganizationID:      tenant.OrganizationID,
		UserID:              tenant.UserID,
		RunnerID:            req.Msg.GetRunnerId(),
		AgentSlug:           req.Msg.GetAgentSlug(),
		RepositoryID:        optionalInt64(req.Msg.RepositoryId),
		TicketSlug:          optionalString(req.Msg.TicketSlug),
		Alias:               alias,
		AgentfileLayer:      optionalString(req.Msg.AgentfileLayer),
		Cols:                req.Msg.GetCols(),
		Rows:                req.Msg.GetRows(),
		SourcePodKey:        req.Msg.GetSourcePodKey(),
		ResumeAgentSession:  optionalBool(req.Msg.ResumeAgentSession),
		Perpetual:           req.Msg.GetPerpetual(),
	}

	result, err := s.orchestrator.CreatePod(ctx, orchReq)
	if err != nil {
		return nil, mapServiceError(err)
	}

	resp := &podv1.CreatePodResponse{Pod: ToProtoPod(result.Pod)}
	if result.Warning != "" {
		w := result.Warning
		resp.Warning = &w
	}
	return connect.NewResponse(resp), nil
}

// TerminatePod — REST analogue: POST /api/v1/organizations/:slug/pods/:key/terminate.
func (s *Server) TerminatePod(
	ctx context.Context, req *connect.Request[podv1.TerminatePodRequest],
) (*connect.Response[podv1.TerminatePodResponse], error) {
	if s.podCoordinator == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("pod coordinator not configured"))
	}
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	podKey := req.Msg.GetPodKey()

	pod, err := s.podSvc.GetPod(ctx, podKey)
	if err != nil {
		return nil, mapServiceError(err)
	}
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.PodPolicy.AllowWrite(sub, s.podResourceWithGrants(ctx, podKey, pod.OrganizationID, pod.CreatedByID)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}

	if err := s.podCoordinator.TerminatePod(ctx, podKey); err != nil {
		return nil, mapServiceError(err)
	}
	if s.grantSvc != nil {
		_ = s.grantSvc.CleanupByResource(ctx, grant.TypePod, podKey)
	}
	return connect.NewResponse(&podv1.TerminatePodResponse{Message: "Pod terminated"}), nil
}

// UpdatePodAlias — REST analogue: PATCH /api/v1/organizations/:slug/pods/:key/alias.
// Alias presence carries clear semantics: absent = no change, empty string = clear.
func (s *Server) UpdatePodAlias(
	ctx context.Context, req *connect.Request[podv1.UpdatePodAliasRequest],
) (*connect.Response[podv1.UpdatePodAliasResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	podKey := req.Msg.GetPodKey()

	pod, err := s.podSvc.GetPod(ctx, podKey)
	if err != nil {
		return nil, mapServiceError(err)
	}
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.PodPolicy.AllowWrite(sub, s.podResourceWithGrants(ctx, podKey, pod.OrganizationID, pod.CreatedByID)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}

	alias := optionalString(req.Msg.Alias)
	if alias != nil && strings.TrimSpace(*alias) == "" {
		alias = nil
	}
	if alias != nil && len(*alias) > 100 {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("alias must be 100 characters or less"))
	}

	if err := s.podSvc.UpdateAlias(ctx, podKey, alias); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&podv1.UpdatePodAliasResponse{Message: "Pod alias updated"}), nil
}

// UpdatePodPerpetual — REST analogue: PATCH /api/v1/organizations/:slug/pods/:key/perpetual.
// Members can only edit their own pods; owner/admin can edit any in the org.
func (s *Server) UpdatePodPerpetual(
	ctx context.Context, req *connect.Request[podv1.UpdatePodPerpetualRequest],
) (*connect.Response[podv1.UpdatePodPerpetualResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	podKey := req.Msg.GetPodKey()

	pod, err := s.podSvc.GetPod(ctx, podKey)
	if err != nil {
		return nil, mapServiceError(err)
	}
	if pod.OrganizationID != tenant.OrganizationID {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}
	if pod.CreatedByID != tenant.UserID && tenant.UserRole == "member" {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("admin role required"))
	}

	perpetual := req.Msg.GetPerpetual()
	if err := s.podSvc.UpdatePerpetual(ctx, podKey, perpetual); err != nil {
		return nil, mapServiceError(err)
	}
	if s.commandSender != nil {
		_ = s.commandSender.SendUpdatePodPerpetual(ctx, pod.RunnerID, podKey, perpetual)
	}
	return connect.NewResponse(&podv1.UpdatePodPerpetualResponse{Message: "Pod perpetual mode updated"}), nil
}

// SendPodPrompt — REST analogue: POST /api/v1/orgs/:slug/pods/:key/prompt.
// Mode-transparent: PTY writes to stdin, ACP forwards via protocol.
func (s *Server) SendPodPrompt(
	ctx context.Context, req *connect.Request[podv1.SendPodPromptRequest],
) (*connect.Response[podv1.SendPodPromptResponse], error) {
	if s.commandSender == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("command sender not configured"))
	}
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	podKey := req.Msg.GetPodKey()

	pod, err := s.podSvc.GetPod(ctx, podKey)
	if err != nil {
		return nil, mapServiceError(err)
	}
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.PodPolicy.AllowWrite(sub, s.podResourceWithGrants(ctx, podKey, pod.OrganizationID, pod.CreatedByID)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}
	if !pod.IsActive() {
		return nil, connect.NewError(connect.CodeFailedPrecondition, errors.New("pod is not active"))
	}

	prompt := req.Msg.GetPrompt()
	if prompt == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("prompt is required"))
	}

	if err := s.commandSender.SendPrompt(ctx, pod.RunnerID, podKey, prompt); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&podv1.SendPodPromptResponse{Status: "sent"}), nil
}

// --- helpers ---

func normalizeAlias(p *string) *string {
	if p == nil {
		return nil
	}
	trimmed := strings.TrimSpace(*p)
	if trimmed == "" {
		return nil
	}
	return &trimmed
}

func validateAlias(p *string) error {
	if p != nil && len(*p) > 100 {
		return connect.NewError(connect.CodeInvalidArgument, errors.New("alias must be 100 characters or less"))
	}
	return nil
}

func optionalString(p *string) *string {
	if p == nil {
		return nil
	}
	v := *p
	return &v
}

func optionalInt64(p *int64) *int64 {
	if p == nil {
		return nil
	}
	v := *p
	return &v
}

func optionalBool(p *bool) *bool {
	if p == nil {
		return nil
	}
	v := *p
	return &v
}
