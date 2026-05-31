package dns

import "encoding/json"

type cloudflareResponse struct {
	Success bool            `json:"success"`
	Errors  []cloudflareError `json:"errors"`
	Result  json.RawMessage `json:"result"`
}

type cloudflareError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

type cloudflareRecord struct {
	ID      string `json:"id"`
	Type    string `json:"type"`
	Name    string `json:"name"`
	Content string `json:"content"`
	TTL     int    `json:"ttl"`
	Proxied bool   `json:"proxied"`
}
