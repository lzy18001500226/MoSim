package dns

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

const cloudflareAPIBase = "https://api.cloudflare.com/client/v4"

type CloudflareProvider struct {
	apiToken string
	zoneID   string
	client   *http.Client
}

func NewCloudflareProvider(apiToken, zoneID string) *CloudflareProvider {
	return &CloudflareProvider{
		apiToken: apiToken,
		zoneID:   zoneID,
		client: &http.Client{
			Timeout:   30 * time.Second,
			Transport: otelhttp.NewTransport(http.DefaultTransport),
		},
	}
}

func (p *CloudflareProvider) CreateRecord(ctx context.Context, subdomain, ip string) error {
	existing, err := p.getRecordID(ctx, subdomain)
	if err != nil {
		return err
	}
	if existing != "" {
		return p.updateRecordByID(ctx, existing, ip)
	}

	payload := map[string]interface{}{
		"type":    "A",
		"name":    subdomain,
		"content": ip,
		"ttl":     300,
		"proxied": false,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	url := fmt.Sprintf("%s/zones/%s/dns_records", cloudflareAPIBase, p.zoneID)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	resp, err := p.doRequest(req)
	if err != nil {
		return err
	}
	if !resp.Success {
		return fmt.Errorf("cloudflare API error: %v", resp.Errors)
	}
	return nil
}

func (p *CloudflareProvider) DeleteRecord(ctx context.Context, subdomain string) error {
	recordID, err := p.getRecordID(ctx, subdomain)
	if err != nil {
		return err
	}
	if recordID == "" {
		return nil
	}

	url := fmt.Sprintf("%s/zones/%s/dns_records/%s", cloudflareAPIBase, p.zoneID, recordID)
	req, err := http.NewRequestWithContext(ctx, "DELETE", url, nil)
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	resp, err := p.doRequest(req)
	if err != nil {
		return err
	}
	if !resp.Success {
		return fmt.Errorf("cloudflare API error: %v", resp.Errors)
	}
	return nil
}

func (p *CloudflareProvider) GetRecord(ctx context.Context, subdomain string) (string, error) {
	records, err := p.listRecords(ctx, subdomain)
	if err != nil {
		return "", err
	}
	if len(records) == 0 {
		return "", nil
	}
	return records[0].Content, nil
}

func (p *CloudflareProvider) UpdateRecord(ctx context.Context, subdomain, ip string) error {
	recordID, err := p.getRecordID(ctx, subdomain)
	if err != nil {
		return err
	}
	if recordID == "" {
		return p.CreateRecord(ctx, subdomain, ip)
	}
	return p.updateRecordByID(ctx, recordID, ip)
}

func (p *CloudflareProvider) getRecordID(ctx context.Context, subdomain string) (string, error) {
	records, err := p.listRecords(ctx, subdomain)
	if err != nil {
		return "", err
	}
	if len(records) == 0 {
		return "", nil
	}
	return records[0].ID, nil
}

func (p *CloudflareProvider) listRecords(ctx context.Context, subdomain string) ([]cloudflareRecord, error) {
	url := fmt.Sprintf("%s/zones/%s/dns_records?type=A&name=%s", cloudflareAPIBase, p.zoneID, subdomain)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	resp, err := p.doRequest(req)
	if err != nil {
		return nil, err
	}
	if !resp.Success {
		return nil, fmt.Errorf("cloudflare API error: %v", resp.Errors)
	}

	var records []cloudflareRecord
	if err := json.Unmarshal(resp.Result, &records); err != nil {
		return nil, fmt.Errorf("unmarshal records: %w", err)
	}
	return records, nil
}

func (p *CloudflareProvider) updateRecordByID(ctx context.Context, recordID, ip string) error {
	payload := map[string]interface{}{
		"type":    "A",
		"content": ip,
		"ttl":     300,
		"proxied": false,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	url := fmt.Sprintf("%s/zones/%s/dns_records/%s", cloudflareAPIBase, p.zoneID, recordID)
	req, err := http.NewRequestWithContext(ctx, "PATCH", url, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	resp, err := p.doRequest(req)
	if err != nil {
		return err
	}
	if !resp.Success {
		return fmt.Errorf("cloudflare API error: %v", resp.Errors)
	}
	return nil
}

func (p *CloudflareProvider) doRequest(req *http.Request) (*cloudflareResponse, error) {
	req.Header.Set("Authorization", "Bearer "+p.apiToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("http request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read response: %w", err)
	}

	var cfResp cloudflareResponse
	if err := json.Unmarshal(body, &cfResp); err != nil {
		return nil, fmt.Errorf("unmarshal response: %w", err)
	}
	return &cfResp, nil
}
