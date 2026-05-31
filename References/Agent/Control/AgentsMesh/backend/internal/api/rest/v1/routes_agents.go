package v1

import "github.com/gin-gonic/gin"

func registerRunnerRoutes(rg *gin.RouterGroup, svc *Services) {
	if svc.GRPCRunnerHandler == nil {
		return
	}
	runners := rg.Group("/runners")
	RegisterOrgGRPCRunnerRoutes(runners, svc.GRPCRunnerHandler)
}
