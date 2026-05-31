package client

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"
)

const defaultRESTTimeout = 30 * time.Second

// REST is a Connect-RPC client wrapping the backend's gRPC surface. Despite
// the legacy name, R5 retired the user-facing REST routes (/api/v1/orgs/...)
// in favour of Connect-RPC procedures (/proto.*.v1.<Service>/<Method>). Each
// method below issues a Connect-protocol POST against the bare-rooted base
// URL with `Content-Type: application/json` and `Connect-Protocol-Version: 1`.
//
// Wire-shape notes:
//   - Connect's JSON profile uses **camelCase** field names (`pod_key` → `podKey`).
//   - `int64` fields ship as **JSON strings** (Connect's escape hatch against
//     53-bit float truncation in JS clients) — `strconv.ParseInt` on the way out.
//   - Procedures whose proto returns a bare message (e.g. `rpc GetPod returns Pod`)
//     unmarshal into the message directly; wrapped responses (e.g.
//     `CreatePodResponse{pod, warning}`) need an envelope struct.
type REST struct {
	baseURL string
	token   string
	hc      *http.Client
}

func NewREST(baseURL string) *REST {
	return &REST{
		baseURL: baseURL,
		hc:      &http.Client{Timeout: defaultRESTTimeout},
	}
}

// SetToken installs the bearer token returned by Login on every subsequent
// request. Tests typically call this once after a process-wide login.
func (r *REST) SetToken(t string) { r.token = t }

// connectCall is the single Connect-RPC wire helper used by every method
// below. It posts `req` as JSON to `procedure` (e.g.
// "/proto.pod.v1.PodService/CreatePod"), then unmarshals the body into
// `out` if non-nil. Caller is responsible for envelope shape — Connect
// procedures return either a wrapped response message or the bare proto
// (matching the .proto `returns ...`).
//
// `r.baseURL` is configured with the REST `/api/v1` suffix (legacy
// fixture/env.go); Connect handlers mount at the bare `/proto.*` root in
// `backend/cmd/server/connect_init.go`, so the suffix is stripped here.
func (r *REST) connectCall(ctx context.Context, procedure string, req, out any) error {
	connectBase := strings.TrimSuffix(r.baseURL, "/api/v1")
	body, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("marshal %s: %w", procedure, err)
	}
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost,
		connectBase+procedure, bytes.NewReader(body))
	if err != nil {
		return err
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Connect-Protocol-Version", "1")
	if r.token != "" {
		httpReq.Header.Set("Authorization", "Bearer "+r.token)
	}
	resp, err := r.hc.Do(httpReq)
	if err != nil {
		return fmt.Errorf("connect %s: %w", procedure, err)
	}
	defer resp.Body.Close()
	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	if resp.StatusCode/100 != 2 {
		return fmt.Errorf("connect %s -> %d: %s", procedure, resp.StatusCode, string(raw))
	}
	if out == nil || len(raw) == 0 {
		return nil
	}
	if err := json.Unmarshal(raw, out); err != nil {
		return fmt.Errorf("decode %s: %w (body=%s)", procedure, err, string(raw))
	}
	return nil
}

// --- AuthService.Login ---

type LoginResponse struct {
	Token        string `json:"token"`
	RefreshToken string `json:"refresh_token"`
	ExpiresIn    int64  `json:"expires_in"`
}

func (r *REST) Login(ctx context.Context, email, password string) (*LoginResponse, error) {
	req := map[string]string{"email": email, "password": password}
	// int64 fields ship as JSON strings in Connect; decode then ParseInt.
	var out struct {
		Token        string `json:"token"`
		RefreshToken string `json:"refreshToken"`
		ExpiresIn    string `json:"expiresIn"`
	}
	if err := r.connectCall(ctx, "/proto.auth.v1.AuthService/Login", req, &out); err != nil {
		return nil, err
	}
	expiresIn, _ := strconv.ParseInt(out.ExpiresIn, 10, 64)
	return &LoginResponse{
		Token:        out.Token,
		RefreshToken: out.RefreshToken,
		ExpiresIn:    expiresIn,
	}, nil
}

// --- RunnerService.ListRunners ---

type Runner struct {
	ID     int64  `json:"-"`
	NodeID string `json:"nodeId"`
	Status string `json:"status"`
}

