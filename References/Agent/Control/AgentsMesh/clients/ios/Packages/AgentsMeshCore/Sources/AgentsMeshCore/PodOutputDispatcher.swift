import Foundation

/// Central fan-out for terminal byte streams.
///
/// Rust side emits `OutputCallback.onOutput(pod_key, data)` for every chunk
/// that lands over the relay WebSocket. We register a single callback with
/// the core and dispatch to the currently-attached `TerminalView` by
/// `podKey`. Performance-critical path — we bypass TCA reducer's
/// Action/Effect machinery to avoid per-byte overhead.
public final class PodOutputDispatcher: @unchecked Sendable {
    public static let shared = PodOutputDispatcher()

    public typealias Sink = @Sendable (Data) -> Void

    private var sinks: [String: Sink] = [:]
    private let lock = NSLock()

    private init() {}

    public func register(podKey: String, sink: @escaping Sink) {
        lock.lock(); defer { lock.unlock() }
        sinks[podKey] = sink
    }

    public func unregister(podKey: String) {
        lock.lock(); defer { lock.unlock() }
        sinks.removeValue(forKey: podKey)
    }

    /// Entry point from the Rust callback. Must be fast and non-blocking —
    /// it runs on whatever thread the WebSocket reader uses.
    public func feed(podKey: String, data: Data) {
        lock.lock()
        let sink = sinks[podKey]
        lock.unlock()
        sink?(data)
    }

    /// The UniFFI-conformant callback handle registered with the Rust core.
    public lazy var callback: OutputCallback = Callback(dispatcher: self)

    fileprivate final class Callback: OutputCallback, @unchecked Sendable {
        private weak var dispatcher: PodOutputDispatcher?
        init(dispatcher: PodOutputDispatcher) { self.dispatcher = dispatcher }

        func onOutput(podKey: String, data: Data) {
            dispatcher?.feed(podKey: podKey, data: data)
        }
    }
}
