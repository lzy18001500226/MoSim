package channelconnect

import (
	"encoding/json"
	"errors"

	channeldomain "github.com/anthropics/agentsmesh/backend/internal/domain/channel"
	channelservice "github.com/anthropics/agentsmesh/backend/internal/service/channel"
	channelv1 "github.com/anthropics/agentsmesh/proto/gen/go/channel/v1"
)

// resolveSendContent / resolveEditContent mirror REST's resolveContent
// (channel_messages.go:74): accept either `source` (markdown — parsed
// server-side via channelservice.ParseMarkdown) or `content_json` (pre-built
// MessageContent AST), but not both. `attachment_key` is permitted on its
// own (text=empty + attachment).
func resolveSendContent(req *channelv1.SendChannelMessageRequest) (channeldomain.MessageContent, error) {
	return resolveContent(
		req.Source, req.GetMentions(), req.ContentJson, req.GetAttachmentKey(),
	)
}

func resolveEditContent(req *channelv1.EditChannelMessageRequest) (channeldomain.MessageContent, error) {
	return resolveContent(
		req.Source, req.GetMentions(), req.ContentJson, req.GetAttachmentKey(),
	)
}

func resolveContent(
	source *string, mentions map[string]*channelv1.MentionRef,
	contentJSON *string, attachmentKey string,
) (channeldomain.MessageContent, error) {
	hasSource := source != nil && *source != ""
	hasContent := contentJSON != nil && *contentJSON != ""
	if hasSource && hasContent {
		return channeldomain.MessageContent{}, errors.New("provide either source or content_json, not both")
	}
	var resolved channeldomain.MessageContent
	switch {
	case hasSource:
		refs := make(map[string]channelservice.MentionRef, len(mentions))
		for k, v := range mentions {
			if v == nil {
				continue
			}
			refs[k] = channelservice.MentionRef{EntityType: v.GetEntityType(), EntityKey: v.GetEntityKey()}
		}
		parsed, err := channelservice.ParseMarkdown(*source, refs)
		if err != nil {
			return channeldomain.MessageContent{}, err
		}
		resolved = parsed
	case hasContent:
		if err := json.Unmarshal([]byte(*contentJSON), &resolved); err != nil {
			return channeldomain.MessageContent{}, err
		}
	case attachmentKey != "":
		resolved = channeldomain.MessageContent{Kind: "text"}
	default:
		return channeldomain.MessageContent{}, errors.New("source, content_json, or attachment_key is required")
	}
	if attachmentKey != "" {
		resolved.AttachmentKey = attachmentKey
	}
	return resolved, nil
}

// clampLimit bounds an optional pagination limit. Absent / non-positive →
// defaultVal; overflow → max. Matches REST clamps (channel_messages.go:24,
// channel_members.go:21).
func clampLimit(p *int32, defaultVal, max int32) int32 {
	if p == nil || *p <= 0 {
		return defaultVal
	}
	if *p > max {
		return max
	}
	return *p
}
