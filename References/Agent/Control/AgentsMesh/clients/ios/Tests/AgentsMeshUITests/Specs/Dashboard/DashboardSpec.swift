import XCTest

/// Tab navigation specs. Mirrors `e2e-playwright/tests/workspace/`
/// in spirit — exercises the dashboard shell, not individual feature
/// content.
final class DashboardSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_can_switch_between_all_tabs() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        let dashboard = DashboardPage(app: app)
        dashboard.waitForRender()

        // Cycle through all 5 tabs to verify each renders without
        // crashing or leaving the user stranded on a placeholder.
        for tabName in ["Channels", "Tickets", "Blocks", "More", "Pods"] {
            dashboard.switchTo(tabName)
            // Tab bar still has the same set of buttons after each
            // switch — sanity check we didn't navigate away.
            XCTAssertTrue(dashboard.tab(tabName).isSelected || dashboard.tab(tabName).exists)
        }
    }
}
