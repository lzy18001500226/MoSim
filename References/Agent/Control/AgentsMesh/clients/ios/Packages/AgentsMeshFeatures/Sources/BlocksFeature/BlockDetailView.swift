import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import CoreClient
import DesignSystem

@Reducer
public struct BlockDetailFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable {
        public let blockId: String
        public let workspaceId: String

        public init(blockId: String, workspaceId: String) {
            self.blockId = blockId
            self.workspaceId = workspaceId
        }
    }

    public enum Action: Sendable {
        case onAppear
    }

    public var body: some ReducerOf<Self> {
        Reduce { _, _ in .none }
    }
}

public struct BlockDetailView: View {
    let store: StoreOf<BlockDetailFeature>
    @Dependency(\.coreClient) private var core

    public init(store: StoreOf<BlockDetailFeature>) { self.store = store }

    public var body: some View {
        BlockDetailWebView(
            workspaceId: store.workspaceId,
            blockId: store.blockId,
            route: BlockstoreRpcRoute(core: core)
        )
        .accessibilityIdentifier("block-detail-webview")
        .navigationBarTitleDisplayMode(.inline)
        .ignoresSafeArea(.container, edges: .bottom)
    }
}
