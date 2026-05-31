import SwiftUI
import AgentsMeshCore
import DesignSystem

/// Pod row + grid card visuals shared between PodListView and PodGridView.
/// Mirrors `design/mobile/pages/ios-pods-list.pastel` and `ios-pods-grid.pastel`.

/// 64pt list-cell row — used in PodListView.
public struct PodRow: View {
    let pod: PodDto

    public init(pod: PodDto) { self.pod = pod }

    public var body: some View {
        HStack(spacing: 12) {
            AMAvatar(
                String(pod.agentSlug.prefix(1).uppercased()),
                shape: .roundedSquare,
                size: .md,
                bg: agentColor,
                mono: true
            )
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(pod.key)
                        .font(.system(size: 15, weight: .semibold, design: .monospaced))
                        .foregroundStyle(AMColors.foreground)
                    Spacer()
                    Text(timeAgo)
                        .font(.system(size: 13))
                        .foregroundStyle(AMColors.mutedForeground)
                }
                HStack(spacing: 8) {
                    Text(pod.agentSlug)
                        .font(.system(size: 13, design: .monospaced))
                        .foregroundStyle(AMColors.mutedForeground)
                    AMChip(statusLabel, variant: statusVariant, dot: true)
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .frame(height: 64)
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
        case .stopping: return "stopping"
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
        guard let last = pod.lastActivity ?? pod.startedAt else { return "—" }
        return formatTime(last)
    }
}

private func formatTime(_ isoString: String) -> String {
    guard let date = ISO8601DateFormatter.cached.date(from: isoString) else { return "—" }
    let interval = Date().timeIntervalSince(date)
    if interval < 60 { return "\(Int(interval))s" }
    if interval < 3600 { return "\(Int(interval / 60))m" }
    if interval < 86400 { return "\(Int(interval / 3600))h" }
    return "\(Int(interval / 86400))d"
}

extension ISO8601DateFormatter {
    static let cached: ISO8601DateFormatter = {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return f
    }()
}
