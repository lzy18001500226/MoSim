import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import CoreClient
import DesignSystem

@Reducer
public struct TicketDetailFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable {
        public let slug: String
        public var ticket: TicketDto?
        public var linkedPods: [PodDto] = []
        public var isLoading: Bool = false
        public var errorMessage: String?

        public init(slug: String) { self.slug = slug }
    }

    public enum Action: Sendable {
        case onAppear
        case ticketLoaded(TicketDto)
        case linkedPodsLoaded([PodDto])
        case loadFailed(String)
        case spawnPodTapped
    }

    @Dependency(\.coreClient) var core

    public var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .onAppear:
                state.isLoading = true
                let s = state.slug
                return .run { send in
                    do {
                        async let ticket = core.getTicket(s)
                        let t = try await ticket
                        await send(.ticketLoaded(t))
                    } catch {
                        await send(.loadFailed(error.localizedDescription))
                    }
                }
            case .ticketLoaded(let t):
                state.isLoading = false
                state.ticket = t
                return .none
            case .linkedPodsLoaded(let pods):
                state.linkedPods = pods
                return .none
            case .loadFailed(let msg):
                state.isLoading = false
                state.errorMessage = msg
                return .none
            case .spawnPodTapped:
                return .none
            }
        }
    }
}

public struct TicketDetailView: View {
    let store: StoreOf<TicketDetailFeature>

    public init(store: StoreOf<TicketDetailFeature>) { self.store = store }

    public var body: some View {
        ZStack(alignment: .bottom) {
            AMColors.groupedBg.ignoresSafeArea()
            content
            if store.ticket != nil { spawnButton }
        }
        .navigationBarTitleDisplayMode(.inline)
        .navigationTitle(store.ticket?.slug ?? "—")
        .onAppear { store.send(.onAppear) }
    }

    @ViewBuilder
    private var content: some View {
        if let t = store.ticket {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header(t)
                    if let body = t.content, !body.isEmpty { description(body) }
                    detailsSection(t)
                    linkedPodsSection
                    Spacer(minLength: 100)
                }
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        } else if store.isLoading {
            ProgressView()
        }
    }

    private func header(_ t: TicketDto) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(t.title)
                .font(AMTypography.title2)
                .foregroundStyle(AMColors.foreground)
            HStack(spacing: 8) {
                AMChip(TicketLabels.status(t.status), variant: TicketLabels.statusVariant(t.status))
                AMChip(TicketLabels.priority(t.priority), variant: .neutral)
            }
        }
    }

    private func description(_ body: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            sectionHeader("DESCRIPTION")
            Text(body)
                .font(AMTypography.body)
                .foregroundStyle(AMColors.foreground)
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(AMColors.card)
                .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
        }
    }

    private func detailsSection(_ t: TicketDto) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            sectionHeader("DETAILS")
            VStack(spacing: 0) {
                detailRow("Repository", t.repositoryId.map { "#\($0)" } ?? "—")
                Divider().padding(.leading, 16)
                detailRow("Status", TicketLabels.status(t.status))
                Divider().padding(.leading, 16)
                detailRow("Priority", TicketLabels.priority(t.priority))
                Divider().padding(.leading, 16)
                detailRow("Linked Pods", "\(store.linkedPods.count)")
            }
            .background(AMColors.card)
            .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
        }
    }

    private func sectionHeader(_ text: String) -> some View {
        Text(text)
            .font(.system(size: 11, weight: .semibold))
            .foregroundStyle(AMColors.mutedForeground)
            .padding(.horizontal, 4)
    }

    private func detailRow(_ label: String, _ value: String) -> some View {
        HStack {
            Text(label).font(AMTypography.body).foregroundStyle(AMColors.foreground)
            Spacer()
            Text(value).font(AMTypography.body).foregroundStyle(AMColors.mutedForeground).lineLimit(1)
        }
        .padding(.horizontal, 16)
        .frame(height: 44)
    }

    @ViewBuilder
    private var linkedPodsSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            sectionHeader("LINKED PODS")
            if store.linkedPods.isEmpty {
                Text("No pods spawned for this ticket yet")
                    .font(AMTypography.body)
                    .foregroundStyle(AMColors.mutedForeground)
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(AMColors.card)
                    .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
            } else {
                VStack(spacing: 0) {
                    ForEach(store.linkedPods, id: \.key) { pod in
                        linkedPodRow(pod)
                        if pod.key != store.linkedPods.last?.key {
                            Divider().padding(.leading, 16)
                        }
                    }
                }
                .background(AMColors.card)
                .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
            }
        }
    }

    private func linkedPodRow(_ pod: PodDto) -> some View {
        HStack(spacing: 8) {
            Text(pod.key)
                .font(.system(size: 13, design: .monospaced))
                .foregroundStyle(AMColors.foreground)
            AMChip(pod.agentSlug, variant: .neutral)
            Spacer()
        }
        .padding(.horizontal, 16)
        .frame(height: 48)
    }

    private var spawnButton: some View {
        Button {
            store.send(.spawnPodTapped)
        } label: {
            Text("Spawn Pod")
                .font(AMTypography.bodySemibold)
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 52)
                .background(AMColors.primary)
                .clipShape(RoundedRectangle(cornerRadius: AMRadius.buttonSm))
        }
        .accessibilityIdentifier("ticket-spawn-pod")
        .padding(.horizontal, 16)
        .padding(.bottom, 16)
    }
}

enum TicketLabels {
    static func status(_ s: TicketStatusDto) -> String {
        switch s {
        case .backlog: return "Backlog"
        case .todo: return "Todo"
        case .inProgress: return "In Progress"
        case .inReview: return "In Review"
        case .done: return "Done"
        default: return "—"
        }
    }
    static func statusVariant(_ s: TicketStatusDto) -> AMChip.Variant {
        switch s {
        case .backlog: return .backlog
        case .todo: return .todo
        case .inProgress: return .running
        case .inReview: return .inReview
        case .done: return .done
        default: return .neutral
        }
    }
    static func priority(_ p: TicketPriorityDto) -> String {
        switch p {
        case .urgent: return "Urgent"
        case .high: return "High"
        case .medium: return "Medium"
        case .low: return "Low"
        default: return "None"
        }
    }
}
