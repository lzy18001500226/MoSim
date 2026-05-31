import XCTest

extension XCUIApplication {
    /// Launch the host app pointing at the dev backend with a clean
    /// keychain. Equivalent to playwright's `await browser.newContext()`
    /// + `await page.goto('/')` — every test gets a fresh session by
    /// default. Pass `resetSession: false` to exercise the
    /// session-restore code path.
    static func launchFresh(
        apiURL: String = TestEnv.apiURL,
        webURL: String = TestEnv.webURL,
        resetSession: Bool = true
    ) -> XCUIApplication {
        let app = XCUIApplication()
        app.launchEnvironment["AGENTSMESH_API_URL"] = apiURL
        app.launchEnvironment["AGENTSMESH_WEB_URL"] = webURL
        if resetSession {
            app.launchEnvironment["AGENTSMESH_RESET_SESSION"] = "1"
        }
        app.launch()
        return app
    }
}
