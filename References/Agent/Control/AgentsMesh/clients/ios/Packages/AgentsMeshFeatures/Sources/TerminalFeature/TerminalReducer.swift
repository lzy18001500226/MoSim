import ComposableArchitecture
import Foundation
import AgentsMeshCore
import CoreClient

@Reducer
public struct TerminalFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable, Identifiable {
        public let id = UUID()
        public var podKey: String
        public var connection: PodConnectionInfoDto?
        public var cols: UInt16 = 80
        public var rows: UInt16 = 24
        public var isConnecting: Bool = true
        public var errorMessage: String?
        public var isAttached: Bool = false

        public init(podKey: String) { self.podKey = podKey }
    }

    public enum Action: Sendable {
        case onAppear
        case connectionFetched(PodConnectionInfoDto)
        case connectionFailed(String)
        case wsAttached
        case wsDetached(reason: String?)
        case inputEntered(Data)
        case resized(cols: UInt16, rows: UInt16)
        case delegate(Delegate)

        public enum Delegate: Equatable, Sendable {
            case dismissRequested
        }
    }

    @Dependency(\.coreClient) var core
    @Dependency(\.relayWebSocket) var relay

    public var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .onAppear:
                let key = state.podKey
                return .run { send in
                    do {
                        let info = try await core.getPodRelayConnection(key)
                        await send(.connectionFetched(info))
                    } catch {
                        await send(.connectionFailed(error.localizedDescription))
                    }
                }

            case .connectionFetched(let info):
                state.connection = info
                let podKey = state.podKey
                let cols = state.cols
                let rows = state.rows
                return .run { send in
                    do {
                        try await relay.connect(info, podKey, cols, rows)
                        await send(.wsAttached)
                    } catch {
                        await send(.wsDetached(reason: error.localizedDescription))
                    }
                }

            case .connectionFailed(let message):
                state.isConnecting = false
                state.errorMessage = message
                return .none

            case .wsAttached:
                state.isConnecting = false
                state.isAttached = true
                return .none

            case .wsDetached(let reason):
                state.isAttached = false
                state.errorMessage = reason
                return .none

            case .inputEntered(let data):
                return .run { _ in
                    try? await relay.sendInput(data)
                }

            case .resized(let cols, let rows):
                state.cols = cols
                state.rows = rows
                return .run { _ in
                    try? await relay.sendResize(cols, rows)
                }

            case .delegate:
                return .none
            }
        }
    }
}
