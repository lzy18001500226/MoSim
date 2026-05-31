import SwiftUI
import ComposableArchitecture
import AgentsMeshCore
import CoreClient
import DesignSystem

/// Loops list — per-org scheduled automation entries. Each row shows
/// schedule, agent, enabled state. Maps to the web's `/[org]/loops`.
struct LoopsView: View {
    @Dependency(\.coreClient) private var core

    var body: some View {
        LoadingState(load: { try await core.listLoops() }) { resp in
            if resp.loops.isEmpty {
                EmptyState(
                    symbol: "repeat",
                    title: "No loops yet",
                    detail: "Schedule a loop to run an agent automatically."
                )
            } else {
                ScrollView {
                    LazyVStack(spacing: 8) {
                        ForEach(resp.loops, id: \.id) { row($0) }
                    }
                    .padding(16)
                }
            }
        }
    }

    private func row(_ loop: LoopDataDto) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                Image(systemName: "repeat")
                    .foregroundStyle(loop.isEnabled ? AMColors.success : AMColors.mutedForeground)
                Text(loop.name).font(AMTypography.bodySemibold)
                Spacer()
                if !loop.isEnabled {
                    Text("Paused")
                        .font(.system(size: 11, weight: .medium))
                        .padding(.horizontal, 8).padding(.vertical, 2)
                        .background(AMColors.mutedForeground.opacity(0.18))
                        .foregroundStyle(AMColors.mutedForeground)
                        .clipShape(Capsule())
                }
            }
            if let d = loop.description, !d.isEmpty {
                Text(d).font(.system(size: 13))
                    .foregroundStyle(AMColors.mutedForeground)
                    .lineLimit(2)
            }
            HStack(spacing: 12) {
                if let s = loop.schedule, !s.isEmpty {
                    metaChip("clock", s)
                }
                if let a = loop.agentSlug, !a.isEmpty {
                    metaChip("cpu", a)
                }
            }
        }
        .padding(12)
        .background(AMColors.card)
        .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
        .overlay(RoundedRectangle(cornerRadius: AMRadius.cell)
            .stroke(AMColors.border, lineWidth: 1))
    }

    private func metaChip(_ symbol: String, _ text: String) -> some View {
        HStack(spacing: 4) {
            Image(systemName: symbol).font(.system(size: 10))
            Text(text).font(.system(size: 11)).lineLimit(1)
        }
        .foregroundStyle(AMColors.mutedForeground)
    }
}
