import SwiftUI
import DesignSystem

/// Bottom composer mirroring Lark — full-width input pill + 6 tool icons
/// + send button. From `design/mobile/pages/ios-channel-detail.pastel`.
public struct ChannelComposer: View {
    let placeholder: String
    @Binding var text: String
    let isSending: Bool
    let onSend: () -> Void

    public init(placeholder: String, text: Binding<String>, isSending: Bool, onSend: @escaping () -> Void) {
        self.placeholder = placeholder
        self._text = text
        self.isSending = isSending
        self.onSend = onSend
    }

    public var body: some View {
        VStack(spacing: 12) {
            // Input row — pill style, expand icon on the right
            HStack(spacing: 8) {
                TextField(placeholder, text: $text, axis: .vertical)
                    .font(AMTypography.body)
                    .lineLimit(1...4)
                Image(systemName: "arrow.up.left.and.arrow.down.right")
                    .font(.system(size: 16))
                    .foregroundStyle(AMColors.mutedForeground)
            }
            .padding(.horizontal, 14)
            .frame(minHeight: 40)
            .background(AMColors.groupedBg)
            .clipShape(Capsule())

            // Toolbar — 6 tool icons + send
            HStack {
                HStack(spacing: 4) {
                    toolButton("face.smiling")
                    toolButton("at")
                    toolButton("photo")
                    toolButton("mic")
                    toolButton("textformat")
                    toolButton("plus")
                }
                Spacer()
                Button(action: onSend) {
                    if isSending {
                        ProgressView().tint(.white)
                            .frame(width: 36, height: 36)
                    } else {
                        Image(systemName: "arrow.up")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundStyle(.white)
                            .frame(width: 36, height: 36)
                    }
                }
                .background(text.trimmingCharacters(in: .whitespaces).isEmpty
                    ? AMColors.mutedForeground.opacity(0.3) : AMColors.primary)
                .clipShape(Circle())
                .disabled(text.trimmingCharacters(in: .whitespaces).isEmpty || isSending)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(AMColors.card)
    }

    private func toolButton(_ symbol: String) -> some View {
        Button {
        } label: {
            Image(systemName: symbol)
                .font(.system(size: 22))
                .foregroundStyle(AMColors.foreground)
                .frame(width: 36, height: 36)
        }
        .buttonStyle(.plain)
    }
}
