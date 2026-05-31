// Package loopconnect hosts Connect-RPC handlers for the loop service.
// Mirrors backend/internal/api/rest/v1/loop_handler*.go.
//
// Split rationale (200-line rule):
//   - loop.go              — server scaffolding + Mount + queries (List/Get/Delete)
//   - loop_crud.go         — Create + Update (heaviest field mapping)
//   - loop_actions.go      — Enable/Disable/Trigger
//   - loop_runs.go         — ListRuns + CancelRun
//   - loop_convert.go      — domain ↔ proto translation
package loopconnect

import (
	"context"
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	loopDomain "github.com/anthropics/agentsmesh/backend/internal/domain/loop"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	loopsvc "github.com/anthropics/agentsmesh/backend/internal/service/loop"
	loopv1 "github.com/anthropics/agentsmesh/proto/gen/go/loop/v1"
)

const ServiceName = "proto.loop.v1.LoopService"

const (
	ListLoopsProcedure   = "/" + ServiceName + "/ListLoops"
	GetLoopProcedure     = "/" + ServiceName + "/GetLoop"
	CreateLoopProcedure  = "/" + ServiceName + "/CreateLoop"
	UpdateLoopProcedure  = "/" + ServiceName + "/UpdateLoop"
	DeleteLoopProcedure  = "/" + ServiceName + "/DeleteLoop"
	EnableLoopProcedure  = "/" + ServiceName + "/EnableLoop"
	DisableLoopProcedure = "/" + ServiceName + "/DisableLoop"
	TriggerLoopProcedure = "/" + ServiceName + "/TriggerLoop"
	ListRunsProcedure    = "/" + ServiceName + "/ListRuns"
	CancelRunProcedure   = "/" + ServiceName + "/CancelRun"
)

// LoopServiceInterface mirrors REST LoopHandler's loopService dependency.
type LoopServiceInterface interface {
	List(ctx context.Context, filter *loopsvc.ListLoopsFilter) ([]*loopDomain.Loop, int64, error)
	GetBySlug(ctx context.Context, orgID int64, slug string) (*loopDomain.Loop, error)
	Create(ctx context.Context, req *loopsvc.CreateLoopRequest) (*loopDomain.Loop, error)
	Update(ctx context.Context, orgID int64, slug string, req *loopsvc.UpdateLoopRequest) (*loopDomain.Loop, error)
	Delete(ctx context.Context, orgID int64, slug string) error
	SetStatus(ctx context.Context, orgID int64, slug string, status string) (*loopDomain.Loop, error)
}

// PodTerminatorForLoop mirrors v1.PodTerminatorForLoop (ISP — only TerminatePod).
type PodTerminatorForLoop interface {
	TerminatePod(ctx context.Context, podKey string) error
}

type Server struct {
	svc           LoopServiceInterface
	runSvc        LoopRunServiceInterface
	orchestrator  LoopOrchestratorInterface
	orgSvc        middleware.OrganizationService
	podTerminator PodTerminatorForLoop
}

func NewServer(
	svc LoopServiceInterface,
	runSvc LoopRunServiceInterface,
	orchestrator LoopOrchestratorInterface,
	orgSvc middleware.OrganizationService,
	podTerminator PodTerminatorForLoop,
) *Server {
	return &Server{
		svc:           svc,
		runSvc:        runSvc,
		orchestrator:  orchestrator,
		orgSvc:        orgSvc,
		podTerminator: podTerminator,
	}
}

func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListLoopsProcedure, connect.NewUnaryHandler(ListLoopsProcedure, srv.ListLoops, opts...))
	mux.Handle(GetLoopProcedure, connect.NewUnaryHandler(GetLoopProcedure, srv.GetLoop, opts...))
	mux.Handle(CreateLoopProcedure, connect.NewUnaryHandler(CreateLoopProcedure, srv.CreateLoop, opts...))
	mux.Handle(UpdateLoopProcedure, connect.NewUnaryHandler(UpdateLoopProcedure, srv.UpdateLoop, opts...))
	mux.Handle(DeleteLoopProcedure, connect.NewUnaryHandler(DeleteLoopProcedure, srv.DeleteLoop, opts...))
	mux.Handle(EnableLoopProcedure, connect.NewUnaryHandler(EnableLoopProcedure, srv.EnableLoop, opts...))
	mux.Handle(DisableLoopProcedure, connect.NewUnaryHandler(DisableLoopProcedure, srv.DisableLoop, opts...))
	mux.Handle(TriggerLoopProcedure, connect.NewUnaryHandler(TriggerLoopProcedure, srv.TriggerLoop, opts...))
	mux.Handle(ListRunsProcedure, connect.NewUnaryHandler(ListRunsProcedure, srv.ListRuns, opts...))
	mux.Handle(CancelRunProcedure, connect.NewUnaryHandler(CancelRunProcedure, srv.CancelRun, opts...))
}

