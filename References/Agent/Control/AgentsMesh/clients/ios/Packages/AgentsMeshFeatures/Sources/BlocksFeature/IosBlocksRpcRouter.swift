import Foundation
import AgentsMeshCore
import CoreClient

/// JSON-RPC router for the embedded block-detail WebView.
///
/// Bridges web's `RpcBlockstoreService` (clients/web/src/lib/ios-bridge)
/// over `webkit.messageHandlers.amBridge`. Every wire call carries
/// prost-encoded request bytes (base64) and returns prost-encoded
/// response bytes — the same binary shape `blockstoreConnect.ts` uses
/// when running outside embed mode against the WASM Connect surface.
///
/// State-cache mutators / readers stay on JSON strings since the
/// in-process Rust SSOT (`AgentsMeshCore.blockstore`) keeps the
/// view-type cache.
public protocol IosRpcRoute {
    func dispatch(method: String, args: [String: Any]) async throws -> Any?
}

public struct BlockstoreRpcRoute: IosRpcRoute {
    let core: CoreClient
    public init(core: CoreClient) { self.core = core }

    public func dispatch(method: String, args: [String: Any]) async throws -> Any? {
        // ── Binary wire (Connect-RPC). Web encodes via @bufbuild/protobuf
        // .toBinary(), base64s the Uint8Array, sends as args["bytes"].
        if method.hasSuffix("_connect") {
            let bytes = try decodeBytes(args["bytes"])
            let resp = try await dispatchConnect(method: method, bytes: bytes)
            return encodeBytes(resp)
        }

        // ── State-cache mutators / readers (still JSON, not wire)
        switch method {
        case "apply_remote_op":
            guard let op = args["op"] else { throw RpcError.badArgs("op") }
            let json = try jsonString(from: op)
            try core.blocks.applyRemoteOp(json)
            return NSNull()

        case "set_last_op_id":
            guard let wsId = args["wsId"] as? String,
                  let id = args["id"] as? Int else { throw RpcError.badArgs("wsId+id") }
            core.blocks.setLastOpId(wsId, Int64(id))
            return NSNull()

        case "replace_workspaces_json":
            guard let json = args["json"] as? String else { throw RpcError.badArgs("json") }
            try core.blocks.replaceWorkspacesJson(json)
            return NSNull()

        case "upsert_workspace_json":
            guard let json = args["json"] as? String else { throw RpcError.badArgs("json") }
            try core.blocks.upsertWorkspaceJson(json)
            return NSNull()

        case "upsert_blocks_json":
            guard let json = args["json"] as? String else { throw RpcError.badArgs("json") }
            try core.blocks.upsertBlocksJson(json)
            return NSNull()

        case "upsert_refs_json":
            guard let json = args["json"] as? String else { throw RpcError.badArgs("json") }
            try core.blocks.upsertRefsJson(json)
            return NSNull()

        case "workspaces_json":     return core.blocks.workspacesJson()
        case "blocks_json":         return core.blocks.blocksJson()
        case "refs_json":           return core.blocks.refsJson()
        case "nest_children_json":  return core.blocks.nestChildrenJson()
        case "backlinks_json":      return core.blocks.backlinksJson()
        case "last_op_ids_json":    return core.blocks.lastOpIdsJson()

        case "get_block_json":
            guard let id = args["id"] as? String else { throw RpcError.badArgs("id") }
            return core.blocks.getBlockJson(id) ?? NSNull()

        case "list_children_json":
            guard let id = args["id"] as? String else { throw RpcError.badArgs("id") }
            return core.blocks.listChildrenJson(id)

        case "list_backlinks_json":
            guard let id = args["id"] as? String else { throw RpcError.badArgs("id") }
            return core.blocks.listBacklinksJson(id)

        case "type_defs_json":
            guard let wsId = args["wsId"] as? String else { throw RpcError.badArgs("wsId") }
            return core.blocks.typeDefsJson(wsId)

        case "last_op_id":
            guard let wsId = args["wsId"] as? String else { throw RpcError.badArgs("wsId") }
            return Int(core.blocks.lastOpId(wsId))

        default:
            throw RpcError.unknown(method)
        }
    }

    private func dispatchConnect(method: String, bytes: Data) async throws -> Data {
        switch method {
        case "apply_ops_connect":
            return try await core.blocks.applyOpsConnect(bytes)
        case "list_workspaces_connect":
            return try await core.blocks.listWorkspacesConnect(bytes)
        case "ensure_default_workspace_connect":
            return try await core.blocks.ensureDefaultWorkspaceConnect(bytes)
        case "create_workspace_connect":
            return try await core.blocks.createWorkspaceConnect(bytes)
        case "delete_workspace_connect":
            return try await core.blocks.deleteWorkspaceConnect(bytes)
        case "get_block_connect":
            return try await core.blocks.getBlockConnect(bytes)
        case "list_children_connect":
            return try await core.blocks.listChildrenConnect(bytes)
        case "list_backlinks_connect":
            return try await core.blocks.listBacklinksConnect(bytes)
        case "get_subtree_connect":
            return try await core.blocks.getSubtreeConnect(bytes)
        case "stream_ops_connect":
            return try await core.blocks.streamOpsConnect(bytes)
        case "list_type_defs_connect":
            return try await core.blocks.listTypeDefsConnect(bytes)
        case "semantic_search_connect":
            return try await core.blocks.semanticSearchConnect(bytes)
        default:
            throw RpcError.unknown(method)
        }
    }
}

public enum RpcError: Error, LocalizedError {
    case badArgs(String)
    case unknown(String)

    public var errorDescription: String? {
        switch self {
        case .badArgs(let f): return "Missing or invalid arg: \(f)"
        case .unknown(let m): return "Unknown RPC method: \(m)"
        }
    }
}

private func jsonString(from value: Any) throws -> String {
    let data = try JSONSerialization.data(withJSONObject: value, options: [.fragmentsAllowed])
    return String(data: data, encoding: .utf8) ?? "{}"
}

private func decodeBytes(_ value: Any?) throws -> Data {
    guard let s = value as? String, let data = Data(base64Encoded: s) else {
        throw RpcError.badArgs("bytes")
    }
    return data
}

private func encodeBytes(_ data: Data) -> String {
    data.base64EncodedString()
}
