import SwiftUI
import DesignSystem

/// Generic empty-state placeholder for list views. Avoids duplicating
/// the icon + title + detail layout across each MoreDestination view.
struct EmptyState: View {
    let symbol: String
    let title: String
    let detail: String

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: symbol)
                .font(.system(size: 48))
                .foregroundStyle(AMColors.mutedForeground)
            Text(title).font(AMTypography.bodySemibold)
            Text(detail).font(.system(size: 13))
                .foregroundStyle(AMColors.mutedForeground)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
