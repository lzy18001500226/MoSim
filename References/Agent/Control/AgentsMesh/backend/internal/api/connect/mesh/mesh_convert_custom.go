package meshconnect

import (
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	"github.com/anthropics/agentsmesh/backend/internal/domain/agentpod"
	domainmesh "github.com/anthropics/agentsmesh/backend/internal/domain/mesh"
	meshv1 "github.com/anthropics/agentsmesh/proto/gen/go/mesh/v1"
)

// toProtoMeshNode — codegen-backed value-receiver alias. The wire mapping
// itself lives in `mesh_convert.amesh.go`. Existing callers pass `MeshNode`
// by value (the topology projection holds nodes by value); we box to a
// pointer for the generic codegen signature.
func toProtoMeshNode(n domainmesh.MeshNode) *meshv1.MeshNode {
	return ToProtoMeshNode(&n)
}

func toProtoMeshEdge(e domainmesh.MeshEdge) *meshv1.MeshEdge {
	return ToProtoMeshEdge(&e)
}

func toProtoChannelInfo(c domainmesh.ChannelInfo) *meshv1.ChannelInfo {
	return ToProtoChannelInfo(&c)
}

func toProtoRunnerInfo(r domainmesh.RunnerInfo) *meshv1.RunnerInfo {
	return ToProtoRunnerInfo(&r)
}

func toProtoTopology(t *domainmesh.MeshTopology) *meshv1.MeshTopology {
	if t == nil {
		return &meshv1.MeshTopology{}
	}
	return &meshv1.MeshTopology{
		Nodes:    protoconv.Slice(t.Nodes, toProtoMeshNode),
		Edges:    protoconv.Slice(t.Edges, toProtoMeshEdge),
		Channels: protoconv.Slice(t.Channels, toProtoChannelInfo),
		Runners:  protoconv.Slice(t.Runners, toProtoRunnerInfo),
	}
}

func toProtoMeshNodes(nodes []domainmesh.MeshNode) []*meshv1.MeshNode {
	return protoconv.Slice(nodes, toProtoMeshNode)
}

// podToProtoMeshNode mirrors service/mesh/service.go:podToNode but emits the
// proto wire shape directly. Used by CreatePodForTicket — the underlying
// mesh service returns the raw agentpod.Pod from the orchestrator (not the
// domain projection), so the Connect handler does the projection itself.
//
// Field set matches toProtoMeshNode exactly so renderer callers see the
// same shape from both topology reads and pod-creation responses.
//
// Stays hand-written: the source struct is agentpod.Pod (not mesh.MeshNode);
// the conversion synthesizes runner_node_id and ticket_slug from preloaded
// associations that the codegen template cannot reach mechanically.
func podToProtoMeshNode(p *agentpod.Pod) *meshv1.MeshNode {
	if p == nil {
		return nil
	}
	out := &meshv1.MeshNode{
		PodKey:       p.PodKey,
		Status:       p.Status,
		AgentStatus:  p.AgentStatus,
		AgentSlug:    p.AgentSlug,
		CreatedById:  p.CreatedByID,
		RunnerId:     p.RunnerID,
		Model:        protoconv.StringPtr(p.Model),
		Title:        protoconv.StringPtr(p.Title),
		Alias:        protoconv.StringPtr(p.Alias),
		TicketId:     protoconv.Int64Ptr(p.TicketID),
		RepositoryId: protoconv.Int64Ptr(p.RepositoryID),
		StartedAt:    protoconv.RFC3339Ptr(p.StartedAt),
	}
	if p.Runner != nil {
		out.RunnerNodeId = p.Runner.NodeID
		out.RunnerStatus = p.Runner.Status
	}
	if p.Ticket != nil {
		slug := p.Ticket.Slug
		title := p.Ticket.Title
		out.TicketSlug = &slug
		out.TicketTitle = &title
	}
	return out
}
