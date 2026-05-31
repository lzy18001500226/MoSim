import SwiftUI

/// Avatar — circular (users) or rounded-square (pods/orgs). Mirrors
/// `design/mobile/components/avatar.pastel`.
public struct AMAvatar: View {
    public enum Shape { case circle, roundedSquare }
    public enum Size { case xs, sm, md, lg, xl
        var dimension: CGFloat {
            switch self {
            case .xs: return 24
            case .sm: return 32
            case .md: return 40
            case .lg: return 56
            case .xl: return 80
            }
        }
        var fontSize: CGFloat {
            switch self {
            case .xs: return 11
            case .sm: return 14
            case .md: return 17
            case .lg: return 22
            case .xl: return 32
            }
        }
    }

    let letter: String
    let shape: Shape
    let size: Size
    let bg: Color
    let mono: Bool

    public init(_ letter: String, shape: Shape = .circle, size: Size = .md, bg: Color = AMColors.primary, mono: Bool = false) {
        self.letter = letter
        self.shape = shape
        self.size = size
        self.bg = bg
        self.mono = mono
    }

    public var body: some View {
        let radius: CGFloat = shape == .circle ? size.dimension / 2 : 8
        return Text(letter)
            .font(mono
                ? .system(size: size.fontSize, weight: .semibold, design: .monospaced)
                : .system(size: size.fontSize, weight: .semibold))
            .foregroundStyle(.white)
            .frame(width: size.dimension, height: size.dimension)
            .background(bg)
            .clipShape(RoundedRectangle(cornerRadius: radius))
    }
}
