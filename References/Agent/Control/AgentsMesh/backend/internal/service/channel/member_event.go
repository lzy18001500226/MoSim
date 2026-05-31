package channel

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/infra/eventbus"
)

func (s *Service) publishMemberEvent(ctx context.Context, ch_orgID, channelID, userID int64, eventType eventbus.EventType, role string) {
	if s.eventBus == nil {
		return
	}

	data, err := json.Marshal(eventbus.ChannelMemberChangedData{
		ChannelID: channelID,
		UserID:    userID,
		Role:      role,
	})
	if err != nil {
		slog.ErrorContext(ctx, "failed to marshal member event", "error", err)
		return
	}

	targetUserIDs, _ := s.repo.GetMemberUserIDs(ctx, channelID)
	if eventType == eventbus.EventChannelMemberAdded {
		found := false
		for _, id := range targetUserIDs {
			if id == userID {
				found = true
				break
			}
		}
		if !found {
			targetUserIDs = append(targetUserIDs, userID)
		}
	} else {
		targetUserIDs = append(targetUserIDs, userID)
	}

	s.eventBus.Publish(ctx, &eventbus.Event{
		Type:           eventType,
		Category:       eventbus.CategoryEntity,
		OrganizationID: ch_orgID,
		EntityType:     "channel",
		EntityID:       fmt.Sprintf("%d", channelID),
		Data:           data,
		Timestamp:      time.Now().UnixMilli(),
		TargetUserIDs:  targetUserIDs,
	})
}
