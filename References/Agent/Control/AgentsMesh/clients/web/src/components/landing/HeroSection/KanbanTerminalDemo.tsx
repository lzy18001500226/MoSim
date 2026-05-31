"use client";

import { useKanbanAnimation, getTerminalLineStyle } from "./useKanbanAnimation";
import type { KanbanTicket, TerminalPane } from "./types";

const COLUMN_LABELS = { backlog: "Backlog", in_progress: "In Progress", done: "Done" };
const COLUMN_KEYS = ["backlog", "in_progress", "done"] as const;

const AGENT_COLORS: Record<string, string> = {
  "Claude Code": "bg-orange-500/20 text-orange-400",
  "Codex CLI": "bg-blue-500/20 text-blue-400",
  "Aider": "bg-purple-500/20 text-purple-400",
  "Gemini CLI": "bg-green-500/20 text-green-400",
};

function TicketCard({ ticket }: { ticket: KanbanTicket }) {
  const showExecute = ticket.status === "backlog";

  return (
    <div className={`p-2 bg-background/60 rounded-lg border transition-all duration-500 ${
      ticket.executing ? "border-primary/60 shadow-md shadow-primary/20" : "border-border/60"
    }`}>
      <div className="flex items-center justify-between mb-1">
        <div className="text-xs font-medium text-foreground">{ticket.title}</div>
        {showExecute && (
          <span className={`text-[9px] px-1.5 py-0.5 rounded font-medium transition-all duration-300 ${
            ticket.executing
              ? "bg-primary text-primary-foreground scale-95"
              : "bg-primary/15 text-primary hover:bg-primary/25"
          }`}>
            {ticket.executing ? "Starting..." : "Execute"}
          </span>
        )}
      </div>
      <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${AGENT_COLORS[ticket.agent] ?? "bg-muted text-muted-foreground"}`}>
        {ticket.agent}
      </span>
    </div>
  );
}

function KanbanBoard({ tickets }: { tickets: KanbanTicket[] }) {
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-muted border-b border-border">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
          </div>
          <span className="text-xs font-semibold text-foreground ml-2">Kanban Board</span>
        </div>
        <span className="text-[10px] px-2 py-0.5 bg-primary/20 text-primary rounded">AgentsMesh</span>
      </div>

      {/* Columns */}
      <div className="grid grid-cols-3 gap-0 divide-x divide-border">
        {COLUMN_KEYS.map((col) => {
          const colTickets = tickets.filter((t) => t.status === col);
          return (
            <div key={col} className="p-2 min-h-[120px]">
              <div className="flex items-center gap-1.5 mb-2">
                <div className={`w-1.5 h-1.5 rounded-full ${
                  col === "backlog" ? "bg-muted-foreground" :
                  col === "in_progress" ? "bg-yellow-500 animate-pulse" :
                  "bg-green-500"
                }`} />
                <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                  {COLUMN_LABELS[col]}
                </span>
                <span className="text-[10px] text-muted-foreground/60 ml-auto">{colTickets.length}</span>
              </div>
              <div className="space-y-1.5">
                {colTickets.map((ticket) => (
                  <TicketCard key={ticket.id} ticket={ticket} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function TerminalSplitView({
  terminals,
  displayedLines,
  frameIndex,
}: {
  terminals: TerminalPane[];
  displayedLines: number;
  frameIndex: number;
}) {
  if (terminals.length === 0) return null;

  return (
    <div className={`grid ${terminals.length > 1 ? "grid-cols-2" : "grid-cols-1"} gap-2`}>
      {terminals.map((terminal) => (
        <div
          key={`${frameIndex}-${terminal.id}`}
          className="bg-card rounded-lg border border-border overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-500"
        >
          <div className="flex items-center justify-between px-3 py-1.5 bg-muted border-b border-border">
            <div className="flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full ${terminal.active ? "bg-green-500 animate-pulse" : "bg-muted-foreground"}`} />
              <span className="text-[10px] font-mono font-semibold text-foreground">{terminal.agent}</span>
            </div>
            <span className="text-[10px] text-muted-foreground font-mono">{terminal.ticketId}-dev</span>
          </div>
          <div className="p-2 font-mono text-[11px] leading-relaxed h-[100px] overflow-hidden bg-background/30">
            {terminal.lines.slice(0, displayedLines).map((line, i) => (
              <div key={i} className={getTerminalLineStyle(line.type)}>
                {line.type === "command" ? line.text : `  ${line.text}`}
              </div>
            ))}
            {terminal.active && displayedLines < terminal.lines.length && (
              <span className="animate-pulse text-primary">▋</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export function KanbanTerminalDemo() {
  const { currentFrame, frameIndex, displayedLines } = useKanbanAnimation();

  return (
    <div className="space-y-3">
      <KanbanBoard tickets={currentFrame.tickets} />
      {currentFrame.showTerminals && (
        <TerminalSplitView
          terminals={currentFrame.terminals}
          displayedLines={displayedLines}
          frameIndex={frameIndex}
        />
      )}
    </div>
  );
}

export default KanbanTerminalDemo;
