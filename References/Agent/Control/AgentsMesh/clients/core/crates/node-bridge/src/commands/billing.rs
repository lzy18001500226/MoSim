// R2-S2-Billing: legacy JSON-string napi commands removed. Desktop now uses
// the binary `billing_*_connect` lane (same Connect-RPC wire as web/iOS).
//
// If you need to expose a billing operation to the Electron renderer, add a
// `*_connect` napi method that forwards prost-encoded bytes through
// `BillingService::*_connect`.
