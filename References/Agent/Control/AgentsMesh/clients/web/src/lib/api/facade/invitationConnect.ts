// Facade re-export of the invitation Connect-RPC adapter. Business code
// imports from here (or from the `@/lib/api` barrel) so the wire-shape
// layer stays internal to the facade boundary. Tests mock this path.

export {
  listInvitations,
  createInvitation,
  revokeInvitation,
  resendInvitation,
  acceptInvitation,
  listPendingInvitations,
  getInvitationByToken,
  type Invitation,
  type InvitationInfo,
  type PendingInvitation,
} from "../connect/invitationConnect";
