package runnerconnect

import (
	"context"
	"errors"
	"log/slog"

	"connectrpc.com/connect"
	"github.com/google/uuid"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/pkg/policy"
	runnerapiv1 "github.com/anthropics/agentsmesh/proto/gen/go/runner_api/v1"
)

// Operational handlers — long-running side effects on a registered runner:
// upgrade orchestration, log upload requests + history, sandbox query. CRUD
// of the runner record itself lives in handlers_crud.go; token management
// in handlers_tokens.go.

func (s *Server) UpgradeRunner(
	ctx context.Context, req *connect.Request[runnerapiv1.UpgradeRunnerRequest],
) (*connect.Response[runnerapiv1.UpgradeRunnerResponse], error) {
	if s.upgradeSender == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("upgrade service not configured"))
	}
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	runnerID := req.Msg.GetId()
	r, err := s.runnerSvc.GetRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.RunnerPolicy.AllowWrite(sub, policy.VisibleResource(
		r.OrganizationID, r.RegisteredByUserID, r.Visibility,
	)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}
	if req.Msg.GetForce() {
		slog.WarnContext(ctx, "Deprecated 'force' field received - ignored", "runner_id", runnerID, "user_id", tenant.UserID)
	}
	if !s.upgradeSender.IsConnected(runnerID) {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("runner is not connected"))
	}
	requestID := uuid.New().String()
	// force=true: Poddaemon keeps pods alive across restart.
	if err := s.upgradeSender.SendUpgradeRunner(runnerID, requestID, req.Msg.GetTargetVersion(), true); err != nil {
		if st, ok := status.FromError(err); ok && st.Code() == codes.NotFound {
			return nil, connect.NewError(connect.CodeUnavailable, errors.New("runner disconnected before command could be sent"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	slog.InfoContext(ctx, "Runner upgrade initiated",
		"runner_id", runnerID,
		"request_id", requestID,
		"target_version", req.Msg.GetTargetVersion(),
		"active_pod_count", r.CurrentPods,
		"user_id", tenant.UserID,
		"org_id", tenant.OrganizationID,
	)
	return connect.NewResponse(&runnerapiv1.UpgradeRunnerResponse{
		RequestId: requestID,
		Message:   "Upgrade command sent to runner",
	}), nil
}

func (s *Server) RequestLogUpload(
	ctx context.Context, req *connect.Request[runnerapiv1.RequestLogUploadRequest],
) (*connect.Response[runnerapiv1.RequestLogUploadResponse], error) {
	if s.logUploadSender == nil || s.logUploadSvc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("log upload service not configured"))
	}
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	runnerID := req.Msg.GetId()
	r, err := s.runnerSvc.GetRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.RunnerPolicy.AllowRead(sub, policy.VisibleResource(
		r.OrganizationID, r.RegisteredByUserID, r.Visibility,
	)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}
	if !s.logUploadSender.IsConnected(runnerID) {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("runner is not connected"))
	}
	uploadReq, err := s.logUploadSvc.RequestUpload(ctx, tenant.OrganizationID, runnerID, tenant.UserID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	if err := s.logUploadSender.SendUploadLogs(runnerID, uploadReq.RequestID, uploadReq.PresignedURL, uploadReq.ExpiresAt); err != nil {
		s.logUploadSvc.MarkFailed(uploadReq.RequestID, "failed to send command to runner")
		if st, ok := status.FromError(err); ok && st.Code() == codes.NotFound {
			return nil, connect.NewError(connect.CodeUnavailable, errors.New("runner disconnected before command could be sent"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	slog.InfoContext(ctx, "Log upload requested",
		"runner_id", runnerID,
		"request_id", uploadReq.RequestID,
		"user_id", tenant.UserID,
		"org_id", tenant.OrganizationID,
	)
	return connect.NewResponse(&runnerapiv1.RequestLogUploadResponse{
		RequestId: uploadReq.RequestID,
		Message:   "Log upload command sent to runner",
	}), nil
}

func (s *Server) ListRunnerLogs(
	ctx context.Context, req *connect.Request[runnerapiv1.ListRunnerLogsRequest],
) (*connect.Response[runnerapiv1.ListRunnerLogsResponse], error) {
	if s.logUploadSvc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("log upload service not configured"))
	}
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	runnerID := req.Msg.GetId()
	r, err := s.runnerSvc.GetRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.RunnerPolicy.AllowRead(sub, policy.VisibleResource(
		r.OrganizationID, r.RegisteredByUserID, r.Visibility,
	)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}
	limit := int(req.Msg.GetLimit())
	if limit <= 0 {
		limit = 20
	}
	offset := int(req.Msg.GetOffset())
	logs, err := s.logUploadSvc.ListByRunner(ctx, tenant.OrganizationID, runnerID, limit, offset)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*runnerapiv1.RunnerLog, 0, len(logs))
	for _, l := range logs {
		items = append(items, toProtoLogEntry(l))
	}
	return connect.NewResponse(&runnerapiv1.ListRunnerLogsResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  int32(limit),
		Offset: int32(offset),
	}), nil
}

func (s *Server) QuerySandboxes(
	ctx context.Context, req *connect.Request[runnerapiv1.QuerySandboxesRequest],
) (*connect.Response[runnerapiv1.QuerySandboxesResponse], error) {
	if s.sandboxQuerySvc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("sandbox query service not configured"))
	}
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	runnerID := req.Msg.GetId()
	podKeys := req.Msg.GetPodKeys()
	if len(podKeys) == 0 || len(podKeys) > 100 {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("pod_keys must contain 1-100 entries"))
	}
	r, err := s.runnerSvc.GetRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.RunnerPolicy.AllowRead(sub, policy.VisibleResource(
		r.OrganizationID, r.RegisteredByUserID, r.Visibility,
	)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}
	if !s.sandboxQuerySvc.IsConnected(runnerID) {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("runner is not connected"))
	}
	result, err := s.sandboxQuerySvc.QuerySandboxes(ctx, runnerID, podKeys)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&runnerapiv1.QuerySandboxesResponse{
		Sandboxes: toProtoSandboxStatuses(result.Sandboxes),
		Error:     result.Error,
	}), nil
}
