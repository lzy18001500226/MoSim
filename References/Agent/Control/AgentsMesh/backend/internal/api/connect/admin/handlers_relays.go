package adminconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	adminv1 "github.com/anthropics/agentsmesh/proto/gen/go/admin/v1"
)

// errRelayManagerUnavailable matches REST's apierr.ServiceUnavailable for
// the same condition (relay manager not wired into this deployment).
var errRelayManagerUnavailable = errors.New("relay manager not available")

func (s *Server) ListRelays(
	ctx context.Context, _ *connect.Request[adminv1.ListRelaysRequest],
) (*connect.Response[adminv1.ListRelaysResponse], error) {
	if _, _, err := interceptors.ResolveSystemAdmin(ctx, s.db); err != nil {
		return nil, err
	}
	if s.relayMgr == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errRelayManagerUnavailable)
	}

	relays := s.relayMgr.GetRelays()
	items := make([]*adminv1.AdminRelay, 0, len(relays))
	for _, r := range relays {
		items = append(items, ToProtoAdminRelay(r))
	}
	return connect.NewResponse(&adminv1.ListRelaysResponse{
		Items: items,
		Total: int32(len(relays)),
	}), nil
}

func (s *Server) GetRelayStats(
	ctx context.Context, _ *connect.Request[adminv1.GetRelayStatsRequest],
) (*connect.Response[adminv1.RelayStats], error) {
	if _, _, err := interceptors.ResolveSystemAdmin(ctx, s.db); err != nil {
		return nil, err
	}
	if s.relayMgr == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errRelayManagerUnavailable)
	}

	stats := s.relayMgr.GetStats()
	return connect.NewResponse(&adminv1.RelayStats{
		TotalRelays:      int32(stats.TotalRelays),
		HealthyRelays:    int32(stats.HealthyRelays),
		TotalConnections: int32(stats.TotalConnections),
	}), nil
}

func (s *Server) GetRelay(
	ctx context.Context, req *connect.Request[adminv1.GetRelayRequest],
) (*connect.Response[adminv1.GetRelayResponse], error) {
	if _, _, err := interceptors.ResolveSystemAdmin(ctx, s.db); err != nil {
		return nil, err
	}
	if s.relayMgr == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errRelayManagerUnavailable)
	}
	if req.Msg.GetId() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("relay id is required"))
	}

	relayInfo := s.relayMgr.GetRelayByID(req.Msg.GetId())
	if relayInfo == nil {
		return nil, connect.NewError(connect.CodeNotFound,
			errors.New("relay not found"))
	}
	return connect.NewResponse(&adminv1.GetRelayResponse{
		Relay: ToProtoAdminRelay(relayInfo),
	}), nil
}

// ForceUnregisterRelay removes a relay from the live roster. Mirrors REST
// DELETE /api/v1/admin/relays/:id (relays.go:99) — audit logs use
// TargetType("relay") + AuditActionDelete; relay rows are not assigned a
// numeric id by the DB (Redis roster keyed by string ID), so target_id
// stays 0 and the relay_id rides in old_data.
func (s *Server) ForceUnregisterRelay(
	ctx context.Context, req *connect.Request[adminv1.ForceUnregisterRelayRequest],
) (*connect.Response[adminv1.ForceUnregisterRelayResponse], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}
	if s.relayMgr == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errRelayManagerUnavailable)
	}
	relayID := req.Msg.GetId()
	if relayID == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("relay id is required"))
	}

	relayInfo := s.relayMgr.GetRelayByID(relayID)
	if relayInfo == nil {
		return nil, connect.NewError(connect.CodeNotFound,
			errors.New("relay not found"))
	}

	s.relayMgr.ForceUnregister(relayID)

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionDelete, admin.TargetType("relay"), 0,
		map[string]any{"relay_id": relayID, "url": relayInfo.URL}, nil,
		req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(&adminv1.ForceUnregisterRelayResponse{
		Status:  "unregistered",
		RelayId: relayID,
	}), nil
}
