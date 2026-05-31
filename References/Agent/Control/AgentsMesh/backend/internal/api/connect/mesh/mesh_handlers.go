package meshconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	domainmesh "github.com/anthropics/agentsmesh/backend/internal/domain/mesh"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	meshv1 "github.com/anthropics/agentsmesh/proto/gen/go/mesh/v1"
)

// tenantOrError returns the TenantContext from ctx (populated by
// ResolveOrgScope above each handler call). nil only when something
// upstream is broken — ResolveOrgScope sets the tenant on success.
func tenantOrError(ctx context.Context) *middleware.TenantContext {
	return middleware.GetTenant(ctx)
}

// Read-only RPC: GetMeshTopology. Aggregates active pods + bindings +
// channels + runners for the org. Tenant comes from ResolveOrgScope —
// the mesh service needs both org_id (filter scope) and user_id (channel
// visibility filter).

func (s *Server) GetMeshTopology(
	ctx context.Context, req *connect.Request[meshv1.GetMeshTopologyRequest],
) (*connect.Response[meshv1.MeshTopology], error) {
	ctx, org, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := tenantOrError(ctx)
	if tenant == nil {
		return nil, connect.NewError(
			connect.CodeUnauthenticated,
			errors.New("authentication required"),
		)
	}

	topology, err := s.meshSvc.GetTopology(ctx, org.GetID(), tenant.UserID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoTopology(topology)), nil
}

// GetTicketPods resolves the ticket by slug and returns its pods.
// Migrated from MeshHandler.GetTicketPods (REST /tickets/:slug/pods).
// `active_only=true` filters out terminated pods, matching REST query param.
func (s *Server) GetTicketPods(
	ctx context.Context, req *connect.Request[meshv1.GetTicketPodsRequest],
) (*connect.Response[meshv1.GetTicketPodsResponse], error) {
	ctx, org, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetTicketSlug() == "" {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("ticket_slug is required"),
		)
	}

	t, err := s.ticketSvc.GetTicketBySlug(ctx, org.GetID(), req.Msg.GetTicketSlug())
	if err != nil {
		return nil, connect.NewError(
			connect.CodeNotFound,
			errors.New("ticket not found"),
		)
	}

	var pods []domainmesh.MeshNode
	if req.Msg.GetActiveOnly() {
		pods, err = s.meshSvc.GetActivePodsForTicket(ctx, t.ID)
	} else {
		pods, err = s.meshSvc.GetPodsForTicket(ctx, t.ID)
	}
	if err != nil {
		return nil, mapServiceError(err)
	}

	return connect.NewResponse(&meshv1.GetTicketPodsResponse{
		Pods: toProtoMeshNodes(pods),
	}), nil
}

// BatchGetTicketPods returns pods grouped by ticket id. Mirrors REST's
// POST /tickets/batch-pods. Caps at 100 ticket ids per request (parity
// with REST's MeshHandler.BatchGetTicketPods limit).
func (s *Server) BatchGetTicketPods(
	ctx context.Context, req *connect.Request[meshv1.BatchGetTicketPodsRequest],
) (*connect.Response[meshv1.BatchGetTicketPodsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	ids := req.Msg.GetTicketIds()
	if len(ids) == 0 {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("ticket_ids cannot be empty"),
		)
	}
	if len(ids) > 100 {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("cannot query more than 100 tickets at once"),
		)
	}

	result, err := s.meshSvc.BatchGetTicketPods(ctx, ids)
	if err != nil {
		return nil, mapServiceError(err)
	}

	wirePods := make(map[int64]*meshv1.TicketPodList, len(result.TicketPods))
	for ticketID, nodes := range result.TicketPods {
		wirePods[ticketID] = &meshv1.TicketPodList{Pods: toProtoMeshNodes(nodes)}
	}
	return connect.NewResponse(&meshv1.BatchGetTicketPodsResponse{
		TicketPods: wirePods,
	}), nil
}

// CreatePodForTicket creates a new pod scoped to a ticket via the mesh
// service's orchestrator delegation. Returns the pod as a MeshNode so the
// renderer reads the same shape it does from the topology / list endpoints.
func (s *Server) CreatePodForTicket(
	ctx context.Context, req *connect.Request[meshv1.CreatePodForTicketRequest],
) (*connect.Response[meshv1.MeshNode], error) {
	ctx, org, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := tenantOrError(ctx)
	if tenant == nil {
		return nil, connect.NewError(
			connect.CodeUnauthenticated,
			errors.New("authentication required"),
		)
	}
	if req.Msg.GetTicketSlug() == "" {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("ticket_slug is required"),
		)
	}
	if req.Msg.GetRunnerId() == 0 {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("runner_id is required"),
		)
	}

	t, err := s.ticketSvc.GetTicketBySlug(ctx, org.GetID(), req.Msg.GetTicketSlug())
	if err != nil {
		return nil, connect.NewError(
			connect.CodeNotFound,
			errors.New("ticket not found"),
		)
	}

	pod, err := s.meshSvc.CreatePodForTicket(ctx, &domainmesh.CreatePodForTicketRequest{
		OrganizationID: org.GetID(),
		TicketID:       t.ID,
		RunnerID:       req.Msg.GetRunnerId(),
		CreatedByID:    tenant.UserID,
		Prompt:         req.Msg.GetPrompt(),
		Model:          req.Msg.GetModel(),
		PermissionMode: req.Msg.GetPermissionMode(),
	})
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(podToProtoMeshNode(pod)), nil
}
