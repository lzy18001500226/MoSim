package channel

import (
	"time"

	"github.com/lib/pq"
)

const (
	BindingStatusPending  = "pending"
	BindingStatusActive   = "active"
	BindingStatusRejected = "rejected"
	BindingStatusInactive = "inactive"
	BindingStatusExpired  = "expired"
)

const (
	BindingScopePodRead  = "pod:read"
	BindingScopePodWrite = "pod:write"
)

const (
	BindingPolicySameUserAuto    = "same_user_auto"
	BindingPolicySameProjectAuto = "same_project_auto"
	BindingPolicyExplicitOnly    = "explicit_only"
)

var ValidBindingScopes = map[string]bool{
	BindingScopePodRead:  true,
	BindingScopePodWrite: true,
}

type PodBinding struct {
	ID             int64 `gorm:"primaryKey" json:"id"`
	OrganizationID int64 `gorm:"not null;index" json:"organization_id"`

	InitiatorPod  string         `gorm:"size:100;not null;index" json:"initiator_pod"`
	TargetPod     string         `gorm:"size:100;not null;index" json:"target_pod"`
	GrantedScopes pq.StringArray `gorm:"type:text[]" json:"granted_scopes"`
	PendingScopes pq.StringArray `gorm:"type:text[]" json:"pending_scopes"`
	Status        string         `gorm:"size:50;not null;default:'pending'" json:"status"`

	RequestedAt *time.Time `json:"requested_at,omitempty"`
	RespondedAt *time.Time `json:"responded_at,omitempty"`
	ExpiresAt   *time.Time `json:"expires_at,omitempty"`

	RejectionReason *string `gorm:"size:500" json:"rejection_reason,omitempty"`

	CreatedAt time.Time `gorm:"not null;default:now()" json:"created_at"`
	UpdatedAt time.Time `gorm:"not null;default:now()" json:"updated_at"`
}

func (PodBinding) TableName() string {
	return "pod_bindings"
}

func (b *PodBinding) HasScope(scope string) bool {
	for _, s := range b.GrantedScopes {
		if s == scope {
			return true
		}
	}
	return false
}

func (b *PodBinding) HasPendingScope(scope string) bool {
	for _, s := range b.PendingScopes {
		if s == scope {
			return true
		}
	}
	return false
}

func (b *PodBinding) IsActive() bool {
	return b.Status == BindingStatusActive
}

func (b *PodBinding) IsPending() bool {
	return b.Status == BindingStatusPending
}

func (b *PodBinding) CanObserve() bool {
	return b.IsActive() && b.HasScope(BindingScopePodRead)
}

func (b *PodBinding) CanControl() bool {
	return b.IsActive() && b.HasScope(BindingScopePodWrite)
}
