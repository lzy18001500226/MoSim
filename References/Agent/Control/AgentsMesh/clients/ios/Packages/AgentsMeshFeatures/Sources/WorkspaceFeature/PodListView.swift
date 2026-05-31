import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Pod list view — Lark-style mobile list. Mirrors `design/mobile/pages/ios-pods-list.pastel`.
/// Mine/Others/Completed segment + 64pt list rows. Tap → open terminal.
public struct PodListView: View {
    @Perception.Bindable var store: StoreOf<PodListFeature>

    public init(store: StoreOf<PodListFeature>) {
        self.store = store
    }

    @State private var scope: PodScope = .mine

    public var body: some View {
        ZStack {
            AMColors.groupedBg.ignoresSafeArea()
            content
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button { store.send(.avatarTapped) } label: {
                    HStack(spacing: 8) {
                        AMAvatar("S", size: .sm, bg: AMColors.primary)
                        Text("Pods")
                            .font(AMTypography.navTitle)
                            .foregroundStyle(AMColors.foreground)
                    }
                }
                .accessibilityIdentifier("nav-avatar")
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button { store.send(.composeTapped) } label: {
                    Image(systemName: "plus")
                        .font(.system(size: 17, weight: .medium))
                        .foregroundStyle(AMColors.primary)
                }
                .accessibilityIdentifier("nav-compose")
            }
        }
        .searchable(
            text: $store.searchQuery.sending(\.searchQueryChanged),
            placement: .navigationBarDrawer(displayMode: .automatic),
            prompt: "Search pod / agent"
        )
        .onAppear { store.send(.onAppear) }
        .refreshable { store.send(.refreshRequested) }
        .sheet(isPresented: $store.showingCompose.sending(\.setComposeVisible)) {
            CreatePodSheet(
                isPresented: $store.showingCompose.sending(\.setComposeVisible)
            ) { req in
                store.send(.createPodRequested(req))
            }
        }
    }

    @ViewBuilder
    private var content: some View {
        VStack(spacing: 0) {
            segmentBar
            list
        }
    }

    private var segmentBar: some View {
        AMSegmentedControl(
            [(label: "Mine", tag: .mine), (label: "Others", tag: .others), (label: "Completed", tag: .completed)],
            selection: $scope
        )
        .padding(.horizontal, 16)
        .padding(.top, 8)
        .padding(.bottom, 8)
        .background(AMColors.groupedBg)
    }

    @ViewBuilder
    private var list: some View {
        if store.isLoading && store.pods.isEmpty {
            ProgressView().frame(maxHeight: .infinity)
        } else if filteredPods.isEmpty {
            emptyState.frame(maxHeight: .infinity)
        } else {
            ScrollView {
                LazyVStack(spacing: 0) {
                    ForEach(Array(filteredPods.enumerated()), id: \.element.key) { index, pod in
                        Button { store.send(.podTapped(pod.key)) } label: {
                            PodRow(pod: pod)
                        }
                        .buttonStyle(.plain)
                        if index < filteredPods.count - 1 {
                            Divider().background(AMColors.separator).padding(.leading, 68)
                        }
                    }
                }
                .padding(.vertical, 4)
                .background(AMColors.card)
                .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
                .padding(.horizontal, 16)
                .padding(.bottom, 100)
            }
        }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "terminal")
                .font(.system(size: 48))
                .foregroundStyle(AMColors.mutedForeground)
            Text("No pods")
                .font(AMTypography.heading)
                .foregroundStyle(AMColors.foreground)
            Text("Tap + to spin up your first agent.")
                .font(AMTypography.body)
                .foregroundStyle(AMColors.mutedForeground)
        }
    }

    private var filteredPods: [PodDto] {
        let scoped: [PodDto]
        switch scope {
        case .mine: scoped = store.pods.filter { $0.status == .running || $0.status == .paused || $0.status == .pending }
        case .others: scoped = store.pods.filter { $0.status == .creating || $0.status == .initializing }
        case .completed: scoped = store.pods.filter { $0.status == .completed || $0.status == .stopping || $0.status == .disconnected }
        }
        let q = store.searchQuery.trimmingCharacters(in: .whitespaces).lowercased()
        guard !q.isEmpty else { return scoped }
        return scoped.filter { pod in
            pod.key.lowercased().contains(q)
                || pod.agentSlug.lowercased().contains(q)
                || (pod.alias?.lowercased().contains(q) ?? false)
        }
    }

    enum PodScope: Hashable { case mine, others, completed }
}
