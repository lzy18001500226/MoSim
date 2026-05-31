package skillregistryadminconnect

import (
	"context"
	"errors"
	"time"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	extensionservice "github.com/anthropics/agentsmesh/backend/internal/service/extension"
	extensionv1 "github.com/anthropics/agentsmesh/proto/gen/go/extension/v1"
)

// errPlatformRegistryDuplicate fires when a Create call collides on
// repository URL. Mirrors REST's ALREADY_EXISTS error envelope.
var errPlatformRegistryDuplicate = errors.New("platform skill registry with this URL already exists")

func (s *Server) SyncSkillRegistry(
	ctx context.Context, req *connect.Request[extensionv1.SyncAdminSkillRegistryRequest],
) (*connect.Response[extensionv1.SyncAdminSkillRegistryResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	registry, err := s.repo.GetSkillRegistry(ctx, req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeNotFound, errors.New("skill registry not found"))
	}
	if !registry.IsPlatformLevel() {
		return nil, connect.NewError(connect.CodeInvalidArgument, errPlatformLevelOnly)
	}
	if s.worker == nil {
		return nil, connect.NewError(connect.CodeInternal, errMarketplaceWorkerUnavailable)
	}

	if err := s.worker.SyncSingle(ctx, req.Msg.GetId()); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	// Reload so the response carries the post-sync status (success/failed/...).
	// REST swallows this re-read error; we mirror that — the caller already
	// knows sync succeeded if we got here.
	registry, _ = s.repo.GetSkillRegistry(ctx, req.Msg.GetId())

	return connect.NewResponse(&extensionv1.SyncAdminSkillRegistryResponse{
		Message:  "sync completed",
		Registry: ToProtoAdminSkillRegistry(registry),
	}), nil
}

func (s *Server) DeleteSkillRegistry(
	ctx context.Context, req *connect.Request[extensionv1.DeleteAdminSkillRegistryRequest],
) (*connect.Response[extensionv1.DeleteAdminSkillRegistryResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	registry, err := s.repo.GetSkillRegistry(ctx, req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeNotFound, errors.New("skill registry not found"))
	}
	if !registry.IsPlatformLevel() {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("cannot delete non-platform-level skill registry via admin API"),
		)
	}

	if err := s.repo.DeleteSkillRegistry(ctx, req.Msg.GetId()); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	return connect.NewResponse(&extensionv1.DeleteAdminSkillRegistryResponse{}), nil
}

// triggerAsyncSync mirrors REST's fire-and-forget goroutine
// (skill_registries.go:99). Detached from the request context — the
// caller's response is already on the wire when this fires. 10-minute
// budget matches REST.
func triggerAsyncSync(worker *extensionservice.MarketplaceWorker, registryID int64) {
	go func() {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Minute)
		defer cancel()
		_ = worker.SyncSingle(ctx, registryID)
	}()
}
