import SwiftUI
import DesignSystem

/// Help page — links to docs and quick reference. Static content, no
/// network calls. Intentionally lightweight: most help is web-based.
struct HelpView: View {
    var body: some View {
        ZStack {
            AMColors.groupedBg.ignoresSafeArea()
            ScrollView {
                LazyVStack(spacing: 8) {
                    section("Documentation") {
                        link("Getting started",
                             URL(string: "https://agentsmesh.ai/docs/getting-started")!)
                        link("Concepts: Pod / Agent / Loop",
                             URL(string: "https://agentsmesh.ai/docs/concepts")!)
                        link("FAQ", URL(string: "https://agentsmesh.ai/docs/faq")!)
                    }
                    section("Reference") {
                        link("AgentFile DSL",
                             URL(string: "https://agentsmesh.ai/docs/agentfile")!)
                        link("CLI commands",
                             URL(string: "https://agentsmesh.ai/docs/cli")!)
                    }
                    section("Support") {
                        link("Report an issue",
                             URL(string: "https://github.com/agentsmesh/agentsmesh/issues")!)
                        link("Email support",
                             URL(string: "mailto:support@agentsmesh.ai")!)
                    }
                }
                .padding(16)
            }
        }
    }

    @ViewBuilder
    private func section(_ title: String,
                         @ViewBuilder content: () -> some View) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title.uppercased())
                .font(.system(size: 11, weight: .semibold))
                .foregroundStyle(AMColors.mutedForeground)
                .padding(.horizontal, 12)
                .padding(.top, 12)
                .padding(.bottom, 4)
            VStack(spacing: 0) { content() }
                .background(AMColors.card)
                .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
                .overlay(RoundedRectangle(cornerRadius: AMRadius.cell)
                    .stroke(AMColors.border, lineWidth: 1))
        }
    }

    private func link(_ label: String, _ url: URL) -> some View {
        Link(destination: url) {
            HStack(spacing: 8) {
                Text(label).font(.system(size: 14))
                    .foregroundStyle(AMColors.foreground)
                Spacer()
                Image(systemName: "arrow.up.right.square")
                    .font(.system(size: 12))
                    .foregroundStyle(AMColors.mutedForeground)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 12)
            .contentShape(Rectangle())
        }
        .overlay(alignment: .bottom) {
            Rectangle().fill(AMColors.border).frame(height: 0.5)
                .padding(.leading, 12)
        }
    }
}
