package podconnect

import (
	"context"
	"errors"
	"log/slog"
	"time"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/internal/service/relay"
	"github.com/anthropics/agentsmesh/backend/pkg/policy"
	podv1 "github.com/anthropics/agentsmesh/proto/gen/go/pod/v1"
)

// GetPodConnection — REST analogue: GET /api/v1/orgs/:slug/pods/:key/relay/connect.
// Returns Relay connection info: public URL + browser token + optional local
// relay URL/token when the runner advertises a local WS server.
func (s *Server) GetPodConnection(
	ctx context.Context, req *connect.Request[podv1.GetPodConnectionRequest],
) (*connect.Response[podv1.PodConnectionInfo], error) {
	if s.relayManager == nil || !s.relayManager.HasHealthyRelays() {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("relay service is not available"))
	}
	if s.tokenGenerator == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("token generator not configured"))
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
	if !policy.PodPolicy.AllowRead(sub, s.podResourceWithGrants(ctx, podKey, pod.OrganizationID, pod.CreatedByID)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}
	if !pod.IsActive() {
		return nil, connect.NewError(connect.CodeFailedPrecondition, errors.New("pod is not active"))
	}

	relayInfo := s.selectRelay(ctx, tenant.OrganizationSlug)
	if relayInfo == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("no healthy relay available"))
	}

	var localRelayURL, localToken, localRelayNodeID string
	if s.commandSender != nil && pod.RunnerID > 0 {
		runnerToken, err := s.tokenGenerator.GenerateToken(podKey, pod.RunnerID, 0, tenant.OrganizationID, time.Hour)
		if err != nil {
			return nil, connect.NewError(connect.CodeInternal, errors.New("failed to generate runner token"))
		}
		if s.stateReader != nil {
			localRelayURL = s.stateReader.GetRunnerLocalRelayURL(pod.RunnerID)
		}
		if localRelayURL != "" {
			lt, err := s.tokenGenerator.GenerateToken(podKey, pod.RunnerID, tenant.UserID, tenant.OrganizationID, time.Hour)
			if err != nil {
				slog.WarnContext(ctx, "failed to generate local token, falling back to cloud relay only",
					"pod_key", podKey, "runner_id", pod.RunnerID, "error", err)
				localRelayURL = ""
			} else {
				localToken = lt
				if s.stateReader != nil {
					localRelayNodeID = s.stateReader.GetRunnerNodeID(pod.RunnerID)
				}
			}
		}
		if err := s.commandSender.SendSubscribePod(ctx, pod.RunnerID, podKey, relayInfo.URL, runnerToken, localToken, true, 1000); err != nil {
			slog.WarnContext(ctx, "failed to send subscribe pod command", "pod_key", podKey, "runner_id", pod.RunnerID, "error", err)
		}
	}

	token, err := s.tokenGenerator.GenerateToken(podKey, pod.RunnerID, tenant.UserID, tenant.OrganizationID, time.Hour)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, errors.New("failed to generate token"))
	}

	return connect.NewResponse(&podv1.PodConnectionInfo{
		RelayUrl:         relayInfo.URL,
		Token:            token,
		PodKey:           podKey,
		LocalRelayUrl:    localRelayURL,
		LocalToken:       localToken,
		LocalRelayNodeId: localRelayNodeID,
	}), nil
}

func (s *Server) selectRelay(_ context.Context, orgSlug string) *relay.RelayInfo {
	opts := relay.GeoSelectOptions{OrgSlug: orgSlug}
	// Connect handlers don't have a Gin context for ClientIP; geo resolution
	// degrades to "no user location" — Relay manager handles that case by
	// falling back to org-affinity / round-robin.
	return s.relayManager.SelectRelayForPodGeo(opts)
}
