import SwiftUI

/// iOS-style segmented control. Mirrors `design/mobile/components/segment.pastel`.
/// Compact 30pt height for use inside nav bars.
public struct AMSegmentedControl<Tag: Hashable>: View {
    let segments: [(label: String, tag: Tag)]
    @Binding var selection: Tag
    let compact: Bool

    public init(_ segments: [(label: String, tag: Tag)], selection: Binding<Tag>, compact: Bool = false) {
        self.segments = segments
        self._selection = selection
        self.compact = compact
    }

    public var body: some View {
        HStack(spacing: 0) {
            ForEach(segments, id: \.tag) { seg in
                Button {
                    selection = seg.tag
                } label: {
                    Text(seg.label)
                        .font(.system(size: 13, weight: selection == seg.tag ? .semibold : .medium))
                        .foregroundStyle(AMColors.foreground)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, compact ? 3 : 4)
                        .background(
                            ZStack {
                                if selection == seg.tag {
                                    RoundedRectangle(cornerRadius: 6)
                                        .fill(.white)
                                        .shadow(color: .black.opacity(0.06), radius: 1, y: 1)
                                }
                            }
                        )
                }
                .buttonStyle(.plain)
            }
        }
        .padding(2)
        .background(Color(red: 0.914, green: 0.914, blue: 0.922))
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .frame(height: compact ? 30 : 32)
    }
}
