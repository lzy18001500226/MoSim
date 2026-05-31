import SwiftUI
import AgentsMeshCore
import DesignSystem

/// 设计稿 ios-create-pod-sheet.pastel + clients/web `CreatePodForm`。
/// AgentFile (CLAUDE.md 中提到) 是 Pod 配置 SSOT — 此处把表单字段拼成
/// `AGENT/REPO/BRANCH/PROMPT` 行交给 `agentfile_layer`，service 层会 merge。
public struct CreatePodSheet: View {
    @Binding var isPresented: Bool
    let onCreate: (CreatePodRequestDto) -> Void

    @State private var agent: String = "claude-code"
    @State private var alias: String = ""
    @State private var repository: String = ""
    @State private var branch: String = "main"
    @State private var prompt: String = ""
    @State private var perpetual: Bool = false

    public init(
        isPresented: Binding<Bool>,
        onCreate: @escaping (CreatePodRequestDto) -> Void
    ) {
        self._isPresented = isPresented
        self.onCreate = onCreate
    }

    private var canSubmit: Bool {
        !repository.isEmpty && !prompt.isEmpty
    }

    public var body: some View {
        VStack(spacing: 0) {
            AMSheetHeader(
                title: "New Pod",
                cancelLabel: "Cancel",
                saveLabel: "Create",
                saveEnabled: canSubmit,
                onCancel: { isPresented = false },
                onSave: submit
            )
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    AMSectionHeader("Agent")
                    agentPicker
                    AMSectionHeader("Alias (optional)")
                    field("my-feature-pod", $alias)
                    AMSectionHeader("Repository")
                    field("dev-org/demo-api", $repository)
                        .accessibilityIdentifier("compose-repository")
                    AMSectionHeader("Branch")
                    field("main", $branch)
                    AMSectionHeader("Prompt")
                    promptInput
                    perpetualToggle
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 24)
            }
        }
        .background(AMColors.groupedBg)
    }

    private func submit() {
        let req = CreatePodRequestDto(
            agentSlug: agent,
            agentfileLayer: buildAgentfileLayer(
                agent: agent,
                repo: repository.trimmingCharacters(in: .whitespaces),
                branch: branch.isEmpty ? "main" : branch,
                prompt: prompt
            ),
            runnerId: nil,
            alias: alias.isEmpty ? nil : alias,
            ticketSlug: nil,
            cols: nil,
            rows: nil,
            sourcePodKey: nil,
            resumeAgentSession: nil,
            perpetual: perpetual ? true : nil
        )
        onCreate(req)
        isPresented = false
    }

    private var agentPicker: some View {
        HStack(spacing: 8) {
            agentChip("claude-code", color: AMColors.success)
            agentChip("codex", color: AMColors.primary)
            agentChip("aider", color: AMColors.warning)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(AMColors.card)
        .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
    }

    private func agentChip(_ name: String, color: Color) -> some View {
        Button { agent = name } label: {
            HStack(spacing: 6) {
                Circle().fill(color).frame(width: 8, height: 8)
                Text(name)
                    .font(.system(size: 13, weight: agent == name ? .semibold : .medium, design: .monospaced))
                    .foregroundStyle(AMColors.foreground)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(agent == name ? AMColors.primarySoft : AMColors.groupedBg)
            .clipShape(RoundedRectangle(cornerRadius: AMRadius.buttonSm))
        }
        .buttonStyle(.plain)
    }

    private func field(_ placeholder: String, _ binding: Binding<String>) -> some View {
        TextField(placeholder, text: binding)
            .font(AMTypography.body)
            .autocorrectionDisabled(true)
            .textInputAutocapitalization(.never)
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(AMColors.card)
            .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
    }

    private var promptInput: some View {
        TextEditor(text: $prompt)
            .font(.system(size: 13, design: .monospaced))
            .frame(minHeight: 120)
            .padding(8)
            .background(AMColors.card)
            .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
            .accessibilityIdentifier("compose-prompt")
            .overlay(alignment: .topLeading) {
                if prompt.isEmpty {
                    Text("Plan and implement the Redis migration…")
                        .font(.system(size: 13, design: .monospaced))
                        .foregroundStyle(AMColors.mutedForeground)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 16)
                        .allowsHitTesting(false)
                }
            }
    }

    private var perpetualToggle: some View {
        Toggle(isOn: $perpetual) {
            VStack(alignment: .leading, spacing: 2) {
                Text("Perpetual pod").font(AMTypography.body)
                Text("Auto-restart on exit; survives crashes")
                    .font(.system(size: 12))
                    .foregroundStyle(AMColors.mutedForeground)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(AMColors.card)
        .clipShape(RoundedRectangle(cornerRadius: AMRadius.cell))
    }
}

/// AgentFile DSL minimum-viable layer: 用户表单字段拼成行，service 层 merge
/// agent 默认配置。
func buildAgentfileLayer(agent: String, repo: String, branch: String, prompt: String) -> String {
    let escapedPrompt = prompt.replacingOccurrences(of: "\"\"\"", with: "'''")
    return """
    AGENT \"\(agent)\"
    REPO \"\(repo)\"
    BRANCH \"\(branch)\"
    PROMPT \"\"\"
    \(escapedPrompt)
    \"\"\"
    """
}
