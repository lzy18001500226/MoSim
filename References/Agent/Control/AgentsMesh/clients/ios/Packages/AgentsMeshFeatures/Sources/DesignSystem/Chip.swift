import SwiftUI

/// Tag chip — `design/mobile/components/chip.pastel`. Used for status
/// pills, label tags, "外部" / "机器人" badges.
public struct AMChip: View {
    public enum Variant {
        case running, executing, idle, done, todo, inReview, backlog
        case label(fg: Color, bg: Color)
        case neutral
        case primary

        var fg: Color {
            switch self {
            case .running, .done: return AMColors.successText
            case .executing: return AMColors.primaryStrong
            case .idle, .neutral, .backlog: return AMColors.secondaryText
            case .todo: return AMColors.primaryStrong
            case .inReview: return AMColors.purple
            case .label(let fg, _): return fg
            case .primary: return AMColors.primaryStrong
            }
        }
        var bg: Color {
            switch self {
            case .running, .done: return AMColors.successSoft
            case .executing, .todo, .primary: return AMColors.primarySoft
            case .idle, .neutral, .backlog: return Color(red: 0.941, green: 0.953, blue: 0.965)
            case .inReview: return Color(red: 0.949, green: 0.918, blue: 0.992)
            case .label(_, let bg): return bg
            }
        }
    }

    let text: String
    let variant: Variant
    let dot: Bool

    public init(_ text: String, variant: Variant = .neutral, dot: Bool = false) {
        self.text = text
        self.variant = variant
        self.dot = dot
    }

    public var body: some View {
        HStack(spacing: 4) {
            if dot {
                Circle()
                    .fill(variant.fg)
                    .frame(width: 6, height: 6)
            }
            Text(text)
                .font(.system(size: 11, weight: .medium))
                .foregroundStyle(variant.fg)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 2)
        .background(variant.bg)
        .clipShape(RoundedRectangle(cornerRadius: AMRadius.chip))
    }
}
