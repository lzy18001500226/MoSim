import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Flat list view — mirrors web TicketListView. Each row card-like:
/// slug + status pill, title (2 lines), footer with priority/due/avatar.
public struct TicketsListView: View {
    let store: StoreOf<TicketsFeature>

    public var body: some View {
        ScrollView {
            LazyVStack(spacing: 0) {
                ForEach(store.tickets, id: \.slug) { ticket in
                    Button { store.send(.ticketTapped(ticket.slug)) } label: {
                        ListRow(ticket: ticket)
                    }
                    .buttonStyle(.plain)
                    Divider().background(AMColors.separator).padding(.leading, 16)
                }
            }
            .padding(.bottom, 100)
        }
    }
}

private struct ListRow: View {
    let ticket: TicketDto
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                Text(ticket.slug)
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                    .foregroundStyle(AMColors.secondaryText)
                Text(statusLabel)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(statusColor)
            }
            Text(ticket.title)
                .font(.system(size: 15))
                .foregroundStyle(AMColors.foreground)
                .lineLimit(2)
            HStack {
                Text(priority).font(.system(size: 12)).foregroundStyle(AMColors.mutedForeground)
                Spacer()
                AMAvatar("D", size: .xs, bg: AMColors.primary)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(AMColors.card)
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
    private var priority: String {
        switch ticket.priority {
        case .urgent, .high: return "▲ High"
        case .medium: return "● Med"
        case .low: return "▼ Low"
        default: return "—"
        }
    }
}
