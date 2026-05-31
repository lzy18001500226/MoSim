import SwiftUI
import ComposableArchitecture
import AgentsMeshCore
import CoreClient
import DesignSystem

/// Mesh — runner-grouped pod / agent topology. Mirrors what the web's
/// `/[org]/mesh` page lists: each runner card shows current/max pod
/// capacity and the pods currently assigned to it.
struct MeshView: View {
    @Dependency(\.coreClient) private var core

    var body: some View {
        LoadingState(load: { try await core.getMeshTopology() }) { topology in
            ScrollView {
                LazyVStack(spacing: 12) {
                    if topology.runners.isEmpty {
                        EmptyMeshState()
                    } else {
                        ForEach(topology.runners, id: \.id) { runner in
                            runnerCard(runner, nodes: topology.nodes)
                        }
                    }
                }
                .padding(16)
            }
        }
    }

    private func runnerCard(_ runner: MeshRunnerInfoDto, nodes: [MeshNodeDto]) -> some View {
        let assigned = nodes.filter { $0.runnerId == runner.id }
        return VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Image(systemName: "server.rack")
                    .foregroundStyle(AMColors.purple)
                Text(runner.name).font(AMTypography.bodySemibold)
                Spacer()
                Text(statusLabel(runner.status))
                    .font(.system(size: 11, weight: .medium))
                    .padding(.horizontal, 8).padding(.vertical, 2)
                    .background(statusColor(runner.status).opacity(0.18))
                    .foregroundStyle(statusColor(runner.status))
                    .clipShape(Capsule())
            }
            Text("\(runner.currentPods ?? Int32(assigned.count)) / \(runner.maxConcurrentPods ?? 0) pods")
                .font(.system(size: 12))
                .foregroundStyle(AMColors.mutedForeground)
            if !assigned.isEmpty {
                Divider()
                ForEach(assigned, id: \.podKey) { node in
                    HStack(spacing: 6) {
                        Circle().fill(AMColors.success).frame(width: 6, height: 6)
                        Text(node.alias ?? node.podKey)
                            .font(.system(size: 13))
                            .lineLimit(1)
                        Spacer()
                        Text(node.agentSlug)
                            .font(.system(size: 11))
                            .foregroundStyle(AMColors.mutedForeground)
                    }
                }
            }
        }
        .padding(12)
        .background(AMColors.card)
        .clipShape(RoundedRectangle(cornerRadius: AMRadius.card))
        .overlay(RoundedRectangle(cornerRadius: AMRadius.card)
            .stroke(AMColors.border, lineWidth: 1))
    }

    private func statusLabel(_ s: RunnerStatusDto) -> String {
        switch s {
        case .online: return "Online"
        case .offline: return "Offline"
        case .maintenance: return "Maintenance"
        case .unknown: return "Unknown"
        }
    }

    private func statusColor(_ s: RunnerStatusDto) -> Color {
        switch s {
        case .online: return AMColors.success
        case .offline: return AMColors.mutedForeground
        case .maintenance: return AMColors.warning
        case .unknown: return AMColors.mutedForeground
        }
    }
}

private struct EmptyMeshState: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "network.slash")
                .font(.system(size: 48))
                .foregroundStyle(AMColors.mutedForeground)
            Text("No runners online").font(AMTypography.bodySemibold)
            Text("Connect a runner to see the mesh topology.")
                .font(.system(size: 13))
                .foregroundStyle(AMColors.mutedForeground)
        }
        .padding(.top, 80)
    }
}
