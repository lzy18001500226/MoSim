import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Pages tree view — mirrors web BlocksSidebar. Search pill at top,
/// PAGES section header with +, then recursive tree of nodes.
public struct BlocksTreeView: View {
    @Perception.Bindable var store: StoreOf<BlocksFeature>

    public init(store: StoreOf<BlocksFeature>) { self.store = store }

    public var body: some View {
        ZStack {
            AMColors.card.ignoresSafeArea()
            content
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button { store.send(.avatarTapped) } label: {
                    HStack(spacing: 8) {
                        AMAvatar("S", size: .sm, bg: AMColors.primary)
                        Text("Blocks")
                            .font(AMTypography.navTitle)
                            .foregroundStyle(AMColors.foreground)
                    }
                }
                .accessibilityIdentifier("nav-avatar")
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button { store.send(.composeTapped) } label: {
                    Image(systemName: "plus").font(.system(size: 17, weight: .medium)).foregroundStyle(AMColors.primary)
                }
                .accessibilityIdentifier("nav-compose")
            }
        }
        .onAppear { store.send(.onAppear) }
    }

    @ViewBuilder
    private var content: some View {
        VStack(spacing: 0) {
            searchPill
            AMSectionHeader("PAGES", onAdd: { })
            if store.isLoading && store.tree.isEmpty {
                ProgressView().frame(maxHeight: .infinity)
            } else if store.tree.isEmpty {
                emptyState.frame(maxHeight: .infinity)
            } else {
                ScrollView {
                    LazyVStack(spacing: 0) {
                        ForEach(store.tree) { node in
                            TreeNodeView(node: node, depth: 0) { id in
                                store.send(.pageTapped(id))
                            }
                        }
                    }
                    .padding(.bottom, 100)
                }
            }
        }
    }

    private var searchPill: some View {
        HStack(spacing: 8) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 16))
                .foregroundStyle(AMColors.primary)
            Text("Search blocks · semantic")
                .font(.system(size: 14))
                .foregroundStyle(AMColors.mutedForeground)
            Spacer()
        }
        .padding(.horizontal, 12)
        .frame(height: 36)
        .background(AMColors.groupedBg)
        .clipShape(RoundedRectangle(cornerRadius: 10))
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "doc.text")
                .font(.system(size: 48))
                .foregroundStyle(AMColors.mutedForeground)
            Text("No pages yet").font(AMTypography.heading).foregroundStyle(AMColors.foreground)
            Text("Tap + to create your first page.").font(AMTypography.body).foregroundStyle(AMColors.mutedForeground)
        }
    }
}

/// Recursive tree row.
struct TreeNodeView: View {
    let node: PageNode
    let depth: Int
    let onTap: (String) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Button { onTap(node.id) } label: {
                HStack(spacing: 6) {
                    Image(systemName: "chevron.right")
                        .font(.system(size: 11))
                        .foregroundStyle(AMColors.mutedForeground)
                    Text(node.icon ?? "📄")
                        .font(.system(size: 14))
                    Text(node.title)
                        .font(.system(size: 15))
                        .foregroundStyle(AMColors.foreground)
                        .lineLimit(1)
                    Spacer()
                }
                .padding(.leading, CGFloat(12 + depth * 16))
                .padding(.trailing, 16)
                .frame(height: 36)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("page-row-\(node.id)")

            ForEach(node.children) { child in
                TreeNodeView(node: child, depth: depth + 1, onTap: onTap)
            }
        }
    }
}
