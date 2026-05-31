import SwiftUI
import WebKit

/// Embeds a WKWebView that loads the web React bundle's
/// `/blocks-embed/{blockId}?wsId=...` page. All Rust-core service calls
/// inside the WebView go via `webkit.messageHandlers.amBridge` and land
/// in the `Coordinator` here, which dispatches to a native
/// `IosRpcRoute` (typically `BlockstoreRpcRoute`).
///
/// Single Rust core instance shared across the iOS app — no second
/// WebSocket, no second auth token, no duplicated cache.
public struct BlockDetailWebView: UIViewRepresentable {
    let workspaceId: String
    let blockId: String
    let route: IosRpcRoute

    public init(workspaceId: String, blockId: String, route: IosRpcRoute) {
        self.workspaceId = workspaceId
        self.blockId = blockId
        self.route = route
    }

    public func makeCoordinator() -> Coordinator {
        Coordinator(route: route)
    }

    public func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.userContentController.add(context.coordinator, name: "amBridge")
        // Inject a flag *before* any page JS runs so `WasmProvider`
        // (root layout) can detect embed mode and skip its own platform
        // init in favour of ours.
        let initJs = "window.__amEmbedMode = 'ios';"
        let initScript = WKUserScript(
            source: initJs,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: false
        )
        config.userContentController.addUserScript(initScript)

        let view = WKWebView(frame: .zero, configuration: config)
        context.coordinator.webView = view

        let url = embedURL(workspaceId: workspaceId, blockId: blockId)
        view.load(URLRequest(url: url))
        return view
    }

    public func updateUIView(_ view: WKWebView, context: Context) {}

    public final class Coordinator: NSObject, WKScriptMessageHandler {
        let route: IosRpcRoute
        weak var webView: WKWebView?

        init(route: IosRpcRoute) { self.route = route }

        public func userContentController(
            _ ucc: WKUserContentController,
            didReceive message: WKScriptMessage
        ) {
            guard let body = message.body as? [String: Any],
                  let id = body["id"] as? Int,
                  let method = body["method"] as? String else { return }
            let args = body["args"] as? [String: Any] ?? [:]
            Task { [weak self] in
                guard let self else { return }
                do {
                    let result = try await self.route.dispatch(method: method, args: args)
                    self.resolve(id: id, result: result ?? NSNull())
                } catch {
                    self.reject(id: id, error: error.localizedDescription)
                }
            }
        }

        @MainActor
        private func resolve(id: Int, result: Any) {
            evaluateResolve(id: id, payload: ["result": result])
        }

        @MainActor
        private func reject(id: Int, error: String) {
            evaluateResolve(id: id, payload: ["error": error])
        }

        @MainActor
        private func evaluateResolve(id: Int, payload: [String: Any]) {
            guard let data = try? JSONSerialization.data(withJSONObject: payload),
                  let json = String(data: data, encoding: .utf8) else { return }
            webView?.evaluateJavaScript("window.__amResolve(\(id), \(json))",
                                        completionHandler: nil)
        }
    }
}

/// Resolution order for the web base URL:
///   1. `AGENTSMESH_WEB_URL` env (XCUITest launchEnvironment override)
///   2. `AGENTSMESH_WEB_URL` Info.plist key
///   3. Derived from `AGENTSMESH_API_URL` by swapping the port to the
///      well-known dev web port (worktree-allocated, see deploy/dev/.env)
///   4. Production fallback `https://app.agentsmesh.ai`
private func resolveWebBaseURL() -> URL {
    let env = ProcessInfo.processInfo.environment
    let candidate = env["AGENTSMESH_WEB_URL"]
        ?? (Bundle.main.object(forInfoDictionaryKey: "AGENTSMESH_WEB_URL") as? String)
    if let s = candidate, let u = URL(string: s) { return u }

    if let api = env["AGENTSMESH_API_URL"]
        ?? (Bundle.main.object(forInfoDictionaryKey: "AGENTSMESH_API_URL") as? String),
       let derived = deriveWebURL(fromApiURL: api) {
        return derived
    }
    return URL(string: "https://app.agentsmesh.ai")!
}

private func deriveWebURL(fromApiURL api: String) -> URL? {
    guard var comps = URLComponents(string: api) else { return nil }
    if comps.host == "localhost" || comps.host == "127.0.0.1" {
        // Dev convention: API on `HTTP_PORT`, web on `HTTP_PORT + 7`
        // (see deploy/dev/.env — 25350 → 25357 for the main worktree).
        let apiPort = comps.port ?? 80
        comps.port = apiPort + 7
    }
    return comps.url
}

private func embedURL(workspaceId: String, blockId: String) -> URL {
    var comps = URLComponents(url: resolveWebBaseURL(), resolvingAgainstBaseURL: false)!
    comps.path = "/blocks-embed/\(blockId)"
    comps.queryItems = [URLQueryItem(name: "wsId", value: workspaceId)]
    return comps.url!
}
