import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Org drawer — Lark-inspired slide-in. Left 60pt rail with org avatars,
/// 280pt main column with account header + 7 menu items, right strip is
/// dim overlay (tap to close). Mirrors `design/mobile/pages/ios-org-drawer.pastel`.
public struct OrgDrawerView: View {
    @Perception.Bindable var store: StoreOf<OrgDrawerFeature>
    let onClose: () -> Void

    public init(store: StoreOf<OrgDrawerFeature>, onClose: @escaping () -> Void) {
        self.store = store
        self.onClose = onClose
    }

    public var body: some View {
        HStack(spacing: 0) {
            rail
            mainColumn
        }
        .ignoresSafeArea(.container, edges: .bottom)
        .onAppear { store.send(.onAppear) }
    }

    private var rail: some View {
        VStack(spacing: 4) {
            ForEach(store.organizations, id: \.slug) { org in
                Button { store.send(.orgTapped(slug: org.slug)) } label: {
                    railItem(for: org)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("drawer-org-\(org.slug)")
            }
            Spacer()
        }
        .padding(.top, 60)
        .frame(width: 60)
        .background(AMColors.groupedBg)
    }

    private func railItem(for org: OrganizationDto) -> some View {
        let isActive = org.slug == store.currentOrgSlug
        let initial = String(org.name.prefix(1).uppercased())
        return VStack(spacing: 4) {
            HStack(spacing: 6) {
                if isActive {
                    Capsule().fill(AMColors.primary).frame(width: 3, height: 36)
                } else {
                    Color.clear.frame(width: 3, height: 36)
                }
                AMAvatar(initial, shape: .roundedSquare, size: .md, bg: tint(for: org.slug), mono: true)
            }
            Text(org.name)
                .font(.system(size: 9, weight: isActive ? .medium : .regular))
                .foregroundStyle(isActive ? AMColors.foreground : AMColors.mutedForeground)
                .lineLimit(1)
        }
        .padding(.vertical, 10)
    }

    private var mainColumn: some View {
        VStack(alignment: .leading, spacing: 0) {
            accountHeader
            ScrollView {
                VStack(spacing: 0) {
                    menuGroup {
                        menuRow("person.fill",         "Account",          color: AMColors.primary)
                    }
                    menuGroup {
                        menuRow("bell.fill",           "Notifications",    color: AMColors.destructive, meta: "On")
                        menuRow("paintpalette.fill",   "Appearance",       color: AMColors.purple, meta: "Auto")
                        menuRow("globe",               "Language",         color: AMColors.success)
                    }
                    menuGroup {
                        menuRow("key.fill",            "Agent Credentials", color: AMColors.warning)
                        menuRow("arrow.triangle.branch", "Git",            color: AMColors.primary)
                    }
                    menuGroup {
                        menuRow("building.2.fill",     "Organization",     color: AMColors.primary)
                    }
                    menuGroup {
                        menuRow("questionmark.circle.fill", "Help & Support", color: AMColors.warning)
                    }
                    menuGroup {
                        Button { store.send(.signOutTapped) } label: {
                            HStack(spacing: 14) {
                                Image(systemName: "rectangle.portrait.and.arrow.right")
                                    .font(.system(size: 17))
                                    .foregroundStyle(AMColors.destructive)
                                    .frame(width: 28, height: 28)
                                Text("Sign Out")
                                    .font(.system(size: 17))
                                    .foregroundStyle(AMColors.destructive)
                                Spacer()
                            }
                            .padding(.horizontal, 16)
                            .frame(height: 48)
                            .background(AMColors.card)
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("drawer-signout")
                    }
                }
                .padding(.bottom, 40)
            }
        }
        .frame(maxWidth: .infinity)
        .background(AMColors.card)
    }

    private var accountHeader: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                AMAvatar("S", size: .lg, bg: AMColors.primary)
                Spacer()
                Image(systemName: "pencil")
                    .font(.system(size: 16))
                    .foregroundStyle(AMColors.foreground)
                    .frame(width: 32, height: 32)
                    .background(AMColors.groupedBg)
                    .clipShape(Circle())
            }
            VStack(alignment: .leading, spacing: 2) {
                Text("Stone.D")
                    .font(.system(size: 22, weight: .semibold))
                    .foregroundStyle(AMColors.foreground)
                Text("@stone-d · AgentsMesh")
                    .font(.system(size: 13))
                    .foregroundStyle(AMColors.mutedForeground)
            }
        }
        .padding(.horizontal, 16)
        .padding(.top, 60)
        .padding(.bottom, 12)
    }

    @ViewBuilder
    private func menuGroup<Content: View>(@ViewBuilder _ content: () -> Content) -> some View {
        VStack(spacing: 0) { content() }
            .padding(.top, 12)
    }

    private func menuRow(_ symbol: String, _ label: String, color: Color, meta: String? = nil) -> some View {
        HStack(spacing: 14) {
            Image(systemName: symbol)
                .font(.system(size: 17))
                .foregroundStyle(color)
                .frame(width: 28, height: 28)
            Text(label)
                .font(.system(size: 17))
                .foregroundStyle(AMColors.foreground)
            Spacer()
            if let meta {
                Text(meta).font(.system(size: 15)).foregroundStyle(AMColors.mutedForeground)
            }
            Image(systemName: "chevron.right")
                .font(.system(size: 12, weight: .medium))
                .foregroundStyle(Color(red: 0.78, green: 0.78, blue: 0.80))
        }
        .padding(.horizontal, 16)
        .frame(height: 48)
        .background(AMColors.card)
    }

    private func tint(for slug: String) -> Color {
        let palette: [Color] = [AMColors.primary, AMColors.purple, AMColors.success, AMColors.warning]
        return palette[abs(slug.hashValue) % palette.count]
    }
}
