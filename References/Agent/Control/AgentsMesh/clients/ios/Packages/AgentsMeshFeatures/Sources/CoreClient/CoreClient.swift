import ComposableArchitecture
import Foundation
import AgentsMeshCore

/// Typed wrapper over the Rust `AgentsMeshCore` methods that reducers need.
/// Structuring as a TCA `DependencyClient` gives us trivial test overrides
/// and decouples reducers from `CoreBridge.shared`.
public struct CoreClient: Sendable {
    // ── Auth
    public var login: @Sendable (_ email: String, _ password: String) async throws -> AuthSessionDto
    public var logout: @Sendable () async throws -> Void
    public var isAuthenticated: @Sendable () -> Bool
    public var bootstrap: @Sendable () async throws -> BootstrapResultDto
    public var currentUser: @Sendable () -> UserDto?
    public var currentOrg: @Sendable () -> OrganizationDto?
    public var fetchOrganizations: @Sendable () async throws -> [OrganizationDto]
    public var switchOrg: @Sendable (_ slug: String) throws -> Void

    // ── Workspace (Pods + Runners)
    public var listPods: @Sendable (_ status: String?) async throws -> PodListResponseDto
    public var getPod: @Sendable (_ key: String) async throws -> PodDto
    public var createPod: @Sendable (_ req: CreatePodRequestDto) async throws -> CreatePodResponseDto
    public var terminatePod: @Sendable (_ key: String) async throws -> Void
    public var getPodRelayConnection: @Sendable (_ key: String) async throws -> PodConnectionInfoDto
    public var listRunners: @Sendable () async throws -> RunnerListResponseDto

    // ── Infra (More tab destinations)
    public var getMeshTopology: @Sendable () async throws -> MeshTopologyDto
    public var listLoops: @Sendable () async throws -> LoopListResponseDto
    public var listRepositories: @Sendable () async throws -> RepositoryListResponseDto

    // ── Channels
    public var listChannels: @Sendable (_ includeArchived: Bool?) async throws -> ChannelListResponseDto
    public var getChannel: @Sendable (_ id: Int64) async throws -> ChannelDto
    public var getChannelMessages: @Sendable (_ id: Int64, _ limit: UInt32?, _ beforeId: Int64?) async throws -> ChannelMessageListResponseDto
    public var sendChannelMessage: @Sendable (_ id: Int64, _ contentJson: String, _ podKey: String?, _ replyTo: Int64?) async throws -> ChannelMessageDto
    public var markChannelRead: @Sendable (_ id: Int64, _ messageId: Int64) async throws -> Void
    public var getChannelUnreadCounts: @Sendable () async throws -> ChannelUnreadResponseDto
    public var getChannelPods: @Sendable (_ id: Int64) async throws -> PodListResponseDto

    // ── Tickets
    public var listTickets: @Sendable (_ status: String?, _ limit: UInt32?, _ offset: UInt32?) async throws -> TicketListResponseDto
    public var getTicket: @Sendable (_ slug: String) async throws -> TicketDto
    public var getTicketBoard: @Sendable (_ repositoryId: Int64?) async throws -> BoardResponseDto
    public var updateTicketStatus: @Sendable (_ slug: String, _ status: TicketStatusDto) async throws -> TicketDto
    public var createTicket: @Sendable (_ req: CreateTicketRequestDto) async throws -> TicketDto
    public var addTicketAssignee: @Sendable (_ slug: String, _ userId: Int64) async throws -> Void
    public var listLabels: @Sendable (_ repositoryId: Int64?) async throws -> LabelListResponseDto

    // ── Blocks
    public var blocks: BlocksCoreClient
}

