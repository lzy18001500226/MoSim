import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Ticket card — mirrors web TicketCard. Shared between List and Board.
public struct TicketCard: View {
    let ticket: TicketDto
    let showStatus: Bool

    public init(ticket: TicketDto, showStatus: Bool = false) {
        self.ticket = ticket
        self.showStatus = showStatus
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(ticket.slug)
                    .font(.system(size: 11, weight: .medium, design: .monospaced))
                    .foregroundStyle(AMColors.secondaryText)
                Spacer()
                if showStatus {
                    Text(statusLabel)
                        .font(.system(size: 11, weight: .medium))
                        .foregroundStyle(statusColor)
                }
            }
            Text(ticket.title)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(AMColors.foreground)
                .lineLimit(2)
            Divider().background(AMColors.border)
            HStack {
                Text(priorityLabel)
                    .font(.system(size: 11))
                    .foregroundStyle(AMColors.mutedForeground)
                Spacer()
                AMAvatar("D", size: .xs, bg: AMColors.primary)
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
        .background(AMColors.card)
        .overlay(
            RoundedRectangle(cornerRadius: 6).stroke(AMColors.border, lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 6))
    }

    private var statusLabel: String {
        switch ticket.status {
        case .backlog: return "Backlog"
        case .todo: return "Todo"
        case .inProgress: return "In Progress"
        case .inReview: return "In Review"
        case .done: return "Done"
        default: return "—"
        }
    }
    private var statusColor: Color {
        switch ticket.status {
        case .backlog: return AMColors.secondaryText
        case .todo: return AMColors.primaryStrong
        case .inProgress: return AMColors.warningText
        case .inReview: return AMColors.purple
        case .done: return AMColors.successText
        default: return AMColors.mutedForeground
        }
    }
    private var priorityLabel: String {
        switch ticket.priority {
        case .urgent, .high: return "▲ High"
        case .medium: return "● Med"
        case .low: return "▼ Low"
        default: return "—"
        }
    }
}
