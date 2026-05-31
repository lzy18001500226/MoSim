import XCTest

/// Channels feature specs. Mirrors `e2e-playwright/tests/channels/`
/// shape — keeps each spec focused on one observable.
final class ChannelsListSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_channels_tab_renders_list_or_empty_state() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        let dashboard = DashboardPage(app: app)
        dashboard.waitForRender()

        dashboard.switchTo("Channels")
        ChannelsListPage(app: app).waitForLoaded()
    }
}
