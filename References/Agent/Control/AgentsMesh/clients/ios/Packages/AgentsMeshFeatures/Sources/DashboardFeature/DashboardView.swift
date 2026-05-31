import ComposableArchitecture
import SwiftUI
import BlocksFeature
import ChannelsFeature
import DesignSystem
import MoreFeature
import OrgDrawerFeature
import TerminalFeature
import TicketsFeature
import WorkspaceFeature

/// 5-tab dashboard. Each tab owns its own NavigationStack so push
/// transitions stay scoped to the active tab. iOS 26 renders the
/// floating capsule tab bar automatically.
public struct DashboardView: View {
    @Perception.Bindable var store: StoreOf<DashboardFeature>

    public init(store: StoreOf<DashboardFeature>) { self.store = store }

    public var body: some View {
        ZStack(alignment: .leading) {
            TabView(selection: $store.selectedTab.sending(\.tabSelected)) {
                podsTab
                channelsTab
                ticketsTab
                blocksTab
                moreTab
            }
            .tint(AMColors.primary)
            .fullScreenCover(
                item: $store.scope(state: \.terminal, action: \.terminal)
            ) { terminalStore in
                NavigationStack {
                    TerminalView(store: terminalStore)
                        .toolbar {
                            ToolbarItem(placement: .topBarLeading) {
                                Button("Close") { store.send(.terminalDismissed) }
                            }
                        }
                }
            }
            .sheet(isPresented: $store.showingMoreSheet.sending(\.setMoreSheetVisible)) {
                NavigationStack { MoreView() }
                    .presentationDetents([.medium, .large])
                    .presentationDragIndicator(.visible)
            }

            if let drawerStore = store.scope(state: \.drawer, action: \.drawer.presented) {
                Color.black.opacity(0.5)
                    .ignoresSafeArea()
                    .contentShape(Rectangle())
                    .onTapGesture { store.send(.drawerDismissed) }
                    .transition(.opacity)
                    .zIndex(1)

                OrgDrawerView(
                    store: drawerStore,
                    onClose: { store.send(.drawerDismissed) }
                )
                .frame(width: 340)
                .frame(maxHeight: .infinity)
                .background(AMColors.card)
                .ignoresSafeArea(.container, edges: .vertical)
                .transition(.move(edge: .leading))
                .zIndex(2)
            }
        }
        .animation(.easeInOut(duration: 0.28), value: store.drawer != nil)
    }

    private var podsTab: some View {
        NavigationStack {
            PodListView(store: store.scope(state: \.workspace, action: \.workspace))
        }
        .tabItem { Label(AMTab.pods.label, systemImage: AMTab.pods.symbol) }
        .tag(AMTab.pods)
    }

    private var channelsTab: some View {
        NavigationStack {
            ChannelsListView(store: store.scope(state: \.channels, action: \.channels))
                .navigationDestination(
                    item: $store.scope(state: \.channelDetail, action: \.channelDetail)
                ) { detailStore in
                    ChannelDetailView(store: detailStore)
                }
        }
        .tabItem { Label(AMTab.channels.label, systemImage: AMTab.channels.symbol) }
        .tag(AMTab.channels)
    }

    private var ticketsTab: some View {
        NavigationStack {
            TicketsView(store: store.scope(state: \.tickets, action: \.tickets))
                .navigationDestination(
                    item: $store.scope(state: \.ticketDetail, action: \.ticketDetail)
                ) { detailStore in
                    TicketDetailView(store: detailStore)
                }
        }
        .tabItem { Label(AMTab.tickets.label, systemImage: AMTab.tickets.symbol) }
        .tag(AMTab.tickets)
    }

    private var blocksTab: some View {
        NavigationStack {
            BlocksTreeView(store: store.scope(state: \.blocks, action: \.blocks))
                .navigationDestination(
                    item: $store.scope(state: \.blockDetail, action: \.blockDetail)
                ) { detailStore in
                    BlockDetailView(store: detailStore)
                }
        }
        .tabItem { Label(AMTab.blocks.label, systemImage: AMTab.blocks.symbol) }
        .tag(AMTab.blocks)
    }

    private var moreTab: some View {
        // More 通过 sheet 呈现；此 tab 仅作为 tabbar 入口。
        Color.clear
            .tabItem { Label(AMTab.more.label, systemImage: AMTab.more.symbol) }
            .tag(AMTab.more)
    }
}