func (r *REST) ListRunners(ctx context.Context, orgSlug string) ([]Runner, error) {
	req := map[string]string{"orgSlug": orgSlug}
	var out struct {
		Items []struct {
			ID     string `json:"id"`
			NodeID string `json:"nodeId"`
			Status string `json:"status"`
		} `json:"items"`
	}
	if err := r.connectCall(ctx, "/proto.runner_api.v1.RunnerService/ListRunners", req, &out); err != nil {
		return nil, err
	}
	runners := make([]Runner, 0, len(out.Items))
	for _, item := range out.Items {
		id, perr := strconv.ParseInt(item.ID, 10, 64)
		if perr != nil {
			return nil, fmt.Errorf("decode runner id %q: %w", item.ID, perr)
		}
		runners = append(runners, Runner{ID: id, NodeID: item.NodeID, Status: item.Status})
	}
	return runners, nil
}

// --- PodService.{CreatePod, TerminatePod, GetPod} ---

type CreatePodRequest struct {
	AgentSlug      string  `json:"agentSlug"`
	RunnerID       int64   `json:"runnerId,omitempty,string"`
	Alias          *string `json:"alias,omitempty"`
	AgentfileLayer *string `json:"agentfileLayer,omitempty"`
	Cols           int32   `json:"cols"`
	Rows           int32   `json:"rows"`
}

type Pod struct {
	ID      int64  `json:"-"`
	PodKey  string `json:"podKey"`
	Status  string `json:"status"`
	Agent   string `json:"agentSlug"`
	OrgSlug string `json:"organizationSlug,omitempty"`
}

// decodePodWire converts Connect's wire-shape Pod (id-as-string) to the
// public `Pod` type, parsing the int64. Shared by Create/Get.
func decodePodWire(raw json.RawMessage) (*Pod, error) {
	var wire struct {
		ID      string `json:"id"`
		PodKey  string `json:"podKey"`
		Status  string `json:"status"`
		Agent   string `json:"agentSlug"`
		OrgSlug string `json:"organizationSlug,omitempty"`
	}
	if err := json.Unmarshal(raw, &wire); err != nil {
		return nil, err
	}
	id, _ := strconv.ParseInt(wire.ID, 10, 64)
	return &Pod{ID: id, PodKey: wire.PodKey, Status: wire.Status, Agent: wire.Agent, OrgSlug: wire.OrgSlug}, nil
}

func (r *REST) CreatePod(ctx context.Context, orgSlug string, req CreatePodRequest) (*Pod, error) {
	type wirePodReq struct {
		OrgSlug        string  `json:"orgSlug"`
		AgentSlug      string  `json:"agentSlug"`
		RunnerID       string  `json:"runnerId,omitempty"`
		Alias          *string `json:"alias,omitempty"`
		AgentfileLayer *string `json:"agentfileLayer,omitempty"`
		Cols           int32   `json:"cols"`
		Rows           int32   `json:"rows"`
	}
	wireReq := wirePodReq{
		OrgSlug:        orgSlug,
		AgentSlug:      req.AgentSlug,
		Alias:          req.Alias,
		AgentfileLayer: req.AgentfileLayer,
		Cols:           req.Cols,
		Rows:           req.Rows,
	}
	if req.RunnerID != 0 {
		wireReq.RunnerID = strconv.FormatInt(req.RunnerID, 10)
	}
	var resp struct {
		Pod     json.RawMessage `json:"pod"`
		Warning string          `json:"warning,omitempty"`
	}
	if err := r.connectCall(ctx, "/proto.pod.v1.PodService/CreatePod", wireReq, &resp); err != nil {
		return nil, err
	}
	return decodePodWire(resp.Pod)
}

func (r *REST) TerminatePod(ctx context.Context, orgSlug, podKey string) error {
	req := map[string]string{"orgSlug": orgSlug, "podKey": podKey}
	return r.connectCall(ctx, "/proto.pod.v1.PodService/TerminatePod", req, nil)
}

func (r *REST) GetPod(ctx context.Context, orgSlug, podKey string) (*Pod, error) {
	req := map[string]string{"orgSlug": orgSlug, "podKey": podKey}
	// GetPod returns the bare Pod message (no envelope).
	var podRaw json.RawMessage
	if err := r.connectCall(ctx, "/proto.pod.v1.PodService/GetPod", req, &podRaw); err != nil {
		return nil, err
	}
	return decodePodWire(podRaw)
}

