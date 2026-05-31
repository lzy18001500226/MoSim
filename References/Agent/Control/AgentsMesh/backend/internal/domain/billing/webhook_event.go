package billing

import "time"

// WebhookEvent represents a processed webhook event for idempotency checking
type WebhookEvent struct {
	ID          int64     `gorm:"primaryKey" json:"id"`
	EventID     string    `gorm:"size:255;not null;uniqueIndex:uq_webhook_events_event_provider" json:"event_id"`
	Provider    string    `gorm:"size:50;not null;uniqueIndex:uq_webhook_events_event_provider" json:"provider"`
	EventType   string    `gorm:"size:100;not null" json:"event_type"`
	ProcessedAt time.Time `gorm:"not null;default:now()" json:"processed_at"`
}

func (WebhookEvent) TableName() string {
	return "webhook_events"
}
