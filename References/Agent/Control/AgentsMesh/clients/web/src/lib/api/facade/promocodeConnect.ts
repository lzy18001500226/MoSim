// Facade re-export of the promocode Connect-RPC adapter. Business code
// imports from here (or from the `@/lib/api` barrel) so the wire-shape
// layer stays internal to the facade boundary. Tests mock this path.

export {
  validatePromoCode,
  redeemPromoCode,
  getRedemptionHistory,
  type PromoCodeType,
  type ValidatePromoCodeResponse,
  type RedeemPromoCodeResponse,
  type PromoCodeRedemption,
} from "../connect/promocodeConnect";
