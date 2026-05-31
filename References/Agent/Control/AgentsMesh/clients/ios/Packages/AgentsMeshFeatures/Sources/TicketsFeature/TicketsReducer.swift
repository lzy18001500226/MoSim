import ComposableArchitecture
import Foundation
import AgentsMeshCore
import CoreClient

/// Root tickets feature — owns selection between List and Board scope and
/// loads tickets once for both views.
@Reducer
public struct TicketsFeature {
    public enum Mode: Hashable, Sendable { case list, board }

    public init() {}

    @ObservableState
    public struct State: Equatable {
        public var mode: Mode = .board
        public var tickets: [TicketDto] = []
        public var board: BoardResponseDto?
        public var isLoading: Bool = false
        public var errorMessage: String?
        public var selectedSlug: String?

        public init() {}
    }

    public enum Action: Sendable {
        case onAppear
        case modeChanged(Mode)
        case ticketsLoaded([TicketDto], BoardResponseDto)
        case loadFailed(String)
        case ticketTapped(String)
        case statusUpdated(slug: String, status: TicketStatusDto)
        case avatarTapped
        case composeTapped
        case delegate(Delegate)

        public enum Delegate: Equatable, Sendable {
            case openTicket(slug: String)
            case requestDrawer
            case requestCompose
        }
    }

    @Dependency(\.coreClient) var core

    public var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .onAppear:
                state.isLoading = true
                return .run { send in
                    do {
                        async let list = core.listTickets(nil, 100, 0)
                        async let board = core.getTicketBoard(nil)
                        let (l, b) = try await (list, board)
                        await send(.ticketsLoaded(l.tickets, b))
                    } catch {
                        await send(.loadFailed(error.localizedDescription))
                    }
                }

            case .modeChanged(let m):
                state.mode = m
                return .none

            case .ticketsLoaded(let tickets, let board):
                state.isLoading = false
                state.tickets = tickets
                state.board = board
                return .none

            case .loadFailed(let msg):
                state.isLoading = false
                state.errorMessage = msg
                return .none

            case .ticketTapped(let slug):
                state.selectedSlug = slug
                return .send(.delegate(.openTicket(slug: slug)))

            case .statusUpdated(let slug, let status):
                let s = slug
                let st = status
                return .run { send in
                    _ = try? await core.updateTicketStatus(s, st)
                    await send(.onAppear)
                }

            case .avatarTapped:
                return .send(.delegate(.requestDrawer))

            case .composeTapped:
                return .send(.delegate(.requestCompose))

            case .delegate:
                return .none
            }
        }
    }
}
