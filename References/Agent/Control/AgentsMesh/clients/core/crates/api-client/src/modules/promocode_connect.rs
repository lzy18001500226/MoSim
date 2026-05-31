use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_promocode_v1 as pc_proto;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================
//
// Org-scoped PromoCodeService — every request carries `org_slug` at tag 1
// (conventions §3.5). The auth interceptor injects UserID; the Go handler
// resolves the org via ResolveOrgScope and enforces owner-only on Redeem.
//
// Scope: validate / redeem / get_redemption_history. Platform-admin CRUD
// over promo codes stays on REST during this migration — those endpoints
// gate on the ADMIN middleware, not org middleware, so they ship in the
// admin/ surface sweep.
//
// Procedure paths derive from `proto.promocode.v1.PromoCodeService/<Method>`
// (conventions §12). connect_call enforces application/proto and Connect
// protocol headers.

impl ApiClient {
    pub async fn validate_promo_code_connect(
        &self,
        req: &pc_proto::ValidatePromoCodeRequest,
    ) -> Result<pc_proto::ValidatePromoCodeResponse, ApiError> {
        connect_call(
            self,
            "/proto.promocode.v1.PromoCodeService/Validate",
            req,
        )
        .await
    }

    pub async fn redeem_promo_code_connect(
        &self,
        req: &pc_proto::RedeemPromoCodeRequest,
    ) -> Result<pc_proto::RedeemPromoCodeResponse, ApiError> {
        connect_call(
            self,
            "/proto.promocode.v1.PromoCodeService/Redeem",
            req,
        )
        .await
    }

    pub async fn get_redemption_history_connect(
        &self,
        req: &pc_proto::GetRedemptionHistoryRequest,
    ) -> Result<pc_proto::GetRedemptionHistoryResponse, ApiError> {
        connect_call(
            self,
            "/proto.promocode.v1.PromoCodeService/GetRedemptionHistory",
            req,
        )
        .await
    }
}
