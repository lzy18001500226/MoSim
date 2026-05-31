import SwiftUI

/// Tab bar 5-tab IA. Used by Dashboard's TabView. SF Symbols map
/// 1:1 to the lucide icons in the pastel mockups; iOS 26 renders
/// the floating capsule tab bar automatically.
public enum AMTab: String, CaseIterable, Hashable, Sendable {
    case pods, channels, tickets, blocks, more

    public var label: String {
        switch self {
        case .pods: return "Pods"
        case .channels: return "Channels"
        case .tickets: return "Tickets"
        case .blocks: return "Blocks"
        case .more: return "More"
        }
    }

    /// SF Symbol name. Filled variant is preferred when active; iOS
    /// `.tabItem` uses the active state automatically when selected.
    public var symbol: String {
        switch self {
        case .pods: return "terminal.fill"
        case .channels: return "bubble.left.and.bubble.right.fill"
        case .tickets: return "ticket.fill"
        case .blocks: return "square.stack.3d.up.fill"
        case .more: return "ellipsis"
        }
    }
}
