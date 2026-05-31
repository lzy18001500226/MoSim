import SwiftUI

/// Bottom-sheet header — grabber + cancel/title/save row. Mirrors
/// `design/mobile/components/sheet-header.pastel`.
public struct AMSheetHeader: View {
    let title: String
    let cancelLabel: String
    let saveLabel: String
    let saveEnabled: Bool
    let onCancel: () -> Void
    let onSave: () -> Void

    public init(
        title: String,
        cancelLabel: String = "Cancel",
        saveLabel: String = "Save",
        saveEnabled: Bool = true,
        onCancel: @escaping () -> Void,
        onSave: @escaping () -> Void
    ) {
        self.title = title
        self.cancelLabel = cancelLabel
        self.saveLabel = saveLabel
        self.saveEnabled = saveEnabled
        self.onCancel = onCancel
        self.onSave = onSave
    }

    public var body: some View {
        VStack(spacing: 0) {
            // Grabber
            Capsule()
                .fill(Color(red: 0.78, green: 0.78, blue: 0.80))
                .frame(width: 36, height: 5)
                .padding(.top, 6)
                .padding(.bottom, 8)

            HStack {
                Button(cancelLabel, action: onCancel)
                    .font(.system(size: 17))
                    .foregroundStyle(AMColors.primary)
                Spacer()
                Text(title)
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundStyle(AMColors.foreground)
                Spacer()
                Button(saveLabel, action: onSave)
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundStyle(saveEnabled ? AMColors.primary : AMColors.mutedForeground)
                    .disabled(!saveEnabled)
            }
            .padding(.horizontal, 16)
            .frame(height: 44)
        }
        .background(AMColors.card)
    }
}

/// Lightweight sheet grabber — for sheets that don't need an action header.
public struct AMSheetGrabber: View {
    public init() {}
    public var body: some View {
        Capsule()
            .fill(Color(red: 0.78, green: 0.78, blue: 0.80))
            .frame(width: 36, height: 5)
            .padding(.top, 6)
            .padding(.bottom, 8)
            .frame(maxWidth: .infinity)
    }
}
