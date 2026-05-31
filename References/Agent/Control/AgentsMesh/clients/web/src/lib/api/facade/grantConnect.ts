// Facade re-export of the grant Connect-RPC adapter. Business code imports
// from here (or from the `@/lib/api` barrel) so the wire-shape layer stays
// internal to the facade boundary. Tests mock this path.

export {
  fromProtoGrant,
  listGrants,
  createGrant,
  deleteGrant,
} from "../connect/grantConnect";
