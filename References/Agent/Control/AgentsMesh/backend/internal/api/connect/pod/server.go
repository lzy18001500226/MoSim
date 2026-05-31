// Package podconnect hosts Connect-RPC handlers for the pod domain.
// Mirrors backend/internal/api/rest/v1/pod*.go but exposes the data plane
// via Connect (binary protobuf wire, see conventions.md §2.5). REST stays
// mounted in parallel; the migration runs dual-track until all 26 services
// have flipped.
//
// Streaming endpoints (terminal data plane, pod events) intentionally stay
// on Relay/WebSocket — this migration is unary RPC only.
//
// Handler shape follows runbook §3:
//   * ResolveOrgScope reads org_slug + injects TenantContext.
//   * Single-entity get/create/update return the entity directly.
//   * List responses follow {items, total, limit, offset}.
//   * CreatePod keeps {pod, warning?} envelope locked by 986a38ca6 (PR #340).
//   * Errors map to Connect codes (conventions §10).
package podconnect

import (
	"context"

	"github.com/anthropics/agentsmesh/backend/internal/domain/grant"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/internal/service/agentpod"
	"github.com/anthropics/agentsmesh/backend/internal/service/geo"
	grantservice "github.com/anthropics/agentsmesh/backend/internal/service/grant"
	"github.com/anthropics/agentsmesh/backend/internal/service/relay"
	"github.com/anthropics/agentsmesh/backend/internal/service/runner"
	"github.com/anthropics/agentsmesh/backend/pkg/policy"
)

// ServiceName mirrors proto.pod.v1.PodService exactly — Connect derives the
// URL from `<package>.<Service>` (conventions §1, §12).
const ServiceName = "proto.pod.v1.PodService"

const (
	ListPodsProcedure           = "/" + ServiceName + "/ListPods"
	GetPodProcedure             = "/" + ServiceName + "/GetPod"
	CreatePodProcedure          = "/" + ServiceName + "/CreatePod"
	TerminatePodProcedure       = "/" + ServiceName + "/TerminatePod"
	UpdatePodAliasProcedure     = "/" + ServiceName + "/UpdatePodAlias"
	UpdatePodPerpetualProcedure = "/" + ServiceName + "/UpdatePodPerpetual"
	GetPodConnectionProcedure   = "/" + ServiceName + "/GetPodConnection"
	SendPodPromptProcedure      = "/" + ServiceName + "/SendPodPrompt"
	ListPodsByTicketProcedure   = "/" + ServiceName + "/ListPodsByTicket"
)

// Server implements PodService. Fields mirror PodHandler / PodConnectHandler
// in v1/pods.go and v1/pod_relay_connect.go, threaded through cmd/server
// wiring at mount time. Streaming endpoints (terminal data plane) intentionally
// stay on Relay/WebSocket — Connect handles unary control plane only.
type Server struct {
	podSvc         *agentpod.PodService
	orgSvc         middleware.OrganizationService
	orchestrator   *agentpod.PodOrchestrator
	podCoordinator *runner.PodCoordinator
	commandSender  runner.RunnerCommandSender
	stateReader    runner.RunnerStateReader
	relayManager   *relay.Manager
	tokenGenerator *relay.TokenGenerator
	geoResolver    geo.Resolver
	grantSvc       *grantservice.Service
	eventBus       EventPublisher
}

// EventPublisher is the subset of eventbus.EventBus the handler depends on.
// Kept as an interface so unit tests can substitute a no-op.
type EventPublisher interface {
	Publish(ctx context.Context, ev EventPublisherEvent) error
}

// EventPublisherEvent is an opaque event payload. Concrete shape lives in
// the eventbus package — handlers only need to publish, not introspect.
type EventPublisherEvent = any

// NewServer constructs a Server. Optional dependencies can be left nil; the
// corresponding handlers degrade gracefully (CodeUnavailable for missing
// command-sender, etc.).
func NewServer(
	podSvc *agentpod.PodService,
	orgSvc middleware.OrganizationService,
	opts ...Option,
) *Server {
	s := &Server{podSvc: podSvc, orgSvc: orgSvc}
	for _, opt := range opts {
		opt(s)
	}
	return s
}

// Option configures a Server. Mirrors the PodHandlerOption pattern in
// v1/pods.go so wiring stays parallel between Gin and Connect.
type Option func(*Server)

func WithOrchestrator(o *agentpod.PodOrchestrator) Option {
	return func(s *Server) { s.orchestrator = o }
}

func WithPodCoordinator(pc *runner.PodCoordinator) Option {
	return func(s *Server) { s.podCoordinator = pc }
}

func WithCommandSender(cs runner.RunnerCommandSender) Option {
	return func(s *Server) { s.commandSender = cs }
}

func WithStateReader(sr runner.RunnerStateReader) Option {
	return func(s *Server) { s.stateReader = sr }
}

func WithRelayManager(rm *relay.Manager) Option {
	return func(s *Server) { s.relayManager = rm }
}

func WithTokenGenerator(tg *relay.TokenGenerator) Option {
	return func(s *Server) { s.tokenGenerator = tg }
}

func WithGeoResolver(gr geo.Resolver) Option {
	return func(s *Server) { s.geoResolver = gr }
}

func WithGrantService(gs *grantservice.Service) Option {
	return func(s *Server) { s.grantSvc = gs }
}

func WithEventBus(eb EventPublisher) Option {
	return func(s *Server) { s.eventBus = eb }
}

// podResourceWithGrants mirrors PodHandler.podResourceWithGrants (v1/pod_relay_connect.go:56).
// Builds a policy.ResourceContext that respects per-user grants on the pod.
func (s *Server) podResourceWithGrants(ctx context.Context, podKey string, orgID, createdByID int64) policy.ResourceContext {
	rc := policy.PodResource(orgID, createdByID)
	if s.grantSvc == nil {
		return rc
	}
	if ids, err := s.grantSvc.GetGrantedUserIDs(ctx, grant.TypePod, podKey); err == nil && len(ids) > 0 {
		return rc.WithGrants(ids)
	}
	return rc
}