// --- OrgService.{CreateOrg, DeleteOrg} ---

type Org struct {
	ID   int64  `json:"-"`
	Name string `json:"name"`
	Slug string `json:"slug"`
}

func (r *REST) CreateOrg(ctx context.Context, name, slug string) (*Org, error) {
	req := map[string]string{"name": name, "slug": slug}
	var wire struct {
		ID   string `json:"id"`
		Name string `json:"name"`
		Slug string `json:"slug"`
	}
	if err := r.connectCall(ctx, "/proto.org.v1.OrgService/CreateOrg", req, &wire); err != nil {
		return nil, err
	}
	if wire.Slug == "" {
		return nil, fmt.Errorf("create_org returned empty slug; raw=%+v", wire)
	}
	id, _ := strconv.ParseInt(wire.ID, 10, 64)
	return &Org{ID: id, Name: wire.Name, Slug: wire.Slug}, nil
}

func (r *REST) DeleteOrg(ctx context.Context, slug string) error {
	req := map[string]string{"orgSlug": slug}
	return r.connectCall(ctx, "/proto.org.v1.OrgService/DeleteOrg", req, nil)
}

// --- TicketService.CreateTicket ---

type CreateTicketRequest struct {
	Title    string `json:"title"`
	Content  string `json:"content,omitempty"`
	Priority string `json:"priority,omitempty"`
}

type Ticket struct {
	ID    int64  `json:"-"`
	Slug  string `json:"slug"`
	Title string `json:"title"`
}

func (r *REST) CreateTicket(ctx context.Context, orgSlug string, req CreateTicketRequest) (*Ticket, error) {
	wireReq := map[string]any{
		"orgSlug":  orgSlug,
		"title":    req.Title,
		"content":  req.Content,
		"priority": req.Priority,
	}
	var wire struct {
		ID    string `json:"id"`
		Slug  string `json:"slug"`
		Title string `json:"title"`
	}
	if err := r.connectCall(ctx, "/proto.ticket.v1.TicketService/CreateTicket", wireReq, &wire); err != nil {
		return nil, err
	}
	id, _ := strconv.ParseInt(wire.ID, 10, 64)
	return &Ticket{ID: id, Slug: wire.Slug, Title: wire.Title}, nil
}

// --- LoopService.{CreateLoop, EnableLoop} ---

type CreateLoopRequest struct {
	Name           string `json:"name"`
	AgentSlug      string `json:"agent_slug"`
	PromptTemplate string `json:"prompt_template"`
	RunnerID       *int64 `json:"runner_id,omitempty"`
}

type Loop struct {
	ID   int64  `json:"-"`
	Slug string `json:"slug"`
	Name string `json:"name"`
}

func (r *REST) CreateLoop(ctx context.Context, orgSlug string, req CreateLoopRequest) (*Loop, error) {
	wireReq := map[string]any{
		"orgSlug":        orgSlug,
		"name":           req.Name,
		"slug":           "",
		"description":    "",
		"agentSlug":      req.AgentSlug,
		"permissionMode": "bypassPermissions",
		"promptTemplate": req.PromptTemplate,
		// JSON-encoded payloads ship as raw strings.
		"promptVariablesJson": "{}",
		"configOverridesJson": "{}",
		"autopilotConfigJson": "{}",
		"branchName":          "",
		"executionMode":       "direct",
		"cronExpression":      "",
		"callbackUrl":         "",
		"sandboxStrategy":     "fresh",
		"concurrencyPolicy":   "skip",
	}
	if req.RunnerID != nil {
		wireReq["runnerId"] = strconv.FormatInt(*req.RunnerID, 10)
	}
	var wire struct {
		ID   string `json:"id"`
		Slug string `json:"slug"`
		Name string `json:"name"`
	}
	if err := r.connectCall(ctx, "/proto.loop.v1.LoopService/CreateLoop", wireReq, &wire); err != nil {
		return nil, err
	}
	id, _ := strconv.ParseInt(wire.ID, 10, 64)
	return &Loop{ID: id, Slug: wire.Slug, Name: wire.Name}, nil
}

func (r *REST) EnableLoop(ctx context.Context, orgSlug, loopSlug string) error {
	req := map[string]string{"orgSlug": orgSlug, "loopSlug": loopSlug}
	return r.connectCall(ctx, "/proto.loop.v1.LoopService/EnableLoop", req, nil)
}
