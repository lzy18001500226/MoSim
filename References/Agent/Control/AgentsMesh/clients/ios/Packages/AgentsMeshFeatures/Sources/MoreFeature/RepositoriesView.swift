import SwiftUI
import ComposableArchitecture
import AgentsMeshCore
import CoreClient
import DesignSystem

/// Repositories — connected git repos for the active org.
struct RepositoriesView: View {
    @Dependency(\.coreClient) private var core

    var body: some View {
        LoadingState(load: { try await core.listRepositories() }) { resp in
            if resp.repositories.isEmpty {
                EmptyState(
                    symbol: "folder",
                    title: "No repositories",
                    detail: "Connect a git provider (GitLab / GitHub / Gitea) to add repos."
                )
            } else {
                ScrollView {
                    LazyVStack(spacing: 8) {
                        ForEach(resp.repositories, id: \.id) { row($0) }
                    }
                    .padding(16)
                }
            }
        }
    }

    private func row(_ repo: RepositoryDto) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 8) {
                Image(systemName: "folder.fill")
                    .foregroundStyle(AMColors.warning)
                Text(repo.name).font(AMTypography.bodySemibold)
                Spacer()
                if let v = repo.visibility, !v.isEmpty {
                    Text(v.capitalized)
                        .font(.system(size: 11, weight: .medium))
                        .padding(.horizontal, 8).padding(.vertical, 2)
                        .background(AMColors.mutedForeground.opacity(0.18))
                        .foregroundStyle(AMColors.mutedForeground)
                        .clipShape(Capsule())
                }
            }
            if let slug = repo.slug, !slug.isEmpty {
                Text(slug).font(.system(size: 12))
                    .foregroundStyle(AMColors.mutedForeground)
                    .lineLimit(1)
            }
            HStack(spacing: 12) {
                if let p = repo.providerType, !p.isEmpty {
                    metaChip("link", p)
                }
                if let b = repo.defaultBranch, !b.isEmpty {
                    metaChip("arrow.triangle.branch", b)
                }
                if let prefix = repo.ticketPrefix, !prefix.isEmpty {
                    metaChip("number", prefix)
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
