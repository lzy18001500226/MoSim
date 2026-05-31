package middleware_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/pkg/apierr"
	"github.com/gin-gonic/gin"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/alicebob/miniredis/v2"
)

func setupRedisForTest(t *testing.T) (*redis.Client, func()) {
	t.Helper()
	mr := miniredis.RunT(t)
	client := redis.NewClient(&redis.Options{Addr: mr.Addr()})
	return client, func() { client.Close(); mr.Close() }
}

func newTestRouter(mw gin.HandlerFunc) *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.POST("/test", mw, func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})
	return r
}

func TestRateLimiter_AllowsWithinLimit(t *testing.T) {
	client, cleanup := setupRedisForTest(t)
	defer cleanup()

	mw := middleware.IPRateLimiter(client, "login", 5, time.Minute)
	router := newTestRouter(mw)

	for i := 0; i < 5; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code, "request %d should succeed", i+1)
	}
}

func TestRateLimiter_BlocksOverLimit(t *testing.T) {
	client, cleanup := setupRedisForTest(t)
	defer cleanup()

	mw := middleware.IPRateLimiter(client, "login", 3, time.Minute)
	router := newTestRouter(mw)

	// First 3 requests succeed.
	for i := 0; i < 3; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
	}

	// 4th request is blocked.
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/test", nil)
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusTooManyRequests, w.Code)

	var resp apierr.ErrorResponse
	err := json.Unmarshal(w.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Equal(t, apierr.RATE_LIMITED, resp.Code)
}

func TestRateLimiter_DifferentScopesAreIndependent(t *testing.T) {
	client, cleanup := setupRedisForTest(t)
	defer cleanup()

	gin.SetMode(gin.TestMode)
	r := gin.New()

	loginMw := middleware.IPRateLimiter(client, "login", 2, time.Minute)
	registerMw := middleware.IPRateLimiter(client, "register", 2, time.Minute)

	r.POST("/login", loginMw, func(c *gin.Context) { c.JSON(200, gin.H{"ok": true}) })
	r.POST("/register", registerMw, func(c *gin.Context) { c.JSON(200, gin.H{"ok": true}) })

	// Exhaust login limit.
	for i := 0; i < 2; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/login", nil)
		r.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
	}

	// Login is now blocked.
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/login", nil)
	r.ServeHTTP(w, req)
	assert.Equal(t, http.StatusTooManyRequests, w.Code)

	// Register should still work (different scope).
	w = httptest.NewRecorder()
	req, _ = http.NewRequest("POST", "/register", nil)
	r.ServeHTTP(w, req)
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestRateLimiter_NilRedisIsNoOp(t *testing.T) {
	mw := middleware.IPRateLimiter(nil, "login", 1, time.Minute)
	router := newTestRouter(mw)

	// Should allow unlimited requests when Redis is nil.
	for i := 0; i < 10; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
	}
}

func TestRateLimiter_EmptyKeySkips(t *testing.T) {
	client, cleanup := setupRedisForTest(t)
	defer cleanup()

	mw := middleware.RateLimiter(client, middleware.RateLimitConfig{
		MaxAttempts: 1,
		Window:      time.Minute,
		KeyFunc:     func(c *gin.Context) string { return "" },
	})
	router := newTestRouter(mw)

	for i := 0; i < 10; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
	}
}

// injectUserID returns a middleware that sets c.Set("user_id", uid) — used to
// simulate AuthMiddleware in front of UserRateLimiter tests.
func injectUserID(uid int64) gin.HandlerFunc {
	return func(c *gin.Context) {
		if uid != 0 {
			c.Set("user_id", uid)
		}
		c.Next()
	}
}

func TestUserRateLimiter_KeysByUserID_Independent(t *testing.T) {
	client, cleanup := setupRedisForTest(t)
	defer cleanup()

	gin.SetMode(gin.TestMode)
	r := gin.New()

	mw := middleware.UserRateLimiter(client, "orgs-personal", 2, time.Minute)
	r.POST("/u/:id/test",
		func(c *gin.Context) {
			// Map :id to user_id so we can hit one route with different users.
			var uid int64
			switch c.Param("id") {
			case "1":
				uid = 1
			case "2":
				uid = 2
			}
			c.Set("user_id", uid)
		},
		mw,
		func(c *gin.Context) { c.JSON(200, gin.H{"ok": true}) },
	)

	// User 1 exhausts limit.
	for i := 0; i < 2; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/u/1/test", nil)
		r.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code, "user 1 request %d", i+1)
	}
	// User 1's 3rd request blocked.
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/u/1/test", nil)
	r.ServeHTTP(w, req)
	assert.Equal(t, http.StatusTooManyRequests, w.Code)

	// User 2 unaffected.
	w = httptest.NewRecorder()
	req, _ = http.NewRequest("POST", "/u/2/test", nil)
	r.ServeHTTP(w, req)
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestUserRateLimiter_FallsBackToIP_WhenUnauthenticated(t *testing.T) {
	client, cleanup := setupRedisForTest(t)
	defer cleanup()

	gin.SetMode(gin.TestMode)
	r := gin.New()
	mw := middleware.UserRateLimiter(client, "orgs-personal", 2, time.Minute)
	r.POST("/test", mw, func(c *gin.Context) { c.JSON(200, gin.H{"ok": true}) })

	send := func(remoteAddr string) *httptest.ResponseRecorder {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		req.RemoteAddr = remoteAddr
		r.ServeHTTP(w, req)
		return w
	}

	// Same IP: 3rd request blocked.
	for i := 0; i < 2; i++ {
		assert.Equal(t, http.StatusOK, send("1.2.3.4:5678").Code)
	}
	assert.Equal(t, http.StatusTooManyRequests, send("1.2.3.4:5678").Code)

	// Different IP: independent bucket, still allowed.
	assert.Equal(t, http.StatusOK, send("9.9.9.9:1111").Code)
}

func TestUserRateLimiter_EmptyIPAndUserSkipsCounting(t *testing.T) {
	client, cleanup := setupRedisForTest(t)
	defer cleanup()

	gin.SetMode(gin.TestMode)
	r := gin.New()
	// Stub TrustedPlatform so ClientIP() returns "" when RemoteAddr is empty.
	r.TrustedPlatform = ""
	mw := middleware.UserRateLimiter(client, "orgs-personal", 1, time.Minute)
	r.POST("/test", mw, func(c *gin.Context) { c.JSON(200, gin.H{"ok": true}) })

	// httptest default RemoteAddr is empty → ClientIP() empty → KeyFunc returns
	// "" → RateLimiter skips counting → no global shared bucket.
	for i := 0; i < 5; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		req.RemoteAddr = ""
		r.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code, "empty IP+user must not enter limiter")
	}
}

func TestUserRateLimiter_NilRedisIsNoOp(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	mw := middleware.UserRateLimiter(nil, "orgs-personal", 1, time.Minute)
	r.POST("/test", injectUserID(42), mw, func(c *gin.Context) { c.JSON(200, gin.H{"ok": true}) })

	for i := 0; i < 5; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		r.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
	}
}

func TestRateLimiter_DisabledEnvBypassesAllChecks(t *testing.T) {
	t.Setenv("RATE_LIMIT_DISABLED", "true")

	client, cleanup := setupRedisForTest(t)
	defer cleanup()

	// MaxAttempts=1 — without the bypass the second request would 429.
	mw := middleware.IPRateLimiter(client, "login", 1, time.Minute)
	router := newTestRouter(mw)

	for i := 0; i < 10; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code, "RATE_LIMIT_DISABLED must short-circuit request %d", i+1)
	}
}
