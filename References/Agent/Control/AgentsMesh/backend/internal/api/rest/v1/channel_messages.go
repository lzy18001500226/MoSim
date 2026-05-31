package v1

import (
	"errors"
	"net/http"
	"strconv"

	channelDomain "github.com/anthropics/agentsmesh/backend/internal/domain/channel"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	channelService "github.com/anthropics/agentsmesh/backend/internal/service/channel"
	"github.com/anthropics/agentsmesh/backend/pkg/apierr"
	"github.com/gin-gonic/gin"
)

// MentionRefRequest is the wire-format mapping a `@<key>` substring in a
// markdown source string to a typed entity reference. Used by SendMessage
// when `source` is supplied.
type MentionRefRequest struct {
	EntityType string `json:"entity_type"`
	EntityKey  string `json:"entity_key"`
}

// SendMessageRequest accepts EITHER a markdown source string (server parses to
// AST) OR a pre-built MessageContent AST. Sending both is a 400.
type SendMessageRequest struct {
	Source        *string                       `json:"source,omitempty"`
	Mentions      map[string]MentionRefRequest  `json:"mentions,omitempty"`
	Content       *channelDomain.MessageContent `json:"content,omitempty"`
	AttachmentKey string                        `json:"attachment_key,omitempty"`
	PodKey        string                        `json:"pod_key"`
	ReplyTo       *int64                        `json:"reply_to"`
}

// ListMessages lists channel messages.
// Retained for routes_ext.go (third-party API key callers reading messages).
func (h *ChannelHandler) ListMessages(c *gin.Context) {
	ch, ok := h.requireChannelAccess(c)
	if !ok {
		return
	}

	limit := 50
	if l := c.Query("limit"); l != "" {
		if parsed, err := strconv.Atoi(l); err == nil && parsed > 0 && parsed <= 100 {
			limit = parsed
		}
	}

	var messages []*channelDomain.Message
	var hasMore bool
	if beforeIDStr := c.Query("before_id"); beforeIDStr != "" {
		beforeID, err := strconv.ParseInt(beforeIDStr, 10, 64)
		if err != nil {
			apierr.InvalidInput(c, "Invalid before_id")
			return
		}
		messages, hasMore, err = h.channelService.GetMessagesByCursor(c.Request.Context(), ch.ID, beforeID, limit)
		if err != nil {
			apierr.InternalError(c, "Failed to list messages")
			return
		}
	} else {
		var fetchErr error
		messages, hasMore, fetchErr = h.channelService.GetMessages(c.Request.Context(), ch.ID, nil, nil, limit)
		if fetchErr != nil {
			apierr.InternalError(c, "Failed to list messages")
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{"messages": messages, "has_more": hasMore})
}

func resolveContent(source *string, mentions map[string]MentionRefRequest, content *channelDomain.MessageContent, attachmentKey string) (channelDomain.MessageContent, error) {
	hasSource := source != nil && *source != ""
	hasContent := content != nil && len(content.Blocks) > 0
	if hasSource && hasContent {
		return channelDomain.MessageContent{}, errors.New("provide either source or content, not both")
	}
	var resolved channelDomain.MessageContent
	switch {
	case hasSource:
		refs := make(map[string]channelService.MentionRef, len(mentions))
		for display, ref := range mentions {
			refs[display] = channelService.MentionRef{EntityType: ref.EntityType, EntityKey: ref.EntityKey}
		}
		c, err := channelService.ParseMarkdown(*source, refs)
		if err != nil {
			return channelDomain.MessageContent{}, err
		}
		resolved = c
	case hasContent:
		resolved = *content
	case attachmentKey != "":
		resolved = channelDomain.MessageContent{Kind: "text"}
	default:
		return channelDomain.MessageContent{}, errors.New("source, content, or attachment_key is required")
	}
	if attachmentKey != "" {
		resolved.AttachmentKey = attachmentKey
	}
	return resolved, nil
}

// SendMessage sends a message to a channel.
// Retained for routes_ext.go (third-party API key callers posting messages).
func (h *ChannelHandler) SendMessage(c *gin.Context) {
	ch, ok := h.requireChannelAccess(c)
	if !ok {
		return
	}

	var req SendMessageRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		apierr.ValidationError(c, err.Error())
		return
	}

	if ch.IsArchived {
		apierr.BadRequest(c, apierr.VALIDATION_FAILED, "Cannot send messages to archived channel")
		return
	}

	content, err := resolveContent(req.Source, req.Mentions, req.Content, req.AttachmentKey)
	if err != nil {
		apierr.BadRequest(c, apierr.VALIDATION_FAILED, err.Error())
		return
	}

	tenant := middleware.GetTenant(c)
	var podKey *string
	if req.PodKey != "" {
		podKey = &req.PodKey
	}

	msg, err := h.channelService.SendMessage(c.Request.Context(), ch.ID, podKey, &tenant.UserID, content, req.ReplyTo)
	if err != nil {
		if errors.Is(err, channelService.ErrNotMember) {
			apierr.ForbiddenAccess(c)
			return
		}
		if errors.Is(err, channelService.ErrEmptyContent) || errors.Is(err, channelService.ErrInvalidContent) {
			apierr.BadRequest(c, apierr.VALIDATION_FAILED, err.Error())
			return
		}
		apierr.InternalError(c, "Failed to send message")
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": msg})
}
