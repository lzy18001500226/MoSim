// Package tokenusageconnect hosts Connect-RPC handlers for token usage
// analytics. Mirrors backend/internal/api/rest/v1/token_usage.go but
// exposes the dashboard RPC via Connect (binary protobuf wire,
// conventions §2.5). REST stays mounted in parallel.
//
// Admin-only — handler additionally enforces role == owner|admin after
// ResolveOrgScope, mirroring REST's isAdminOrOwner check.
package tokenusageconnect

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"time"

	"connectrpc.com/connect"
	"golang.org/x/sync/errgroup"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/tokenusage"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	tokenusagesvc "github.com/anthropics/agentsmesh/backend/internal/service/tokenusage"
	tuv1 "github.com/anthropics/agentsmesh/proto/gen/go/token_usage/v1"
)

const ServiceName = "proto.token_usage.v1.TokenUsageService"

const GetDashboardProcedure = "/" + ServiceName + "/GetDashboard"

var validGranularities = map[string]bool{"day": true, "week": true, "month": true}

type Server struct {
	svc    *tokenusagesvc.Service
	orgSvc middleware.OrganizationService
}

func NewServer(svc *tokenusagesvc.Service, orgSvc middleware.OrganizationService) *Server {
	return &Server{svc: svc, orgSvc: orgSvc}
}

func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetDashboardProcedure, connect.NewUnaryHandler(
		GetDashboardProcedure, srv.GetDashboard, opts...,
	))
}

// GetDashboard runs 5 aggregations concurrently. Same shape as REST's
// GetDashboard handler.
func (s *Server) GetDashboard(
	ctx context.Context, req *connect.Request[tuv1.GetDashboardRequest],
) (*connect.Response[tuv1.GetDashboardResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if !isAdminOrOwner(tenant) {
		return nil, connect.NewError(connect.CodePermissionDenied,
			errors.New("organization admin role required"))
	}

	filter, err := buildFilter(req.Msg)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}

	var (
		summary    *tokenusage.UsageSummary
		timeSeries []tokenusage.TimeSeriesPoint
		byAgent    []tokenusage.AgentUsage
		byUser     []tokenusage.UserUsage
		byModel    []tokenusage.ModelUsage
	)
	g, gCtx := errgroup.WithContext(ctx)
	g.Go(func() error {
		v, err := s.svc.GetSummary(gCtx, tenant.OrganizationID, filter)
		summary = v
		return err
	})
	g.Go(func() error {
		v, err := s.svc.GetTimeSeries(gCtx, tenant.OrganizationID, filter)
		timeSeries = v
		return err
	})
	g.Go(func() error {
		v, err := s.svc.GetByAgent(gCtx, tenant.OrganizationID, filter)
		byAgent = v
		return err
	})
	g.Go(func() error {
		v, err := s.svc.GetByUser(gCtx, tenant.OrganizationID, filter)
		byUser = v
		return err
	})
	g.Go(func() error {
		v, err := s.svc.GetByModel(gCtx, tenant.OrganizationID, filter)
		byModel = v
		return err
	})
	if err := g.Wait(); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	return connect.NewResponse(&tuv1.GetDashboardResponse{
		Summary:    toProtoSummary(summary),
		TimeSeries: toProtoTimeSeries(timeSeries),
		ByAgent:    toProtoByAgent(byAgent),
		ByUser:     toProtoByUser(byUser),
		ByModel:    toProtoByModel(byModel),
	}), nil
}

func isAdminOrOwner(tenant *middleware.TenantContext) bool {
	return tenant.UserRole == "owner" || tenant.UserRole == "admin"
}

// buildFilter mirrors REST parseFilter, including the 30-day default
// window + 366-day max range cap.
func buildFilter(req *tuv1.GetDashboardRequest) (tokenusage.AggregationFilter, error) {
	var f tokenusage.AggregationFilter
	f.EndTime = time.Now()
	f.StartTime = f.EndTime.AddDate(0, 0, -30)

	if s := req.GetStartTime(); s != "" {
		t, err := time.Parse(time.RFC3339, s)
		if err != nil {
			return f, fmt.Errorf("start_time: %w", err)
		}
		f.StartTime = t
	}
	if s := req.GetEndTime(); s != "" {
		t, err := time.Parse(time.RFC3339, s)
		if err != nil {
			return f, fmt.Errorf("end_time: %w", err)
		}
		f.EndTime = t
	}
	if f.StartTime.After(f.EndTime) {
		return f, errors.New("start_time must be before end_time")
	}
	const maxDateRange = 366 * 24 * time.Hour
	if f.EndTime.Sub(f.StartTime) > maxDateRange {
		return f, errors.New("date range cannot exceed 366 days")
	}

	gran := req.GetGranularity()
	if gran == "" {
		gran = "day"
	}
	if !validGranularities[gran] {
		return f, fmt.Errorf("invalid granularity %q, must be one of: day, week, month", gran)
	}
	f.Granularity = gran

	if v := req.GetAgentSlug(); v != "" {
		f.AgentSlug = &v
	}
	if req.UserId != nil {
		v := req.GetUserId()
		f.UserID = &v
	}
	if v := req.GetModel(); v != "" {
		f.Model = &v
	}
	return f, nil
}
