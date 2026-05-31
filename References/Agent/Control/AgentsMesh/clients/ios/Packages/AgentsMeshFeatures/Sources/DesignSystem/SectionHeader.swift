import SwiftUI

/// Section header — UPPERCASE muted label with optional + button.
/// Mirrors `design/mobile/components/section-header.pastel` and the
/// "PAGES" / "INDICATOR TYPES" headers in BlocksSidebar.
public struct AMSectionHeader: View {
    let label: String
    let onAdd: (() -> Void)?

    public init(_ label: String, onAdd: (() -> Void)? = nil) {
        self.label = label
        self.onAdd = onAdd
    }

    public var body: some View {
        HStack(alignment: .bottom) {
            Text(label.uppercased())
                .font(.system(size: 11, weight: .semibold))
                .tracking(1.5)
                .foregroundStyle(AMColors.mutedForeground)
            Spacer()
            if let onAdd {
                Button(action: onAdd) {
                    Image(systemName: "plus")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(AMColors.mutedForeground)
                        .frame(width: 24, height: 24)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 16)
        .padding(.top, 10)
        .padding(.bottom, 4)
        .frame(height: 32)
    }
}