// ListLoops — REST analogue: GET /loops.
func (s *Server) ListLoops(
	ctx context.Context, req *connect.Request[loopv1.ListLoopsRequest],
) (*connect.Response[loopv1.ListLoopsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if s.svc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("loop service not configured"))
	}
	tenant := middleware.GetTenant(ctx)

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

	var cronEnabled *bool
	if req.Msg.CronEnabled != nil {
		v := req.Msg.GetCronEnabled()
		cronEnabled = &v
	}

	loops, total, err := s.svc.List(ctx, &loopsvc.ListLoopsFilter{
		OrganizationID: tenant.OrganizationID,
		Status:         req.Msg.GetStatus(),
		ExecutionMode:  req.Msg.GetExecutionMode(),
		CronEnabled:    cronEnabled,
		Query:          req.Msg.GetQuery(),
		Limit:          limit,
		Offset:         offset,
	})
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	if s.runSvc != nil && len(loops) > 0 {
		ids := make([]int64, len(loops))
		for i, l := range loops {
			ids[i] = l.ID
		}
		if counts, err := s.runSvc.CountActiveRunsByLoopIDs(ctx, ids); err == nil {
			for _, l := range loops {
				if c, ok := counts[l.ID]; ok {
					l.ActiveRunCount = int(c)
				}
			}
		}
	}

	items := make([]*loopv1.Loop, 0, len(loops))
	for _, l := range loops {
		items = append(items, toProtoLoop(l))
	}
	return connect.NewResponse(&loopv1.ListLoopsResponse{
		Items:  items,
		Total:  total,
		Limit:  int32(limit),
		Offset: int32(req.Msg.GetOffset()),
	}), nil
}

// GetLoop — REST analogue: GET /loops/:slug.
func (s *Server) GetLoop(
	ctx context.Context, req *connect.Request[loopv1.GetLoopRequest],
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
	tenant := middleware.GetTenant(ctx)
	loop, err := s.svc.GetBySlug(ctx, tenant.OrganizationID, req.Msg.GetLoopSlug())
	if err != nil {
		if errors.Is(err, loopsvc.ErrLoopNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, errors.New("loop not found"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	if s.runSvc != nil {
		if counts, err := s.runSvc.CountActiveRunsByLoopIDs(ctx, []int64{loop.ID}); err == nil {
			if c, ok := counts[loop.ID]; ok {
				loop.ActiveRunCount = int(c)
			}
		}
		if avg, err := s.runSvc.GetAvgDuration(ctx, loop.ID); err == nil && avg != nil {
			loop.AvgDurationSec = avg
		}
	}
	return connect.NewResponse(toProtoLoop(loop)), nil
}

// DeleteLoop — REST analogue: DELETE /loops/:slug.
func (s *Server) DeleteLoop(
	ctx context.Context, req *connect.Request[loopv1.DeleteLoopRequest],
) (*connect.Response[loopv1.DeleteLoopResponse], error) {
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
	tenant := middleware.GetTenant(ctx)
	if err := s.svc.Delete(ctx, tenant.OrganizationID, req.Msg.GetLoopSlug()); err != nil {
		switch {
		case errors.Is(err, loopsvc.ErrLoopNotFound):
			return nil, connect.NewError(connect.CodeNotFound, errors.New("loop not found"))
		case errors.Is(err, loopsvc.ErrHasActiveRuns):
			return nil, connect.NewError(connect.CodeFailedPrecondition,
				errors.New("loop has active runs; cancel or wait first"))
		default:
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	}
	return connect.NewResponse(&loopv1.DeleteLoopResponse{Message: "Loop deleted"}), nil
}
