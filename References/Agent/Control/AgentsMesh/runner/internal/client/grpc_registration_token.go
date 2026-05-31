// Package client provides gRPC registration for Runner.
package client

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// ==================== Pre-generated Token Registration ====================

// TokenRegistrationRequest contains parameters for token-based registration.
type TokenRegistrationRequest struct {
	ServerURL string // Base server URL
	Token     string // Pre-generated registration token
	NodeID    string // Optional node ID
}

// TokenRegistrationResult contains the result of token-based registration.
type TokenRegistrationResult struct {
	RunnerID      int64  `json:"runner_id"`
	Certificate   string `json:"certificate"`
	PrivateKey    string `json:"private_key"`
	CACertificate string `json:"ca_certificate"`
	GRPCEndpoint  string `json:"grpc_endpoint"`
	OrgSlug       string `json:"org_slug"`
}

// RegisterWithToken registers a runner using a pre-generated token.
// Direct registration without browser authorization.
func RegisterWithToken(ctx context.Context, req TokenRegistrationRequest) (*TokenRegistrationResult, error) {
	requestURL := fmt.Sprintf("%s/api/v1/runners/grpc/register", req.ServerURL)

	body := map[string]interface{}{
		"token": req.Token,
	}
	if req.NodeID != "" {
		body["node_id"] = req.NodeID
	}

	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request body: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", requestURL, bytes.NewReader(bodyBytes))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusUnauthorized {
		return nil, fmt.Errorf("invalid or expired token")
	}
	if resp.StatusCode == http.StatusConflict {
		return nil, fmt.Errorf("runner with this node_id already exists")
	}
	if resp.StatusCode == http.StatusPaymentRequired {
		return nil, fmt.Errorf("runner quota exceeded")
	}
	if resp.StatusCode != http.StatusCreated {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("server returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var result TokenRegistrationResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	if result.Certificate == "" {
		return nil, fmt.Errorf("server returned empty certificate")
	}

	return &result, nil
}
