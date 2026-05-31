// Facade re-export of the ticket Connect-RPC adapter. Business code imports
// from here (or from the `@/lib/api` barrel) so the wire-shape layer stays
// internal to the facade boundary. Tests mock this path.
//
// Wire layer split: ticketConnect (CRUD + board + assignees) + ticketLabel
// (label CRUD + label-ticket associations).

export {
  fromProtoTicket,
  fromProtoLabel,
  listTickets,
  getTicket,
  createTicket,
  updateTicket,
  deleteTicket,
  updateTicketStatus,
  getActiveTickets,
  getBoard,
  getSubTickets,
  addAssignee,
  removeAssignee,
  type CreateTicketInput,
  type UpdateTicketInput,
} from "../connect/ticketConnect";

export {
  listLabels,
  createLabel,
  updateLabel,
  deleteLabel,
  addLabel,
  removeLabel,
} from "../connect/ticketLabelConnect";
