import Foundation
import AgentsMeshCore

/// Blocks slice of `CoreClient`. Mirrors the
/// `BlockstoreService` interface that web's
/// `clients/web/src/lib/api/blockstoreApi.ts` calls — every iOS path
/// that talks to the Rust blockstore (BlocksReducer + the embedded
/// WebView's RPC router) goes through this one slice.
///
/// Binary-wire `*Connect` entry points carry the proto bytes the web
/// `blockstoreConnect` adapter encodes; typed accessors (`Workspace`/
/// `Block`/`ChildrenResult`) exist for native TCA reducers.
public struct BlocksCoreClient: Sendable {
    // ── Connect-RPC (binary wire) — webview RPC bridge forwards these
    public var applyOpsConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var listWorkspacesConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var ensureDefaultWorkspaceConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var createWorkspaceConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var deleteWorkspaceConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var getBlockConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var listChildrenConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var listBacklinksConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var getSubtreeConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var streamOpsConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var listTypeDefsConnect: @Sendable (_ bytes: Data) async throws -> Data
    public var semanticSearchConnect: @Sendable (_ bytes: Data) async throws -> Data

    // ── Native-only mutators (apply_remote_op fires from WS, no wire)
    public var applyRemoteOp: @Sendable (_ opJson: String) throws -> Void
    public var setLastOpId: @Sendable (_ wsId: String, _ id: Int64) -> Void

    // ── Async readers (typed) — used by native TCA reducers
    public var ensureDefaultWorkspace: @Sendable () async throws -> WorkspaceDto
    public var listWorkspaces: @Sendable () async throws -> [WorkspaceDto]
    public var getSubtree: @Sendable (_ wsId: String, _ rootId: String, _ depth: UInt32) async throws -> ChildrenResultDto
    public var getBlock: @Sendable (_ id: String) async throws -> BlockDto
    public var semanticSearch: @Sendable (_ wsId: String, _ req: SemanticSearchRequestDto) async throws -> [SearchHitDto]

    // ── Sync flat-map readers — backed by in-process Rust SSOT
    public var workspacesJson: @Sendable () -> String
    public var blocksJson: @Sendable () -> String
    public var refsJson: @Sendable () -> String
    public var nestChildrenJson: @Sendable () -> String
    public var backlinksJson: @Sendable () -> String
    public var lastOpIdsJson: @Sendable () -> String
    public var lastOpId: @Sendable (_ wsId: String) -> Int64

    // ── Sync per-id readers
    public var getBlockJson: @Sendable (_ id: String) -> String?
    public var listChildrenJson: @Sendable (_ parentId: String) -> String
    public var listBacklinksJson: @Sendable (_ targetId: String) -> String
    public var typeDefsJson: @Sendable (_ wsId: String) -> String

    // ── Bulk state-cache mutators (web pushes server results into Rust cache)
    public var replaceWorkspacesJson: @Sendable (_ listJson: String) throws -> Void
    public var upsertWorkspaceJson: @Sendable (_ wsJson: String) throws -> Void
    public var upsertBlocksJson: @Sendable (_ blocksJson: String) throws -> Void
    public var upsertRefsJson: @Sendable (_ refsJson: String) throws -> Void

    public static let live: BlocksCoreClient = liveBlocksCoreClient()
    public static let unimplemented: BlocksCoreClient = unimplementedBlocksCoreClient()
}
