import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Tickets root view — segment toggle in nav top-left + List or Board body.
public struct TicketsView: View {
    @Perception.Bindable var store: StoreOf<TicketsFeature>

    public init(store: StoreOf<TicketsFeature>) { self.store = store }

    public var body: some View {
        ZStack {
            AMColors.card.ignoresSafeArea()
            content
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                AMSegmentedControl(
                    [(label: "List", tag: TicketsFeature.Mode.list),
                     (label: "Board", tag: TicketsFeature.Mode.board)],
                    selection: $store.mode.sending(\.modeChanged),
                    compact: true
                )
                .frame(width: 140)
            }
            ToolbarItem(placement: .topBarTrailing) {
                HStack(spacing: 0) {
                    Button { store.send(.composeTapped) } label: {
                        Image(systemName: "magnifyingglass").font(.system(size: 17)).foregroundStyle(AMColors.primary)
                    }
                    Button { store.send(.composeTapped) } label: {
                        Image(systemName: "plus").font(.system(size: 17, weight: .medium)).foregroundStyle(AMColors.primary)
                    }
                }
            }
        }
        .onAppear { store.send(.onAppear) }
    }

    @ViewBuilder
    private var content: some View {
        if store.isLoading && store.tickets.isEmpty {
            ProgressView().frame(maxHeight: .infinity)
        } else {
            switch store.mode {
            case .list: TicketsListView(store: store)
            case .board: TicketsBoardView(store: store)
            }
        }
    }
}
