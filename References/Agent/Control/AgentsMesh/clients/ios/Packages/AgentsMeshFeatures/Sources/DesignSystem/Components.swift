import SwiftUI

#if canImport(UIKit)
import UIKit
public typealias AMKeyboardType = UIKeyboardType
#else
public enum AMKeyboardType { case `default`, emailAddress, URL }
#endif

/// Primary call-to-action button, matched to the web `<Button>` primary variant.
public struct AMPrimaryButton: View {
    let title: String
    let isLoading: Bool
    let action: () -> Void

    public init(_ title: String, isLoading: Bool = false, action: @escaping () -> Void) {
        self.title = title
        self.isLoading = isLoading
        self.action = action
    }

    public var body: some View {
        Button(action: action) {
            HStack {
                if isLoading { ProgressView().tint(AMColors.primaryForeground) }
                Text(title).font(AMTypography.body.weight(.medium))
            }
            .frame(maxWidth: .infinity, minHeight: 44)
            .background(AMColors.primary)
            .foregroundStyle(AMColors.primaryForeground)
            .clipShape(RoundedRectangle(cornerRadius: AMRadius.m))
        }
        .disabled(isLoading)
    }
}

/// Low-emphasis secondary button used beside a primary CTA.
public struct AMSecondaryButton: View {
    let title: String
    let action: () -> Void

    public init(_ title: String, action: @escaping () -> Void) {
        self.title = title
        self.action = action
    }

    public var body: some View {
        Button(action: action) {
            Text(title)
                .font(AMTypography.body)
                .frame(maxWidth: .infinity, minHeight: 44)
                .foregroundStyle(AMColors.foreground)
                .overlay(
                    RoundedRectangle(cornerRadius: AMRadius.m)
                        .stroke(AMColors.border, lineWidth: 1)
                )
        }
    }
}

/// Labeled text field used across auth screens.
public struct AMTextField: View {
    let title: String
    let placeholder: String
    @Binding var text: String
    let isSecure: Bool
    let keyboard: AMKeyboardType

    public init(
        title: String,
        placeholder: String = "",
        text: Binding<String>,
        isSecure: Bool = false,
        keyboard: AMKeyboardType = .default
    ) {
        self.title = title
        self.placeholder = placeholder
        self._text = text
        self.isSecure = isSecure
        self.keyboard = keyboard
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: AMSpacing.xs) {
            Text(title).font(AMTypography.caption).foregroundStyle(AMColors.mutedForeground)
            Group {
                if isSecure {
                    SecureField(placeholder, text: $text)
                } else {
                    TextField(placeholder, text: $text)
                        #if canImport(UIKit)
                        .keyboardType(keyboard)
                        .textInputAutocapitalization(.never)
                        #endif
                        .autocorrectionDisabled(true)
                }
            }
            .font(AMTypography.body)
            .padding(AMSpacing.m)
            .background(AMColors.card)
            .overlay(
                RoundedRectangle(cornerRadius: AMRadius.m)
                    .stroke(AMColors.border, lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: AMRadius.m))
        }
    }
}

/// Card container used for list rows and empty states.
public struct AMCard<Content: View>: View {
    let content: () -> Content

    public init(@ViewBuilder content: @escaping () -> Content) {
        self.content = content
    }

    public var body: some View {
        content()
            .padding(AMSpacing.l)
            .background(AMColors.card)
            .clipShape(RoundedRectangle(cornerRadius: AMRadius.m))
            .overlay(
                RoundedRectangle(cornerRadius: AMRadius.m)
                    .stroke(AMColors.border, lineWidth: 1)
            )
    }
}
