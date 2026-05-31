import XCTest

/// Verifies the iOS embed mode for block detail: tapping a page row in
/// the Blocks tab pushes a `BlockDetailWebView` (WKWebView) that loads
/// `/blocks-embed/{blockId}` from the local web dev server, with all
/// `blockstoreService` calls round-tripping through the native
/// `BlockstoreRpcRoute`.
///
/// The spec is gated on the dev web server being reachable —
/// `AGENTSMESH_WEB_URL` must point to a running Next.js instance (the
/// CI workflow boots `bazel run //clients/web:next_dev` alongside the
/// backend). When unreachable the test skips rather than fails so this
/// suite stays green on environments that only run the backend.
final class BlockDetailWebViewSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_tapping_page_loads_embedded_webview() throws {
        try skipIfWebUnreachable()

        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()
        DashboardPage(app: app).switchTo("Blocks")

        // Tap the first page row in the tree.
        let rowPredicate = NSPredicate(format: "identifier BEGINSWITH 'page-row-'")
        let firstRow = app.descendants(matching: .any).matching(rowPredicate).firstMatch
        XCTAssertTrue(
            firstRow.waitForExistence(timeout: 10),
            "Blocks pages tree empty — cannot test BlockDetailWebView"
        )
        firstRow.tap()

        // WKWebView reports its embedded content under .webView. Wait for
        // any descendant text to appear — proves navigation happened, the
        // embed URL loaded, and the React bundle rendered something.
        let webView = app.webViews.firstMatch
        XCTAssertTrue(
            webView.waitForExistence(timeout: 20),
            "WKWebView never attached — embed URL likely failed to load"
        )

        // Any non-empty text descendant signals the React render landed.
        let anyText = webView.staticTexts.firstMatch
        XCTAssertTrue(
            anyText.waitForExistence(timeout: 25),
            "WebView attached but no text rendered — RPC bridge or DocumentView failed"
        )
    }

    /// Probe the dev web server with a short timeout. Skipping is the
    /// right call when it's down: the rest of the suite doesn't depend
    /// on web, and surfacing the skip explicitly keeps signal high.
    private func skipIfWebUnreachable() throws {
        guard let url = URL(string: TestEnv.webURL) else {
            throw XCTSkip("AGENTSMESH_WEB_URL invalid: \(TestEnv.webURL)")
        }
        var req = URLRequest(url: url)
        req.timeoutInterval = 2
        req.httpMethod = "HEAD"
        let exp = expectation(description: "web reachable")
        var ok = false
        URLSession.shared.dataTask(with: req) { _, resp, _ in
            if let http = resp as? HTTPURLResponse, http.statusCode < 500 { ok = true }
            exp.fulfill()
        }.resume()
        wait(for: [exp], timeout: 3)
        if !ok { throw XCTSkip("Web dev server unreachable at \(TestEnv.webURL)") }
    }
}
