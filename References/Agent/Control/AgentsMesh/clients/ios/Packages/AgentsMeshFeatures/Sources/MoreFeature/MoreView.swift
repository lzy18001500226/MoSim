import SwiftUI
import DesignSystem

/// Top-level destinations behind the More tab. No "settings" here —
/// settings live in the org drawer's avatar menu, not here.
public enum MoreDestination: String, Hashable, CaseIterable, Identifiable {
    case mesh, loops, repositories, runners, help

    public var id: String { rawValue }

    public var label: String {
        switch self {
        case .mesh: return "Mesh"
        case .loops: return "Loops"
        case .repositories: return "Repositories"
        case .runners: return "Runners"
        case .help: return "Help"
        }
    }

    public var symbol: String {
        switch self {
        case .mesh: return "network"
        case .loops: return "repeat"
        case .repositories: return "folder.fill"
        case .runners: return "server.rack"
        case .help: return "questionmark.circle.fill"
        }
    }

    public var tint: Color {
        switch self {
        case .mesh: return AMColors.primary
        case .loops: return AMColors.success
        case .repositories: return AMColors.warning
        case .runners: return AMColors.purple
        case .help: return AMColors.destructive
        }
    }
}

public struct MoreView: View {
    public init() {}

    public var body: some View {
        ZStack {
            AMColors.groupedBg.ignoresSafeArea()
            ScrollView {
                LazyVGrid(
                    columns: [GridItem(.flexible()), GridItem(.flexible()),
                              GridItem(.flexible()), GridItem(.flexible())],
                    spacing: 20
                ) {
                    ForEach(MoreDestination.allCases) { d in
                        NavigationLink(value: d) { tile(d) }
                            .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 24)
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("More")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(for: MoreDestination.self) { d in
            MoreDestinationView(destination: d)
        }
    }

    private func tile(_ d: MoreDestination) -> some View {
        VStack(spacing: 8) {
            Image(systemName: d.symbol)
                .font(.system(size: 28))
                .foregroundStyle(d.tint)
                .frame(width: 64, height: 64)
                .background(AMColors.card)
                .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
                .overlay(RoundedRectangle(cornerRadius: AMRadius.cell)
                    .stroke(AMColors.border, lineWidth: 1))
            Text(d.label)
                .font(.system(size: 12))
                .foregroundStyle(AMColors.foreground)
                .multilineTextAlignment(.center)
                .lineLimit(1)
        }
        .accessibilityIdentifier(d.label)
    }
}
