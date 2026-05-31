import SwiftUI

/// Design tokens — iOS 26 / Lark visual language. Mirrors
/// `design/mobile/tokens/*.pastel`.
public enum AMColors {
    // Surfaces
    public static let background = Color(red: 0.98, green: 0.98, blue: 0.98)       // #FAFAFA
    public static let groupedBg = Color(red: 0.949, green: 0.949, blue: 0.969)     // #F2F2F7 — iOS systemGroupedBg
    public static let card = Color.white
    public static let glass85 = Color.white.opacity(0.85)                          // Liquid Glass

    // Text
    public static let foreground = Color(red: 0.122, green: 0.137, blue: 0.157)    // #1F2328
    public static let mutedForeground = Color(red: 0.557, green: 0.557, blue: 0.576) // #8E8E93
    public static let secondaryText = Color(red: 0.396, green: 0.427, blue: 0.463) // #656D76

    // Border / divider
    public static let border = Color(red: 0.894, green: 0.914, blue: 0.933)        // #E4E9EE
    public static let borderStrong = Color(red: 0.816, green: 0.843, blue: 0.871)  // #D0D7DE
    public static let separator = Color(red: 0.949, green: 0.949, blue: 0.969)     // #F2F2F7

    // Brand
    public static let primary = Color(red: 0.035, green: 0.412, blue: 0.855)       // #0969DA
    public static let primaryForeground = Color.white
    public static let primarySoft = Color(red: 0.866, green: 0.957, blue: 1.0)     // #DDF4FF
    public static let primaryStrong = Color(red: 0.020, green: 0.314, blue: 0.682) // #0550AE

    // Status
    public static let success = Color(red: 0.247, green: 0.729, blue: 0.314)       // #3FB950
    public static let successSoft = Color(red: 0.855, green: 0.984, blue: 0.882)   // #DAFBE1
    public static let successText = Color(red: 0.102, green: 0.498, blue: 0.216)   // #1A7F37
    public static let warning = Color(red: 0.824, green: 0.600, blue: 0.133)       // #D29922
    public static let warningSoft = Color(red: 1.0, green: 0.973, blue: 0.773)     // #FFF8C5
    public static let warningText = Color(red: 0.604, green: 0.404, blue: 0.0)     // #9A6700
    public static let destructive = Color(red: 0.812, green: 0.133, blue: 0.180)   // #CF222E
    public static let destructiveSoft = Color(red: 1.0, green: 0.922, blue: 0.914) // #FFEBE9
    public static let purple = Color(red: 0.435, green: 0.259, blue: 0.757)        // #6F42C1
    public static let codeBg = Color(red: 0.051, green: 0.067, blue: 0.090)        // #0D1117
    public static let codeText = Color(red: 0.788, green: 0.820, blue: 0.851)      // #C9D1D9
}

public enum AMSpacing {
    public static let xxs: CGFloat = 2
    public static let xs: CGFloat = 4
    public static let s: CGFloat = 8
    public static let m: CGFloat = 12
    public static let l: CGFloat = 16
    public static let xl: CGFloat = 24
    public static let xxl: CGFloat = 32
}

/// iOS 26 corner radius ladder.
public enum AMRadius {
    public static let chip: CGFloat = 4
    public static let buttonSm: CGFloat = 8
    public static let s: CGFloat = 6
    public static let m: CGFloat = 8
    public static let cell: CGFloat = 12
    public static let card: CGFloat = 16
    public static let l: CGFloat = 12
    public static let sheet: CGFloat = 22
    public static let capsule: CGFloat = 28
    public static let full: CGFloat = 999
}

public enum AMShadow {
    public static let floatingLow = (radius: CGFloat(12), y: CGFloat(4), opacity: 0.08)
    public static let floatingMed = (radius: CGFloat(24), y: CGFloat(8), opacity: 0.12)
    public static let floatingHigh = (radius: CGFloat(32), y: CGFloat(12), opacity: 0.16)
    public static let cardSubtle = (radius: CGFloat(2), y: CGFloat(1), opacity: 0.04)
}

public enum AMTypography {
    public static let largeTitle = Font.system(size: 34, weight: .bold)
    public static let title = Font.system(size: 28, weight: .bold)
    public static let title2 = Font.system(size: 22, weight: .semibold)
    public static let heading = Font.system(size: 20, weight: .semibold)
    public static let navTitle = Font.system(size: 17, weight: .semibold)
    public static let body = Font.system(size: 15)
    public static let bodyMedium = Font.system(size: 15, weight: .medium)
    public static let bodySemibold = Font.system(size: 15, weight: .semibold)
    public static let footnote = Font.system(size: 13)
    public static let caption = Font.system(size: 12)
    public static let captionMono = Font.system(size: 11, weight: .medium, design: .monospaced)
    public static let mono = Font.system(size: 14, design: .monospaced)
    public static let monoSm = Font.system(size: 12, design: .monospaced)
}
