package admin

import (
	"github.com/anthropics/agentsmesh/backend/internal/service/admin"
	"github.com/anthropics/agentsmesh/backend/internal/service/auth"
	"github.com/anthropics/agentsmesh/backend/internal/service/billing"
)

// Services contains all admin-related services. Kept as a struct because
// `backend/cmd/server/services_init.go` still wires the bundle even
// though there are no REST routes left to mount — Connect handlers
// access these services via `serviceContainer` directly. Removing the
// struct is a separate cleanup.
type Services struct {
	Auth    *auth.Service
	Admin   *admin.Service
	Billing *billing.Service
}
