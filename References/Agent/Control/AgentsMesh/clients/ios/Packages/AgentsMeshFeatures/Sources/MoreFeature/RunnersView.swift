import SwiftUI
import ComposableArchitecture
import AgentsMeshCore
import CoreClient
import DesignSystem

/// Runners — host machines that execute pods. Shows current/max
/// capacity + last-heartbeat freshness so the user can spot dead nodes.
struct RunnersView: View {
    @Dependency(\.coreClient) private var core

    var body: some View {
        LoadingState(load: { try await core.listRunners() }) { resp in
            if resp.runners.isEmpty {
                EmptyState(
                    symbol: "server.rack",
                    title: "No runners",
                    detail: "Register a runner from the host machine to execute pods."
                )
            } else {
                ScrollView {
                    LazyVStack(spacing: 8) {
                        ForEach(resp.runners, id: \.id) { row($0) }
                    }
                    .padding(16)
                }
            }
        }
    }

    private func row(_ r: RunnerDto) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                Image(systemName: "server.rack")
                    .foregroundStyle(AMColors.purple)
                Text(r.name).font(AMTypography.bodySemibold)
                Spacer()
                Text(label(r.status))
                    .font(.system(size: 11, weight: .medium))
                    .padding(.horizontal, 8).padding(.vertical, 2)
                    .background(color(r.status).opacity(0.18))
                    .foregroundStyle(color(r.status))
                    .clipShape(Capsule())
            }
            HStack(spacing: 12) {
                Text("\(r.activePodCount) / \(r.maxConcurrentPods) pods")
                    .font(.system(size: 12))
                    .foregroundStyle(AMColors.mutedForeground)
                if let v = r.version, !v.isEmpty {
                    Text("v\(v)").font(.system(size: 11))
                        .foregroundStyle(AMColors.mutedForeground)
                }
                if let hb = r.lastHeartbeat, !hb.isEmpty {
                    Text(relTime(hb)).font(.system(size: 11))
                        .foregroundStyle(AMColors.mutedForeground)
                }
            }
        }
        .padding(12)
        .background(AMColors.card)
        .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
        .overlay(RoundedRectangle(cornerRadius: AMRadius.cell)
            .stroke(AMColors.border, lineWidth: 1))
    }

    private func label(_ s: RunnerStatusDto) -> String {
        switch s {
        case .online: return "Online"
        case .offline: return "Offline"
        case .maintenance: return "Maintenance"
        case .unknown: return "Unknown"
        }
    }

    private func color(_ s: RunnerStatusDto) -> Color {
        switch s {
        case .online: return AMColors.success
        case .offline: return AMColors.mutedForeground
        case .maintenance: return AMColors.warning
        case .unknown: return AMColors.mutedForeground
        }
    }

    private func relTime(_ iso: String) -> String {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        guard let d = f.date(from: iso) ?? ISO8601DateFormatter().date(from: iso) else {
            return iso
        }
        let r = RelativeDateTimeFormatter()
        r.unitsStyle = .short
        return r.localizedString(for: d, relativeTo: Date())
    }
}
