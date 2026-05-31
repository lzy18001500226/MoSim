import ComposableArchitecture
import Foundation
import AgentsMeshCore
import CoreClient

/// Pages tree node — recursive structure for the BlocksSidebar pattern.
public struct PageNode: Equatable, Identifiable, Sendable {
    public let id: String
    public let title: String
    public let icon: String?
    public let children: [PageNode]

    public init(id: String, title: String, icon: String?, children: [PageNode]) {
        self.id = id
        self.title = title
        self.icon = icon
        self.children = children
    }
}

@Reducer
public struct BlocksFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable {
        public var workspace: WorkspaceDto?
        public var rootChildren: ChildrenResultDto?
        public var tree: [PageNode] = []
        public var isLoading: Bool = false
        public var errorMessage: String?
        public var selectedBlockId: String?

        public init() {}
    }

    public enum Action: Sendable {
        case onAppear
        case workspaceLoaded(WorkspaceDto)
        case subtreeLoaded(ChildrenResultDto)
        case loadFailed(String)
        case pageTapped(String)
        case avatarTapped
        case composeTapped
        case delegate(Delegate)

        public enum Delegate: Equatable, Sendable {
            case openBlock(id: String, workspaceId: String)
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
                        let ws = try await core.blocks.ensureDefaultWorkspace()
                        await send(.workspaceLoaded(ws))
                        guard let rootId = ws.rootBlockId else { return }
                        let subtree = try await core.blocks.getSubtree(ws.id, rootId, 4)
                        await send(.subtreeLoaded(subtree))
                    } catch {
                        await send(.loadFailed(error.localizedDescription))
                    }
                }
            case .workspaceLoaded(let ws):
                state.workspace = ws
                return .none
            case .subtreeLoaded(let result):
                state.isLoading = false
                state.rootChildren = result
                state.tree = buildTree(from: result, rootId: state.workspace?.rootBlockId ?? "")
                return .none
            case .loadFailed(let msg):
                state.isLoading = false
                state.errorMessage = msg
                return .none
            case .pageTapped(let id):
                state.selectedBlockId = id
                guard let wsId = state.workspace?.id else { return .none }
                return .send(.delegate(.openBlock(id: id, workspaceId: wsId)))
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

/// rel 取值来自 backend block_refs.rel：父子在 schema 中是 "nest"。
func buildTree(from result: ChildrenResultDto, rootId: String) -> [PageNode] {
    let blocksById = Dictionary(uniqueKeysWithValues: result.blocks.map { ($0.id, $0) })
    var childrenByParent: [String: [String]] = [:]
    for ref in result.refs where ref.rel == "nest" {
        childrenByParent[ref.fromId, default: []].append(ref.toId)
    }
    func node(_ id: String) -> PageNode? {
        guard let block = blocksById[id], block.blockType == "page" else { return nil }
        let title = (block.text?.isEmpty == false ? block.text! : "Untitled")
        let children = (childrenByParent[id] ?? []).compactMap(node(_:))
        return PageNode(id: id, title: title, icon: nil, children: children)
    }
    return (childrenByParent[rootId] ?? []).compactMap(node(_:))
}
