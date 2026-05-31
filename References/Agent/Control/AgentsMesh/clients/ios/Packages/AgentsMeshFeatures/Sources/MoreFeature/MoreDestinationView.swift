import SwiftUI
import ComposableArchitecture
import AgentsMeshCore
import CoreClient
import DesignSystem

/// Routes a `MoreDestination` to its concrete view. Each destination
/// fetches its own data via `CoreClient` on appear; loading + error
/// states are handled by `LoadingState` so the views stay declarative.
struct MoreDestinationView: View {
    let destination: MoreDestination

    var body: some View {
        Group {
            switch destination {
            case .mesh: MeshView()
            case .loops: LoopsView()
            case .repositories: RepositoriesView()
            case .runners: RunnersView()
            case .help: HelpView()
            }
        }
        .navigationTitle(destination.label)
        .navigationBarTitleDisplayMode(.inline)
        .accessibilityIdentifier("more-detail-\(destination.rawValue)")
    }
}

/// Generic load-once container — async fetch runs on appear, retries on
/// pull-to-refresh, and surfaces a typed error rather than leaving the
/// view blank if the backend rejects the request.
struct LoadingState<Value, Content: View>: View {
    let load: @Sendable () async throws -> Value
    @ViewBuilder let content: (Value) -> Content

    @State private var value: Value?
    @State private var error: String?

    var body: some View {
        ZStack {
            AMColors.groupedBg.ignoresSafeArea()
            if let value {
                content(value)
            } else if let error {
                errorView(error)
            } else {
                ProgressView().controlSize(.large)
            }
        }
        .task { await fetch() }
        .refreshable { await fetch() }
    }

    @MainActor
    private func fetch() async {
        do { value = try await load(); error = nil }
        catch { self.error = (error as? LocalizedError)?.errorDescription ?? "\(error)" }
    }

    private func errorView(_ msg: String) -> some View {
        VStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 32))
                .foregroundStyle(AMColors.destructive)
            Text("Failed to load")
                .font(AMTypography.bodySemibold)
            Text(msg).font(.system(size: 13))
                .foregroundStyle(AMColors.mutedForeground)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
        }
    }
}
