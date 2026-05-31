import SwiftUI

/// CTA buttons — iOS 26 large 52pt with 12pt corner radius. Mirrors
/// `design/mobile/components/cta-button.pastel`. The legacy 44pt
/// `AMPrimaryButton` lives in Components.swift for compact use.
public struct AMLargeCTAButton: View {
    public enum Variant { case primary, secondary, destructive }

    let title: String
    let variant: Variant
    let isLoading: Bool
    let action: () -> Void

    public init(
        _ title: String,
        variant: Variant = .primary,
        isLoading: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.variant = variant
        self.isLoading = isLoading
        self.action = action
    }

    public var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView().tint(textColor)
                }
                Text(title)
                    .font(.system(size: 17, weight: .semibold))
            }
            .foregroundStyle(textColor)
            .frame(maxWidth: .infinity, minHeight: 52)
            .background(bg)
            .overlay(
                RoundedRectangle(cornerRadius: AMRadius.l)
                    .stroke(strokeColor, lineWidth: variant == .secondary ? 1 : 0)
            )
            .clipShape(RoundedRectangle(cornerRadius: AMRadius.l))
        }
        .disabled(isLoading)
    }

    private var bg: Color {
        switch variant {
        case .primary: return AMColors.primary
        case .secondary: return AMColors.card
        case .destructive: return AMColors.destructive
        }
    }
    private var textColor: Color {
        switch variant {
        case .primary, .destructive: return .white
        case .secondary: return AMColors.foreground
        }
    }
    private var strokeColor: Color {
        variant == .secondary ? AMColors.border : .clear
    }
}
