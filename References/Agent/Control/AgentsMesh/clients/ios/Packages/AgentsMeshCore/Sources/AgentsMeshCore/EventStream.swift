import Foundation

/// Typed projection of `EventCallback.onEvent(eventJson:)` payloads.
/// The Rust side emits a tagged JSON blob; we parse into an enum here
/// so SwiftUI features never deal with raw JSON.
public enum CoreEvent: Sendable {
    case podStatusChanged(podKey: String, status: String)
    case channelMessage(channelId: Int64, messageJson: String)
    case ticketUpdated(slug: String)
    case autopilotAwaitingApproval(key: String)
    case unknown(kind: String, payload: String)
}

/// Bridge a UniFFI `EventCallback` to a Swift `AsyncStream<CoreEvent>`.
/// TCA reducers subscribe via `EventStream.shared.events` inside an
/// `Effect.run { for await ev in stream { ... } }` block.
public final class EventStream: @unchecked Sendable {
    public static let shared = EventStream()

    private let (stream, continuation): (AsyncStream<CoreEvent>, AsyncStream<CoreEvent>.Continuation)

    private init() {
        var cont: AsyncStream<CoreEvent>.Continuation!
        self.stream = AsyncStream { cont = $0 }
        self.continuation = cont
    }

    public var events: AsyncStream<CoreEvent> { stream }

    /// Callback handle to register with the Rust core.
    public lazy var callback: EventCallback = DispatchCallback(forwardTo: self.continuation)

    fileprivate final class DispatchCallback: EventCallback, @unchecked Sendable {
        private let yield: (CoreEvent) -> Void

        init(forwardTo continuation: AsyncStream<CoreEvent>.Continuation) {
            self.yield = { continuation.yield($0) }
        }

        func onEvent(eventJson: String) {
            yield(Self.parse(eventJson))
        }

        static func parse(_ json: String) -> CoreEvent {
            guard
                let data = json.data(using: .utf8),
                let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let kind = obj["kind"] as? String
            else { return .unknown(kind: "parse_error", payload: json) }
            switch kind {
            case "pod_status_changed":
                return .podStatusChanged(
                    podKey: obj["pod_key"] as? String ?? "",
                    status: obj["status"] as? String ?? ""
                )
            case "channel_message":
                return .channelMessage(
                    channelId: (obj["channel_id"] as? NSNumber)?.int64Value ?? 0,
                    messageJson: json
                )
            case "ticket_updated":
                return .ticketUpdated(slug: obj["slug"] as? String ?? "")
            case "autopilot_awaiting_approval":
                return .autopilotAwaitingApproval(key: obj["key"] as? String ?? "")
            default:
                return .unknown(kind: kind, payload: json)
            }
        }
    }
}
