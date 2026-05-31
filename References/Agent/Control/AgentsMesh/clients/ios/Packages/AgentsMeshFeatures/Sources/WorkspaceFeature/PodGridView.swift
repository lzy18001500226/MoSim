import ComposableArchitecture
import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Pod grid view — Chrome iOS Tab Switcher pattern. Mirrors
/// `design/mobile/pages/ios-pods-grid.pastel`. 2-column card grid where
/// each card shows the agent icon + pod_key + a 9pt mini-terminal preview
/// + a status footer. Tap to open the terminal.
public struct PodGridView: View {
    @Perception.Bindable var store: StoreOf<PodListFeature>

    public init(store: StoreOf<PodListFeature>) {
        self.store = store
    }

    private let columns = [
        GridItem(.flexible(), spacing: 12),
        GridItem(.flexible(), spacing: 12)
    ]

    public var body: some View {
        ZStack {
            AMColors.groupedBg.ignoresSafeArea()
            ScrollView {
                LazyVGrid(columns: columns, spacing: 12) {
                    ForEach(store.pods, id: \.key) { pod in
                        Button { store.send(.podTapped(pod.key)) } label: {
                            PodCard(pod: pod)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .padding(.bottom, 100)
            }
        }
        .onAppear { store.send(.onAppear) }
        .refreshable { store.send(.refreshRequested) }
    }
}

struct PodCard: View {
    let pod: PodDto

    var body: some View {
        VStack(spacing: 0) {
            header
            terminalPreview
            footer
        }
        .frame(height: 232)
        .background(AMColors.card)
        .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
        .overlay(
            RoundedRectangle(cornerRadius: AMRadius.cell)
                .stroke(AMColors.border, lineWidth: 1)
        )
        .shadow(color: .black.opacity(0.06), radius: 4, y: 2)
    }

    private var header: some View {
        HStack(spacing: 8) {
            AMAvatar(
                String(pod.agentSlug.prefix(1).uppercased()),
                shape: .roundedSquare,
                size: .xs,
                bg: agentColor,
                mono: true
            )
            Text(pod.key)
                .font(.system(size: 11, weight: .medium, design: .monospaced))
                .foregroundStyle(AMColors.foreground)
                .lineLimit(1)
            Spacer(minLength: 0)
            Image(systemName: "xmark")
                .font(.system(size: 12))
                .foregroundStyle(AMColors.mutedForeground)
        }
        .padding(.horizontal, 10)
        .frame(height: 36)
        .background(AMColors.card)
        .overlay(Rectangle().fill(AMColors.border).frame(height: 1), alignment: .bottom)
    }

    private var terminalPreview: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("$ \(pod.agentSlug) review")
                .font(.system(size: 9, design: .monospaced))
                .foregroundStyle(AMColors.codeText)
            Text("→ Analyzing…")
                .font(.system(size: 9, design: .monospaced))
                .foregroundStyle(AMColors.codeText.opacity(0.7))
            Spacer()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(AMColors.codeBg)
    }

    private var footer: some View {
        HStack {
            AMChip(statusLabel, variant: statusVariant, dot: true)
            Spacer()
            Text(timeAgo)
                .font(.system(size: 11))
                .foregroundStyle(AMColors.mutedForeground)
        }
        .padding(.horizontal, 10)
        .frame(height: 32)
        .background(AMColors.card)
    }

    private var agentColor: Color {
        switch pod.agentSlug.prefix(1).lowercased() {
        case "c": return AMColors.success
        case "x": return AMColors.primary
        case "a": return AMColors.warning
        default: return AMColors.purple
        }
    }
    private var statusLabel: String {
        switch pod.status {
        case .running: return "running"
        case .pending, .creating, .initializing: return "starting"
        case .paused: return "idle"
        default: return "done"
        }
    }
    private var statusVariant: AMChip.Variant {
        switch pod.status {
        case .running: return .running
        case .pending, .creating, .initializing: return .executing
        case .paused: return .idle
        default: return .done
        }
    }
    private var timeAgo: String {
        guard let last = pod.lastActivity ?? pod.startedAt,
              let date = ISO8601DateFormatter.cached.date(from: last) else { return "—" }
        let interval = Date().timeIntervalSince(date)
        if interval < 60 { return "\(Int(interval))s" }
        if interval < 3600 { return "\(Int(interval / 60))m" }
        return "\(Int(interval / 3600))h"
    }
}
