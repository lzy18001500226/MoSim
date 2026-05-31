import { invoke } from "./invoke";
import type { ITicketService } from "@agentsmesh/service-interface";

export class ElectronTicketService implements ITicketService {
  private _ticketsCache = "[]";
  private _labelsCache = "[]";
  private _boardColumnsCache = "[]";
  private _currentTicketCache: string | null = null;
  private _ticketPodsCache: Record<string, string> = {};

  tickets_json(): string { return this._ticketsCache; }
  labels_json(): string { return this._labelsCache; }
  board_columns_json(): string { return this._boardColumnsCache; }
  current_ticket_json(): unknown { return this._currentTicketCache; }

  get_ticket_by_slug_json(slug: string): unknown {
    const tickets = JSON.parse(this._ticketsCache) as { slug: string }[];
    const t = tickets.find(x => x.slug === slug);
    return t ? JSON.stringify(t) : null;
  }

  filter_tickets_json(_search: string, _statusesJson: string, _prioritiesJson: string, _repoIdsJson: string): string {
    return this._ticketsCache;
  }

  set_tickets(json: string): void { this._ticketsCache = json; }
  set_labels(json: string): void { this._labelsCache = json; }
  set_board_columns(json: string): void { this._boardColumnsCache = json; }
  set_current_ticket(json: string): void { this._currentTicketCache = json || null; }

  add_ticket(json: string): void {
    const tickets = JSON.parse(this._ticketsCache) as unknown[];
    tickets.push(JSON.parse(json));
    this._ticketsCache = JSON.stringify(tickets);
  }

  add_label(json: string): void {
    const labels = JSON.parse(this._labelsCache) as unknown[];
    labels.push(JSON.parse(json));
    this._labelsCache = JSON.stringify(labels);
  }

  remove_ticket(slug: string): void {
    const tickets = JSON.parse(this._ticketsCache) as { slug: string }[];
    this._ticketsCache = JSON.stringify(tickets.filter(x => x.slug !== slug));
  }

  remove_label(id: number): void {
    const labels = JSON.parse(this._labelsCache) as { id: number }[];
    this._labelsCache = JSON.stringify(labels.filter(x => x.id !== id));
  }

  update_ticket_local(slug: string, json: string): void {
    const tickets = JSON.parse(this._ticketsCache) as { slug: string }[];
    const idx = tickets.findIndex(x => x.slug === slug);
    if (idx >= 0) tickets[idx] = { ...tickets[idx], ...JSON.parse(json) };
    this._ticketsCache = JSON.stringify(tickets);
  }

  update_ticket_status_local(slug: string, status: string): void {
    const tickets = JSON.parse(this._ticketsCache) as { slug: string; status?: string }[];
    const t = tickets.find(x => x.slug === slug);
    if (t) t.status = status;
    this._ticketsCache = JSON.stringify(tickets);
  }

  append_column_tickets(status: string, json: string): void {
    const cols = JSON.parse(this._boardColumnsCache) as { status: string; tickets: unknown[] }[];
    const col = cols.find(c => c.status === status);
    if (col) col.tickets.push(...(JSON.parse(json) as unknown[]));
    this._boardColumnsCache = JSON.stringify(cols);
  }

  async get_ticket_pods(slug: string, activeOnly?: boolean | null): Promise<string> {
    const result = await invoke<string>("ticketGetTicketPods", slug, activeOnly);
    this._ticketPodsCache[slug] = result;
    return result;
  }

  ticket_pods_json(slug: string): string {
    const raw = this._ticketPodsCache[slug];
    if (!raw) return "[]";
    try {
      const parsed = JSON.parse(raw) as { pods?: unknown[] };
      return JSON.stringify(parsed.pods ?? []);
    } catch {
      return "[]";
    }
  }

  // ─── Connect-RPC bridges (Uint8Array round-trip) ──────────────────

  async list_tickets_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketListTicketsConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async get_ticket_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketGetTicketConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async create_ticket_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketCreateTicketConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async update_ticket_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketUpdateTicketConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async delete_ticket_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketDeleteTicketConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async update_ticket_status_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketUpdateTicketStatusConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async get_active_tickets_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketGetActiveTicketsConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async get_board_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketGetBoardConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async get_sub_tickets_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketGetSubTicketsConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async add_assignee_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketAddAssigneeConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async remove_assignee_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketRemoveAssigneeConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async list_labels_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketListLabelsConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async create_label_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketCreateLabelConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async update_label_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketUpdateLabelConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async delete_label_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketDeleteLabelConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async add_label_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketAddLabelConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }

  async remove_label_connect(request: Uint8Array): Promise<Uint8Array> {
    const bytes = await invoke<number[] | Uint8Array>("ticketRemoveLabelConnect", Array.from(request));
    return bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  }
}
