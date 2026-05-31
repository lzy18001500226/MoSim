import ComposableArchitecture
import Foundation
import AgentsMeshCore
import CoreClient

@Reducer
public struct ChannelsListFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable {
        public var channels: [ChannelDto] = []
        public var unreadCounts: [Int64: Int64] = [:]
        public var lastMessageByChannel: [Int64: ChannelMessageDto] = [:]
        public var isLoading: Bool = false
        public var errorMessage: String?
        public var selectedChannelId: Int64?

        public init() {}
    }

    public enum Action: Sendable {
        case onAppear
        case refreshRequested
        case channelsLoaded([ChannelDto])
        case unreadLoaded([Int64: Int64])
        case lastMessageLoaded(channelId: Int64, message: ChannelMessageDto)
        case loadFailed(String)
        case channelTapped(Int64)
        case avatarTapped
        case composeTapped
        case delegate(Delegate)

        public enum Delegate: Equatable, Sendable {
            case openChannel(id: Int64)
            case requestDrawer
            case requestCompose
        }
    }

    @Dependency(\.coreClient) var core

    public var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .onAppear, .refreshRequested:
                state.isLoading = true
                state.errorMessage = nil
                return .run { send in
                    do {
                        async let chans = core.listChannels(false)
                        async let unread = core.getChannelUnreadCounts()
                        let (c, u) = try await (chans, unread)
                        await send(.channelsLoaded(c.channels))
                        var dict: [Int64: Int64] = [:]
                        for (channelIdStr, count) in u.unread {
                            if let id = Int64(channelIdStr) {
                                dict[id] = Int64(count)
                            }
                        }
                        await send(.unreadLoaded(dict))
                        await withTaskGroup(of: (Int64, ChannelMessageDto?).self) { group in
                            for ch in c.channels {
                                group.addTask {
                                    let resp = try? await core.getChannelMessages(ch.id, 1, nil)
                                    return (ch.id, resp?.messages.last)
                                }
                            }
                            for await (id, msg) in group {
                                if let m = msg {
                                    await send(.lastMessageLoaded(channelId: id, message: m))
                                }
                            }
                        }
                    } catch {
                        await send(.loadFailed(error.localizedDescription))
                    }
                }

            case .channelsLoaded(let chans):
                state.isLoading = false
                state.channels = chans
                return .none

            case .unreadLoaded(let counts):
                state.unreadCounts = counts
                return .none

            case .lastMessageLoaded(let channelId, let message):
                state.lastMessageByChannel[channelId] = message
                return .none

            case .loadFailed(let msg):
                state.isLoading = false
                state.errorMessage = msg
                return .none

            case .channelTapped(let id):
                state.selectedChannelId = id
                return .send(.delegate(.openChannel(id: id)))

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