extension CoreClient: DependencyKey {
    public static let liveValue: CoreClient = {
        // Closures capture CoreBridge.shared.core lazily so this struct
        // can be instantiated before bootstrap (e.g. in previews).
        let core = { CoreBridge.shared.core }
        return CoreClient(
            login: { email, password in
                try await core().login(email: email, password: password)
            },
            logout: { try await core().logout() },
            isAuthenticated: { core().isAuthenticated() },
            bootstrap: { try await core().bootstrap() },
            currentUser: { core().getCurrentUser() },
            currentOrg: { core().getCurrentOrg() },
            fetchOrganizations: { try await core().fetchOrganizations() },
            switchOrg: { slug in try core().switchOrg(slug: slug) },

            listPods: { status in
                try await core().listPods(
                    status: status, runnerId: nil, createdById: nil,
                    limit: nil, offset: nil
                )
            },
            getPod: { key in try await core().getPod(podKey: key) },
            createPod: { req in try await core().createPod(req: req) },
            terminatePod: { key in try await core().terminatePod(podKey: key) },
            getPodRelayConnection: { key in try await core().getPodRelayConnection(podKey: key) },
            listRunners: { try await core().listRunners(status: nil) },

            getMeshTopology: { try await core().getMeshTopology() },
            listLoops: { try await core().listLoops(status: nil, limit: nil, offset: nil) },
            listRepositories: { try await core().listRepositories() },

            listChannels: { includeArchived in try await core().listChannels(includeArchived: includeArchived) },
            getChannel: { id in try await core().getChannel(id: id) },
            getChannelMessages: { id, limit, beforeId in
                try await core().getChannelMessages(id: id, limit: limit, beforeId: beforeId)
            },
            sendChannelMessage: { id, contentJson, podKey, replyTo in
                try await core().sendChannelMessage(id: id, contentJson: contentJson, podKey: podKey, replyTo: replyTo)
            },
            markChannelRead: { id, messageId in try await core().markChannelRead(id: id, messageId: messageId) },
            getChannelUnreadCounts: { try await core().getChannelUnreadCounts() },
            getChannelPods: { id in try await core().getChannelPods(id: id) },

            listTickets: { status, limit, offset in
                try await core().listTickets(status: status, limit: limit, offset: offset)
            },
            getTicket: { slug in try await core().getTicket(slug: slug) },
            getTicketBoard: { repoId in try await core().getTicketBoard(repositoryId: repoId) },
            updateTicketStatus: { slug, status in
                try await core().updateTicketStatus(slug: slug, status: status)
            },
            createTicket: { req in try await core().createTicket(req: req) },
            addTicketAssignee: { slug, userId in
                try await core().addTicketAssignee(slug: slug, userId: userId)
            },
            listLabels: { repoId in try await core().listLabels(repositoryId: repoId) },

            blocks: .live
        )
    }()

    public static let testValue: CoreClient = CoreClient(
        login: unimplemented("CoreClient.login"),
        logout: unimplemented("CoreClient.logout"),
        isAuthenticated: unimplemented("CoreClient.isAuthenticated", placeholder: false),
        bootstrap: unimplemented("CoreClient.bootstrap", placeholder: .anonymous),
        currentUser: unimplemented("CoreClient.currentUser", placeholder: nil),
        currentOrg: unimplemented("CoreClient.currentOrg", placeholder: nil),
        fetchOrganizations: unimplemented("CoreClient.fetchOrganizations"),
        switchOrg: unimplemented("CoreClient.switchOrg"),
        listPods: unimplemented("CoreClient.listPods"),
        getPod: unimplemented("CoreClient.getPod"),
        createPod: unimplemented("CoreClient.createPod"),
        terminatePod: unimplemented("CoreClient.terminatePod"),
        getPodRelayConnection: unimplemented("CoreClient.getPodRelayConnection"),
        listRunners: unimplemented("CoreClient.listRunners"),
        getMeshTopology: unimplemented("CoreClient.getMeshTopology"),
        listLoops: unimplemented("CoreClient.listLoops"),
        listRepositories: unimplemented("CoreClient.listRepositories"),
        listChannels: unimplemented("CoreClient.listChannels"),
        getChannel: unimplemented("CoreClient.getChannel"),
        getChannelMessages: unimplemented("CoreClient.getChannelMessages"),
        sendChannelMessage: unimplemented("CoreClient.sendChannelMessage"),
        markChannelRead: unimplemented("CoreClient.markChannelRead"),
        getChannelUnreadCounts: unimplemented("CoreClient.getChannelUnreadCounts"),
        getChannelPods: unimplemented("CoreClient.getChannelPods"),
        listTickets: unimplemented("CoreClient.listTickets"),
        getTicket: unimplemented("CoreClient.getTicket"),
        getTicketBoard: unimplemented("CoreClient.getTicketBoard"),
        updateTicketStatus: unimplemented("CoreClient.updateTicketStatus"),
        createTicket: unimplemented("CoreClient.createTicket"),
        addTicketAssignee: unimplemented("CoreClient.addTicketAssignee"),
        listLabels: unimplemented("CoreClient.listLabels"),
        blocks: .unimplemented
    )
}

public extension DependencyValues {
    var coreClient: CoreClient {
        get { self[CoreClient.self] }
        set { self[CoreClient.self] = newValue }
    }
}
