package v1

// Billing org-scoped REST handlers all migrated to Connect — see
// backend/internal/api/connect/billing. File upload presign also fully
// on Connect (proto.file.v1.FileService.PresignUpload); REST FileHandler
// + /files/presign route removed once Rust core moved off the REST shim.
// Stub kept so the route group composes cleanly with the rest of the
// org-scoped routes (routes_org_scoped.go).

import "github.com/gin-gonic/gin"

func registerBillingRoutes(_ *gin.RouterGroup, _ *Services) {}
