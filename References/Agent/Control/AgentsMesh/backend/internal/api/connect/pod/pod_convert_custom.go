package podconnect

import (
	agentdom "github.com/anthropics/agentsmesh/backend/internal/domain/agent"
	poddom "github.com/anthropics/agentsmesh/backend/internal/domain/agentpod"
	gpdom "github.com/anthropics/agentsmesh/backend/internal/domain/gitprovider"
	runnerdom "github.com/anthropics/agentsmesh/backend/internal/domain/runner"
	ticketdom "github.com/anthropics/agentsmesh/backend/internal/domain/ticket"
	userdom "github.com/anthropics/agentsmesh/backend/internal/domain/user"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	podv1 "github.com/anthropics/agentsmesh/proto/gen/go/pod/v1"
)

func toProtoPods(pods []*poddom.Pod) []*podv1.Pod {
	return protoconv.Slice(pods, ToProtoPod)
}

// runnerIDToProto flips zero → nil (REST treats zero as "unassigned").
func runnerIDToProto(id int64) *int64 {
	if id == 0 {
		return nil
	}
	v := id
	return &v
}

// createdByIDToProto always boxes — REST emits this even when zero.
func createdByIDToProto(id int64) *int64 {
	v := id
	return &v
}

// promptToProto flips empty string → nil pointer.
func promptToProto(s string) *string {
	if s == "" {
		return nil
	}
	v := s
	return &v
}

func podRunnerInfoToProto(r *runnerdom.Runner) *podv1.PodRunnerInfo {
	if r == nil {
		return nil
	}
	id := r.ID
	node := r.NodeID
	status := r.Status
	return &podv1.PodRunnerInfo{Id: &id, NodeId: &node, Status: &status}
}

func podAgentInfoToProto(a *agentdom.Agent) *podv1.PodAgentInfo {
	if a == nil {
		return nil
	}
	name := a.Name
	slug := a.Slug
	return &podv1.PodAgentInfo{Name: &name, Slug: &slug}
}

func podRepositoryInfoToProto(r *gpdom.Repository) *podv1.PodRepositoryInfo {
	if r == nil {
		return nil
	}
	id := r.ID
	name := r.Name
	slug := r.Slug
	pt := r.ProviderType
	return &podv1.PodRepositoryInfo{Id: &id, Name: &name, Slug: &slug, ProviderType: &pt}
}

func podTicketInfoToProto(t *ticketdom.Ticket) *podv1.PodTicketInfo {
	if t == nil {
		return nil
	}
	id := t.ID
	slug := t.Slug
	title := t.Title
	return &podv1.PodTicketInfo{Id: &id, Slug: &slug, Title: &title}
}

func podLoopInfoToProto(l *poddom.PodLoopInfo) *podv1.PodLoopInfo {
	if l == nil {
		return nil
	}
	id := l.ID
	name := l.Name
	slug := l.Slug
	return &podv1.PodLoopInfo{Id: &id, Name: &name, Slug: &slug}
}

func podCreatedByInfoToProto(u *userdom.User) *podv1.PodCreatedByInfo {
	if u == nil {
		return nil
	}
	id := u.ID
	username := u.Username
	return &podv1.PodCreatedByInfo{
		Id:       &id,
		Username: &username,
		Name:     protoconv.StringPtr(u.Name),
	}
}
