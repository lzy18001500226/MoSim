package loopconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	loopDomain "github.com/anthropics/agentsmesh/backend/internal/domain/loop"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	loopsvc "github.com/anthropics/agentsmesh/backend/internal/service/loop"
	loopv1 "github.com/anthropics/agentsmesh/proto/gen/go/loop/v1"
)

// LoopRunServiceInterface mirrors REST LoopHandler's loopRunService dependency.
type LoopRunServiceInterface interface {
	ListRuns(ctx context.Context, filter *loopsvc.ListRunsFilter) ([]*loopDomain.LoopRun, int64, error)
	GetByID(ctx context.Context, id int64) (*loopDomain.LoopRun, error)
	CountActiveRunsByLoopIDs(ctx context.Context, ids []int64) (map[int64]int64, error)
	GetAvgDuration(ctx context.Context, loopID int64) (*float64, error)
}

// ListRuns — REST analogue: GET /loops/:slug/runs.
func (s *Server) ListRuns(
	ctx context.Context, req *connect.Request[loopv1.ListRunsRequest],
) (*connect.Response[loopv1.ListRunsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if s.svc == nil || s.runSvc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("loop services not configured"))
	}
	if req.Msg.GetLoopSlug() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("loop_slug is required"))
	}
	tenant := middleware.GetTenant(ctx)
	loop, err := s.svc.GetBySlug(ctx, tenant.OrganizationID, req.Msg.GetLoopSlug())
	if err != nil {
		if errors.Is(err, loopsvc.ErrLoopNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, errors.New("loop not found"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	limit := int(req.Msg.GetLimit())
	if limit == 0 {
		limit = 20
	}
	if limit > 100 {
		limit = 100
	}
	offset := int(req.Msg.GetOffset())
	if offset < 0 {
		offset = 0
	}

	runs, total, err := s.runSvc.ListRuns(ctx, &loopsvc.ListRunsFilter{
		LoopID: loop.ID,
		Status: req.Msg.GetStatus(),
		Limit:  limit,
		Offset: offset,
	})
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	items := make([]*loopv1.LoopRun, 0, len(runs))
	for _, r := range runs {
		items = append(items, toProtoLoopRun(r))
	}
	return connect.NewResponse(&loopv1.ListRunsResponse{
		Items:  items,
		Total:  total,
		Limit:  int32(limit),
		Offset: int32(offset),
	}), nil
}

// CancelRun — REST analogue: POST /loops/:slug/runs/:run_id/cancel.
func (s *Server) CancelRun(
	ctx context.Context, req *connect.Request[loopv1.CancelRunRequest],
) (*connect.Response[loopv1.CancelRunResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if s.svc == nil || s.runSvc == nil || s.orchestrator == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("loop services not configured"))
	}
	if req.Msg.GetLoopSlug() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("loop_slug is required"))
	}
	if req.Msg.GetRunId() == 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("run_id is required"))
	}
	tenant := middleware.GetTenant(ctx)

	loop, err := s.svc.GetBySlug(ctx, tenant.OrganizationID, req.Msg.GetLoopSlug())
	if err != nil {
		if errors.Is(err, loopsvc.ErrLoopNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, errors.New("loop not found"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	run, err := s.runSvc.GetByID(ctx, req.Msg.GetRunId())
	if err != nil {
		if errors.Is(err, loopsvc.ErrRunNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, errors.New("run not found"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	if run.LoopID != loop.ID {
		return nil, connect.NewError(connect.CodeNotFound, errors.New("run not found"))
	}
	if run.IsTerminal() {
		return nil, connect.NewError(connect.CodeFailedPrecondition, errors.New("run is already in terminal state"))
	}

	if run.PodKey != nil && s.podTerminator != nil {
		if err := s.podTerminator.TerminatePod(ctx, *run.PodKey); err != nil {
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	} else {
		if err := s.orchestrator.MarkRunCancelled(ctx, req.Msg.GetRunId(), "Cancelled by user"); err != nil {
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	}
	return connect.NewResponse(&loopv1.CancelRunResponse{Message: "Run cancelled"}), nil
}
