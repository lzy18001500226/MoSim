package loopconnect

import (
	"context"
	"encoding/json"
	"errors"
	"strconv"
	"time"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	loopDomain "github.com/anthropics/agentsmesh/backend/internal/domain/loop"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	loopsvc "github.com/anthropics/agentsmesh/backend/internal/service/loop"
	loopv1 "github.com/anthropics/agentsmesh/proto/gen/go/loop/v1"
)

// LoopOrchestratorInterface mirrors REST LoopHandler's orchestrator dependency.
type LoopOrchestratorInterface interface {
	TriggerRun(ctx context.Context, req *loopsvc.TriggerRunRequest) (*loopsvc.TriggerRunResult, error)
	StartRun(ctx context.Context, loop *loopDomain.Loop, run *loopDomain.LoopRun, userID int64)
	MarkRunCancelled(ctx context.Context, runID int64, reason string) error
}

// EnableLoop — REST analogue: POST /loops/:slug/enable.
func (s *Server) EnableLoop(
	ctx context.Context, req *connect.Request[loopv1.LoopActionRequest],
) (*connect.Response[loopv1.Loop], error) {
	return s.setStatus(ctx, req.Msg, loopDomain.StatusEnabled)
}

// DisableLoop — REST analogue: POST /loops/:slug/disable.
func (s *Server) DisableLoop(
	ctx context.Context, req *connect.Request[loopv1.LoopActionRequest],
) (*connect.Response[loopv1.Loop], error) {
	return s.setStatus(ctx, req.Msg, loopDomain.StatusDisabled)
}

func (s *Server) setStatus(
	ctx context.Context, m *loopv1.LoopActionRequest, status string,
) (*connect.Response[loopv1.Loop], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, m, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if s.svc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("loop service not configured"))
	}
	if m.GetLoopSlug() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("loop_slug is required"))
	}
	tenant := middleware.GetTenant(ctx)
	loop, err := s.svc.SetStatus(ctx, tenant.OrganizationID, m.GetLoopSlug(), status)
	if err != nil {
		if errors.Is(err, loopsvc.ErrLoopNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, errors.New("loop not found"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoLoop(loop)), nil
}

// TriggerLoop — REST analogue: POST /loops/:slug/trigger.
func (s *Server) TriggerLoop(
	ctx context.Context, req *connect.Request[loopv1.TriggerLoopRequest],
) (*connect.Response[loopv1.TriggerLoopResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if s.svc == nil || s.orchestrator == nil {
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
	var variables json.RawMessage
	if v := req.Msg.GetVariablesJson(); v != "" {
		variables = json.RawMessage(v)
	}
	result, err := s.orchestrator.TriggerRun(ctx, &loopsvc.TriggerRunRequest{
		LoopID:        loop.ID,
		TriggerType:   loopDomain.RunTriggerManual,
		TriggerSource: "user:" + strconv.FormatInt(tenant.UserID, 10),
		TriggerParams: variables,
	})
	if err != nil {
		if errors.Is(err, loopsvc.ErrLoopDisabled) {
			return nil, connect.NewError(connect.CodeFailedPrecondition, errors.New("loop is disabled"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	if result.Skipped {
		return connect.NewResponse(&loopv1.TriggerLoopResponse{
			Run:     toProtoLoopRun(result.Run),
			Skipped: true,
			Reason:  result.Reason,
		}), nil
	}

	startCtx, startCancel := context.WithTimeout(context.Background(), 5*time.Minute)
	go func() {
		defer startCancel()
		s.orchestrator.StartRun(startCtx, result.Loop, result.Run, tenant.UserID)
	}()

	return connect.NewResponse(&loopv1.TriggerLoopResponse{
		Run:     toProtoLoopRun(result.Run),
		Skipped: false,
	}), nil
}
