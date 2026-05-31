import Foundation
import AgentsMeshCore

/// Construction site for the `live` and `unimplemented` `BlocksCoreClient`
/// instances. Pulled out of `BlocksCoreClient.swift` to keep that file
/// focused on the public surface and stay under the 200-line cap.

func liveBlocksCoreClient() -> BlocksCoreClient {
    let core = { CoreBridge.shared.core }
    return BlocksCoreClient(
        applyOpsConnect: { try await core().blocksApplyOpsConnect(request: $0) },
        listWorkspacesConnect: { try await core().blocksListWorkspacesConnect(request: $0) },
        ensureDefaultWorkspaceConnect: { try await core().blocksEnsureDefaultWorkspaceConnect(request: $0) },
        createWorkspaceConnect: { try await core().blocksCreateWorkspaceConnect(request: $0) },
        deleteWorkspaceConnect: { try await core().blocksDeleteWorkspaceConnect(request: $0) },
        getBlockConnect: { try await core().blocksGetBlockConnect(request: $0) },
        listChildrenConnect: { try await core().blocksListChildrenConnect(request: $0) },
        listBacklinksConnect: { try await core().blocksListBacklinksConnect(request: $0) },
        getSubtreeConnect: { try await core().blocksGetSubtreeConnect(request: $0) },
        streamOpsConnect: { try await core().blocksStreamOpsConnect(request: $0) },
        listTypeDefsConnect: { try await core().blocksListTypeDefsConnect(request: $0) },
        semanticSearchConnect: { try await core().blocksSemanticSearchConnect(request: $0) },

        applyRemoteOp: { json in try core().blocksApplyRemoteOp(opJson: json) },
        setLastOpId: { ws, id in core().blocksSetLastOpId(workspaceId: ws, id: id) },

        ensureDefaultWorkspace: { try await core().blocksEnsureDefaultWorkspace() },
        listWorkspaces: { try await core().blocksListWorkspaces() },
        getSubtree: { ws, root, depth in
            try await core().blocksGetSubtree(workspaceId: ws, rootId: root, maxDepth: depth)
        },
        getBlock: { id in try await core().blocksGetBlock(id: id) },
        semanticSearch: { ws, req in
            try await core().blocksSemanticSearch(workspaceId: ws, req: req)
        },

        workspacesJson: { core().blocksWorkspacesJson() },
        blocksJson: { core().blocksBlocksJson() },
        refsJson: { core().blocksRefsJson() },
        nestChildrenJson: { core().blocksNestChildrenJson() },
        backlinksJson: { core().blocksBacklinksJson() },
        lastOpIdsJson: { core().blocksLastOpIdsJson() },
        lastOpId: { ws in core().blocksLastOpId(workspaceId: ws) },

        getBlockJson: { id in core().blocksGetBlockJson(id: id) },
        listChildrenJson: { id in core().blocksListChildrenJson(parentId: id) },
        listBacklinksJson: { id in core().blocksListBacklinksJson(targetId: id) },
        typeDefsJson: { ws in core().blocksTypeDefsJson(workspaceId: ws) },

        replaceWorkspacesJson: { json in try core().blocksReplaceWorkspacesJson(listJson: json) },
        upsertWorkspaceJson: { json in try core().blocksUpsertWorkspaceJson(wsJson: json) },
        upsertBlocksJson: { json in try core().blocksUpsertBlocksJson(blocksJson: json) },
        upsertRefsJson: { json in try core().blocksUpsertRefsJson(refsJson: json) }
    )
}

func unimplementedBlocksCoreClient() -> BlocksCoreClient {
    BlocksCoreClient(
        applyOpsConnect: { _ in fatalError("unimplemented: blocks.applyOpsConnect") },
        listWorkspacesConnect: { _ in fatalError("unimplemented: blocks.listWorkspacesConnect") },
        ensureDefaultWorkspaceConnect: { _ in fatalError("unimplemented: blocks.ensureDefaultWorkspaceConnect") },
        createWorkspaceConnect: { _ in fatalError("unimplemented: blocks.createWorkspaceConnect") },
        deleteWorkspaceConnect: { _ in fatalError("unimplemented: blocks.deleteWorkspaceConnect") },
        getBlockConnect: { _ in fatalError("unimplemented: blocks.getBlockConnect") },
        listChildrenConnect: { _ in fatalError("unimplemented: blocks.listChildrenConnect") },
        listBacklinksConnect: { _ in fatalError("unimplemented: blocks.listBacklinksConnect") },
        getSubtreeConnect: { _ in fatalError("unimplemented: blocks.getSubtreeConnect") },
        streamOpsConnect: { _ in fatalError("unimplemented: blocks.streamOpsConnect") },
        listTypeDefsConnect: { _ in fatalError("unimplemented: blocks.listTypeDefsConnect") },
        semanticSearchConnect: { _ in fatalError("unimplemented: blocks.semanticSearchConnect") },

        applyRemoteOp: { _ in fatalError("unimplemented: blocks.applyRemoteOp") },
        setLastOpId: { _, _ in fatalError("unimplemented: blocks.setLastOpId") },

        ensureDefaultWorkspace: { fatalError("unimplemented: blocks.ensureDefaultWorkspace") },
        listWorkspaces: { fatalError("unimplemented: blocks.listWorkspaces") },
        getSubtree: { _, _, _ in fatalError("unimplemented: blocks.getSubtree") },
        getBlock: { _ in fatalError("unimplemented: blocks.getBlock") },
        semanticSearch: { _, _ in fatalError("unimplemented: blocks.semanticSearch") },

        workspacesJson: { "{}" },
        blocksJson: { "{}" },
        refsJson: { "{}" },
        nestChildrenJson: { "{}" },
        backlinksJson: { "{}" },
        lastOpIdsJson: { "{}" },
        lastOpId: { _ in 0 },

        getBlockJson: { _ in nil },
        listChildrenJson: { _ in "{\"blocks\":[],\"refs\":[]}" },
        listBacklinksJson: { _ in "{\"refs\":[]}" },
        typeDefsJson: { _ in "{\"blocks\":[]}" },

        replaceWorkspacesJson: { _ in fatalError("unimplemented: blocks.replaceWorkspacesJson") },
        upsertWorkspaceJson: { _ in fatalError("unimplemented: blocks.upsertWorkspaceJson") },
        upsertBlocksJson: { _ in fatalError("unimplemented: blocks.upsertBlocksJson") },
        upsertRefsJson: { _ in fatalError("unimplemented: blocks.upsertRefsJson") }
    )
}
