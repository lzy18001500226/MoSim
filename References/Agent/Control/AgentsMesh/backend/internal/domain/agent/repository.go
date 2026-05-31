package agent

import (
	"context"
	"time"
)

// AgentRepository defines persistence operations for agents
type AgentRepository interface {
	// Builtin agents
	// ListBuiltinActive returns user-facing builtin agents (is_internal=false).
	// Use this for any path that surfaces a list to a regular user.
	ListBuiltinActive(ctx context.Context) ([]*Agent, error)
	// ListBuiltinAll returns every active builtin row including internal
	// ones. Use this for runner discovery + admin / e2e dev paths where
	// the consumer legitimately needs to see test fixtures.
	ListBuiltinAll(ctx context.Context) ([]*Agent, error)
	ListAllActive(ctx context.Context) ([]*Agent, error)
	GetBySlug(ctx context.Context, slug string) (*Agent, error)

	// Custom agents
	ListCustomByOrg(ctx context.Context, orgID int64) ([]*CustomAgent, error)
	GetCustomBySlug(ctx context.Context, orgID int64, slug string) (*CustomAgent, error)
	CustomSlugExists(ctx context.Context, orgID int64, slug string) (bool, error)
	CreateCustom(ctx context.Context, custom *CustomAgent) error
	UpdateCustom(ctx context.Context, orgID int64, slug string, updates map[string]interface{}) (*CustomAgent, error)
	DeleteCustom(ctx context.Context, orgID int64, slug string) error
	CountLoopReferences(ctx context.Context, orgID int64, slug string) (int64, error)
}

// UserConfigRepository defines persistence operations for user agent configs
type UserConfigRepository interface {
	GetByUserAndAgentSlug(ctx context.Context, userID int64, agentSlug string) (*UserAgentConfig, error)
	Upsert(ctx context.Context, userID int64, agentSlug string, configValues ConfigValues) error
	Delete(ctx context.Context, userID int64, agentSlug string) error
	ListByUser(ctx context.Context, userID int64) ([]*UserAgentConfig, error)
}

// MessageRepository defines persistence operations for agent messages
type MessageRepository interface {
	Create(ctx context.Context, message *AgentMessage) error
	GetByID(ctx context.Context, id int64) (*AgentMessage, error)
	Save(ctx context.Context, message *AgentMessage) error
	Delete(ctx context.Context, message *AgentMessage) error

	UpdateStatus(ctx context.Context, messageID int64, updates map[string]interface{}) error
	MarkAllRead(ctx context.Context, podKey string) (int64, error)

	GetMessages(ctx context.Context, podKey string, unreadOnly bool, messageTypes []string, limit, offset int) ([]*AgentMessage, error)
	GetUnreadMessages(ctx context.Context, podKey string, limit int) ([]*AgentMessage, error)
	GetUnreadCount(ctx context.Context, podKey string) (int64, error)
	GetConversation(ctx context.Context, correlationID string, limit int) ([]*AgentMessage, error)
	GetReplies(ctx context.Context, parentMessageID int64) ([]*AgentMessage, error)
	GetSentMessages(ctx context.Context, podKey string, limit, offset int) ([]*AgentMessage, error)
	GetMessagesBetween(ctx context.Context, podA, podB string, limit int) ([]*AgentMessage, error)

	GetPendingRetries(ctx context.Context, before time.Time, limit int) ([]*AgentMessage, error)
	CreateDeadLetter(ctx context.Context, entry *DeadLetterEntry) error
	GetDeadLetters(ctx context.Context, limit, offset int) ([]*DeadLetterEntry, error)
	GetDeadLetterWithMessage(ctx context.Context, id int64) (*DeadLetterEntry, error)
	SaveDeadLetter(ctx context.Context, entry *DeadLetterEntry) error
	CleanupExpiredDeadLetters(ctx context.Context, olderThan time.Time) (int64, error)
}
