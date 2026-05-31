import AgentsMeshCore

/// Map a `CoreError` (UniFFI-generated enum from Rust) to a
/// user-facing string. Lives next to `CoreClient` because every
/// reducer that surfaces errors needs it; placing it here avoids
/// having business features depend on AuthFeature for a single helper.
public enum CoreErrorDescription {
    public static func describe(_ err: CoreError) -> String {
        switch err {
        case .AuthExpired: return "Session expired"
        case .Http(_, _, let message): return message
        case .Network(let message): return "Network: \(message)"
        case .InvalidJson(let message): return "Invalid response: \(message)"
        case .NotFound(let resource, _): return "\(resource) not found"
        case .NotConnected: return "Not connected"
        case .Unknown(let message): return message
        }
    }
}
