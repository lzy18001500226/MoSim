package fixture

import (
	"context"
	"sync"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/client"
)

// loginCache memoises tokens per (email, password) pair so each user logs
// in once per process, not once per test.
type loginCache struct {
	mu    sync.Mutex
	rests map[string]*client.REST
}

var sharedLogins = &loginCache{rests: map[string]*client.REST{}}

func (c *loginCache) get(t *testing.T, env *Env, email, password string) *client.REST {
	t.Helper()
	c.mu.Lock()
	defer c.mu.Unlock()
	if r, ok := c.rests[email]; ok {
		return r
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	rest := client.NewREST(env.BackendBaseURL)
	resp, err := rest.Login(ctx, email, password)
	if err != nil {
		t.Fatalf("login %s failed (is deploy/dev:up running?): %v", email, err)
	}
	rest.SetToken(resp.Token)
	c.rests[email] = rest
	return rest
}

// SharedREST returns a REST client authenticated as the primary dev user
// (env.DevUser). Cached for the lifetime of the test process.
func SharedREST(t *testing.T, env *Env) *client.REST {
	t.Helper()
	return sharedLogins.get(t, env, env.DevUser, env.DevPassword)
}

// SecondaryREST returns a REST client authenticated as the second dev user
// (dev2@agentsmesh.local in seed.sql). Used for tests that need two distinct
// users in the same org — primarily binding pending → accept flows where the
// initiator and target must be different humans for binding to start in
// `pending` state instead of auto-activating.
func SecondaryREST(t *testing.T, env *Env) *client.REST {
	t.Helper()
	return sharedLogins.get(t, env, env.SecondaryUser, env.SecondaryPassword)
}
