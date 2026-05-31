import ComposableArchitecture
import SwiftUI
import WorkspaceFeature
import TerminalFeature
import ChannelsFeature
import TicketsFeature
import BlocksFeature
import MoreFeature
import OrgDrawerFeature
import DesignSystem

/// Dashboard = 5-tab IA (Pods · Channels · Tickets · Blocks · More)
/// + optional terminal cover + optional org drawer overlay. Each tab
/// owns a child feature scoped via Reducer composition.
@Reducer
public struct DashboardFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable {
        public var selectedTab: AMTab = .pods
        public var workspace = PodListFeature.State()
        public var channels = ChannelsListFeature.State()
        public var tickets = TicketsFeature.State()
        public var blocks = BlocksFeature.State()
        @Presents public var terminal: TerminalFeature.State?
        @Presents public var channelDetail: ChannelDetailFeature.State?
        @Presents public var ticketDetail: TicketDetailFeature.State?
        @Presents public var blockDetail: BlockDetailFeature.State?
        @Presents public var drawer: OrgDrawerFeature.State?
        public var showingMoreSheet: Bool = false

        public init() {}
    }

    public enum Action: Sendable {
        case tabSelected(AMTab)
        case setMoreSheetVisible(Bool)
        case workspace(PodListFeature.Action)
        case channels(ChannelsListFeature.Action)
        case tickets(TicketsFeature.Action)
        case blocks(BlocksFeature.Action)
        case terminal(PresentationAction<TerminalFeature.Action>)
        case channelDetail(PresentationAction<ChannelDetailFeature.Action>)
        case ticketDetail(PresentationAction<TicketDetailFeature.Action>)
        case blockDetail(PresentationAction<BlockDetailFeature.Action>)
        case drawer(PresentationAction<OrgDrawerFeature.Action>)
        case terminalDismissed
        case channelDetailDismissed
        case ticketDetailDismissed
        case blockDetailDismissed
        case drawerOpenRequested
        case drawerDismissed
        case delegate(Delegate)

        public enum Delegate: Equatable, Sendable {
            case didSignOut
        }
    }

    public var body: some ReducerOf<Self> {
        Scope(state: \.workspace, action: \.workspace) { PodListFeature() }
        Scope(state: \.channels, action: \.channels) { ChannelsListFeature() }
        Scope(state: \.tickets, action: \.tickets) { TicketsFeature() }
        Scope(state: \.blocks, action: \.blocks) { BlocksFeature() }
        Reduce { state, action in
            switch action {
            case .tabSelected(.more):
                // More 是 modal 不是页面，selectedTab 不切换以保持底层视图。
                state.showingMoreSheet = true
                return .none
            case .tabSelected(let tab):
                state.selectedTab = tab
                return .none

            case .setMoreSheetVisible(let visible):
                state.showingMoreSheet = visible
                return .none

            case .workspace(.delegate(.openTerminal(let key))):
                state.terminal = TerminalFeature.State(podKey: key)
                return .none
            case .workspace(.delegate(.didLogout)):
                return .send(.delegate(.didSignOut))
            case .workspace(.delegate(.requestDrawer)),
                 .channels(.delegate(.requestDrawer)),
                 .tickets(.delegate(.requestDrawer)),
                 .blocks(.delegate(.requestDrawer)):
                state.drawer = OrgDrawerFeature.State()
                return .none
            case .channels(.delegate(.requestCompose)),
                 .tickets(.delegate(.requestCompose)),
                 .blocks(.delegate(.requestCompose)):
                // TODO: per-tab compose sheets (Channels, Tickets, Blocks)
                // are still placeholders. Pods now owns its sheet.
                return .none

            case .channels(.delegate(.openChannel(let id))):
                state.channelDetail = ChannelDetailFeature.State(channelId: id)
                return .none

            case .tickets(.delegate(.openTicket(let slug))):
                state.ticketDetail = TicketDetailFeature.State(slug: slug)
                return .none

            case .blocks(.delegate(.openBlock(let id, let wsId))):
                state.blockDetail = BlockDetailFeature.State(blockId: id, workspaceId: wsId)
                return .none

            case .drawer(.presented(.delegate(.dismiss))):
                state.drawer = nil
                return .none
            case .drawer(.presented(.delegate(.didSignOut))):
                state.drawer = nil
                return .send(.delegate(.didSignOut))

            case .terminalDismissed:
                state.terminal = nil; return .none
            case .channelDetailDismissed:
                state.channelDetail = nil; return .none
            case .ticketDetailDismissed:
                state.ticketDetail = nil; return .none
            case .blockDetailDismissed:
                state.blockDetail = nil; return .none

            case .drawerOpenRequested:
                state.drawer = OrgDrawerFeature.State()
                return .none
            case .drawerDismissed:
                state.drawer = nil
                return .none

            case .terminal(.presented(.delegate(.dismissRequested))):
                state.terminal = nil
                return .none

            case .workspace, .channels, .tickets, .blocks, .terminal,
                 .channelDetail, .ticketDetail, .blockDetail, .drawer,
                 .delegate:
                return .none
            }
        }
        .ifLet(\.$terminal, action: \.terminal) { TerminalFeature() }
        .ifLet(\.$channelDetail, action: \.channelDetail) { ChannelDetailFeature() }
        .ifLet(\.$ticketDetail, action: \.ticketDetail) { TicketDetailFeature() }
        .ifLet(\.$blockDetail, action: \.blockDetail) { BlockDetailFeature() }
        .ifLet(\.$drawer, action: \.drawer) { OrgDrawerFeature() }
    }
}
