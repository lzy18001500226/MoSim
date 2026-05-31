package suites

import (
	"context"
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Channel tools return formatted text (single-record fields or markdown
// tables). We extract the new channel id with a regex so the rest of the
// flow can refer to it by id, and assert downstream tools by substring.

var channelIDRE = regexp.MustCompile(`(?:Channel|ID)[^\d]*(\d+)`)

func TestChannel_FullLifecycle(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	name := fmt.Sprintf("e2e-ch-%d", time.Now().UnixMilli())

	// 1) create_channel — extract numeric id from "Channel: NAME (ID: X)"
	out, err := pod.MCP.CallToolText(ctx, "create_channel", map[string]any{
		"name":        name,
		"description": "e2e channel suite",
	})
	if err != nil {
		t.Fatalf("create_channel: %v", err)
	}
	if !strings.Contains(out, name) {
		t.Errorf("create_channel output missing channel name %q:\n%s", name, out)
	}
	channelID, err := extractChannelID(out)
	if err != nil {
		t.Fatalf("could not parse channel id from create_channel output: %v\n%s", err, out)
	}

	// 2) search_channels — must surface our newly created channel.
	searchOut, err := pod.MCP.CallToolText(ctx, "search_channels", map[string]any{
		"name":  name,
		"limit": 5,
	})
	if err != nil {
		t.Fatalf("search_channels: %v", err)
	}
	if !strings.Contains(searchOut, name) {
		t.Errorf("search_channels output missing %q:\n%s", name, searchOut)
	}

	// 3) get_channel by id.
	getOut, err := pod.MCP.CallToolText(ctx, "get_channel", map[string]any{
		"channel_id": channelID,
	})
	if err != nil {
		t.Fatalf("get_channel: %v", err)
	}
	if !strings.Contains(getOut, name) {
		t.Errorf("get_channel output missing channel name:\n%s", getOut)
	}

	// 4) send_channel_message — verify the body lands in subsequent reads.
	body := "hello from mcp e2e"
	if _, err := pod.MCP.CallToolText(ctx, "send_channel_message", map[string]any{
		"channel_id": channelID,
		"content":    body,
	}); err != nil {
		t.Fatalf("send_channel_message: %v", err)
	}

	msgsOut, err := pod.MCP.CallToolText(ctx, "get_channel_messages", map[string]any{
		"channel_id": channelID,
		"limit":      10,
	})
	if err != nil {
		t.Fatalf("get_channel_messages: %v", err)
	}
	if !strings.Contains(msgsOut, body) {
		t.Errorf("get_channel_messages missing body %q:\n%s", body, msgsOut)
	}

	// 5) document round-trip: GET (likely empty), then UPDATE.
	if _, err := pod.MCP.CallToolText(ctx, "get_channel_document", map[string]any{
		"channel_id": channelID,
	}); err != nil {
		t.Fatalf("get_channel_document: %v", err)
	}
	if _, err := pod.MCP.CallToolText(ctx, "update_channel_document", map[string]any{
		"channel_id": channelID,
		"document":   "# Channel Notes\n\nFirst draft.",
	}); err != nil {
		t.Fatalf("update_channel_document: %v", err)
	}
}

func extractChannelID(text string) (int, error) {
	// Tolerate either "(ID: 4)" or markdown-table "| 4 |" forms.
	if m := regexp.MustCompile(`ID:\s*(\d+)`).FindStringSubmatch(text); len(m) == 2 {
		return strconv.Atoi(m[1])
	}
	if m := regexp.MustCompile(`\|\s*(\d+)\s*\|`).FindStringSubmatch(text); len(m) == 2 {
		return strconv.Atoi(m[1])
	}
	return 0, fmt.Errorf("no channel id found")
}
