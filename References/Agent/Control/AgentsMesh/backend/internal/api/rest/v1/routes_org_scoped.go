package v1

import (
	"github.com/gin-gonic/gin"
)

func RegisterOrgScopedRoutes(rg *gin.RouterGroup, svc *Services) {
	registerRunnerRoutes(rg, svc)
	registerBillingRoutes(rg, svc)
}
