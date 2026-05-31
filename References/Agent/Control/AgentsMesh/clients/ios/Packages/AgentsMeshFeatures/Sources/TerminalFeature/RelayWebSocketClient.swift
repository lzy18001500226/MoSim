import ComposableArchitecture
import Foundation
import AgentsMeshCore

/// Swift-owned Relay WebSocket client. The relay framing protocol is
/// implemented inline since the prior `relay_encode_*` Rust FFI was
/// removed in favor of a Swift-side implementation.
///
/// Protocol (see clients/core/crates/protocol):
///   First byte = MsgType, then payload.
///   - 0x00 Input    : payload = raw stdin bytes
///   - 0x01 Output   : payload = raw stdout bytes (server → client)
///   - 0x02 Resize   : payload = cols_be(2) + rows_be(2)
///   - 0x05 Ping     : zero-length payload (server → client)
public struct RelayWebSocketClient: Sendable {
    public var connect: @Sendable (
        _ info: PodConnectionInfoDto,
        _ podKey: String,
        _ initialCols: UInt16,
        _ initialRows: UInt16
    ) async throws -> Void
    public var sendInput: @Sendable (_ data: Data) async throws -> Void
    public var sendResize: @Sendable (_ cols: UInt16, _ rows: UInt16) async throws -> Void
    public var disconnect: @Sendable () async -> Void
}

extension RelayWebSocketClient: DependencyKey {
    public static let liveValue: RelayWebSocketClient = {
        let actor = RelaySession()
        return RelayWebSocketClient(
            connect: { info, podKey, cols, rows in
                try await actor.connect(info: info, podKey: podKey, cols: cols, rows: rows)
            },
            sendInput: { data in try await actor.sendInput(data) },
            sendResize: { cols, rows in try await actor.sendResize(cols: cols, rows: rows) },
            disconnect: { await actor.disconnect() }
        )
    }()

    public static let testValue = RelayWebSocketClient(
        connect: unimplemented("RelayWebSocketClient.connect"),
        sendInput: unimplemented("RelayWebSocketClient.sendInput"),
        sendResize: unimplemented("RelayWebSocketClient.sendResize"),
        disconnect: unimplemented("RelayWebSocketClient.disconnect", placeholder: ())
    )
}

public extension DependencyValues {
    var relayWebSocket: RelayWebSocketClient {
        get { self[RelayWebSocketClient.self] }
        set { self[RelayWebSocketClient.self] = newValue }
    }
}

private enum RelayMsgType: UInt8 {
    case input = 0x00
    case output = 0x01
    case resize = 0x02
    case ping = 0x05
}

private func encodeInput(_ data: Data) -> Data {
    var out = Data(capacity: data.count + 1)
    out.append(RelayMsgType.input.rawValue)
    out.append(data)
    return out
}

private func encodeResize(cols: UInt16, rows: UInt16) -> Data {
    var out = Data(capacity: 5)
    out.append(RelayMsgType.resize.rawValue)
    out.append(UInt8((cols >> 8) & 0xFF))
    out.append(UInt8(cols & 0xFF))
    out.append(UInt8((rows >> 8) & 0xFF))
    out.append(UInt8(rows & 0xFF))
    return out
}

actor RelaySession {
    enum RelayError: Error {
        case notConnected
        case connectionClosed(String?)
    }

    private var task: URLSessionWebSocketTask?
    private var podKey: String?
    private var readerTask: Task<Void, Never>?

    func connect(
        info: PodConnectionInfoDto,
        podKey: String,
        cols: UInt16,
        rows: UInt16
    ) async throws {
        await disconnect()
        guard var components = URLComponents(string: info.relayUrl) else {
            throw URLError(.badURL)
        }
        var queryItems = components.queryItems ?? []
        queryItems.append(URLQueryItem(name: "token", value: info.token))
        queryItems.append(URLQueryItem(name: "pod_key", value: info.podKey))
        components.queryItems = queryItems
        guard let url = components.url else { throw URLError(.badURL) }

        let session = URLSession(configuration: .default)
        let t = session.webSocketTask(with: url)
        t.resume()
        self.task = t
        self.podKey = podKey

        // Kick off the reader before sending the initial resize so we
        // don't miss the server's hello frame.
        startReader(task: t, podKey: podKey)

        try await sendResize(cols: cols, rows: rows)
    }

    func sendInput(_ data: Data) async throws {
        guard let t = task else { throw RelayError.notConnected }
        try await t.send(.data(encodeInput(data)))
    }

    func sendResize(cols: UInt16, rows: UInt16) async throws {
        guard let t = task else { throw RelayError.notConnected }
        try await t.send(.data(encodeResize(cols: cols, rows: rows)))
    }

    func disconnect() async {
        readerTask?.cancel()
        readerTask = nil
        task?.cancel(with: .goingAway, reason: nil)
        task = nil
        if let key = podKey {
            PodOutputDispatcher.shared.unregister(podKey: key)
            podKey = nil
        }
    }

    private func startReader(task: URLSessionWebSocketTask, podKey: String) {
        readerTask = Task.detached { [weak self] in
            while !Task.isCancelled {
                do {
                    let msg = try await task.receive()
                    let data: Data
                    switch msg {
                    case .data(let d): data = d
                    case .string(let s): data = Data(s.utf8)
                    @unknown default: continue
                    }
                    await self?.handleIncoming(data: data)
                } catch {
                    await self?.handleDisconnect(reason: error.localizedDescription)
                    break
                }
            }
        }
    }

    private func handleIncoming(data: Data) async {
        guard data.count >= 1, let key = podKey else { return }
        let kind = data[0]
        let payload = data.dropFirst()
        // MsgType::Output = 0x01
        if kind == RelayMsgType.output.rawValue {
            PodOutputDispatcher.shared.feed(podKey: key, data: Data(payload))
        }
        // ignore other kinds for MVP
    }

    private func handleDisconnect(reason: String?) async {
        readerTask = nil
        task = nil
    }
}
