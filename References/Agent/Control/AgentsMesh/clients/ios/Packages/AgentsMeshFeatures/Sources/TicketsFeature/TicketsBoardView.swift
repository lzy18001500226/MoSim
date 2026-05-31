import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Kanban board — horizontal-scrolling 5-column layout with colored
/// top stripe per column. Mirrors `design/mobile/pages/ios-tickets-board.pastel`.
public struct TicketsBoardView: View {
    let store: StoreOf<TicketsFeature>

    public var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(columns, id: \.0) { (key, label, color) in
                    KanbanColumn(
                        label: label,
                        accent: color,
                        tickets: bucket(for: key)
                    ) { slug in
                        store.send(.ticketTapped(slug))
                    }
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 12)
            .padding(.bottom, 100)
        }
    }

    private var columns: [(TicketStatusDto, String, Color)] {
        [
            (.backlog,    "Backlog",     AMColors.mutedForeground),
            (.todo,       "Todo",        Color(red: 0.345, green: 0.635, blue: 1.0)),
            (.inProgress, "In Progress", AMColors.warning),
            (.inReview,   "In Review",   AMColors.purple),
            (.done,       "Done",        AMColors.success),
        ]
    }

    private func bucket(for status: TicketStatusDto) -> [TicketDto] {
        store.tickets.filter { $0.status == status }
    }
}

private struct KanbanColumn: View {
    let label: String
    let accent: Color
    let tickets: [TicketDto]
    let onTap: (String) -> Void

    var body: some View {
        VStack(spacing: 0) {
            // Colored top stripe (3pt)
            Rectangle().fill(accent).frame(height: 3)
            HStack(spacing: 6) {
                Circle().fill(accent).frame(width: 8, height: 8)
                Text(label).font(.system(size: 13, weight: .semibold)).foregroundStyle(AMColors.foreground)
                Text("\(tickets.count)")
                    .font(.system(size: 11, design: .monospaced))
                    .foregroundStyle(AMColors.mutedForeground)
                Spacer()
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .accessibilityElement(children: .combine)
            .accessibilityIdentifier("board-column-\(label.replacingOccurrences(of: " ", with: "-").lowercased())")

            ScrollView(.vertical, showsIndicators: false) {
                VStack(spacing: 6) {
                    ForEach(tickets, id: \.slug) { t in
                        Button { onTap(t.slug) } label: { TicketCard(ticket: t) }
                            .buttonStyle(.plain)
                            .accessibilityIdentifier("ticket-card-\(t.slug)")
                    }
                }
                .padding(.horizontal, 8)
                .padding(.bottom, 12)
            }
        }
        .frame(width: 268)
        .frame(maxHeight: .infinity)
        .background(AMColors.groupedBg)
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }
}
