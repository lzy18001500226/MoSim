import SwiftUI

/// List cell — left icon + title (+ optional subtitle) + right meta /
/// chevron. Mirrors `design/mobile/components/list-cell.pastel`. Three
/// height presets matching iOS HIG: 44pt single-line, 60pt two-line,
/// 76pt rich (avatar + meta).
public struct AMListCell<Leading: View, Trailing: View>: View {
    public enum Height: CGFloat { case single = 44, dual = 60, rich = 76 }

    let title: String
    let subtitle: String?
    let height: Height
    let leading: () -> Leading
    let trailing: () -> Trailing

    public init(
        title: String,
        subtitle: String? = nil,
        height: Height = .dual,
        @ViewBuilder leading: @escaping () -> Leading = { EmptyView() },
        @ViewBuilder trailing: @escaping () -> Trailing = { EmptyView() }
    ) {
        self.title = title
        self.subtitle = subtitle
        self.height = height
        self.leading = leading
        self.trailing = trailing
    }

    public var body: some View {
        HStack(spacing: 12) {
            leading()
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.system(size: 17))
                    .foregroundStyle(AMColors.foreground)
                if let subtitle {
                    Text(subtitle)
                        .font(.system(size: 13))
                        .foregroundStyle(AMColors.mutedForeground)
                }
            }
            Spacer(minLength: 0)
            trailing()
        }
        .padding(.horizontal, 16)
        .frame(height: height.rawValue)
        .background(AMColors.card)
    }
}

/// Convenience for the right-side chevron.
public struct AMChevron: View {
    public init() {}
    public var body: some View {
        Image(systemName: "chevron.right")
            .font(.system(size: 14, weight: .medium))
            .foregroundStyle(Color(red: 0.78, green: 0.78, blue: 0.80))
    }
}
