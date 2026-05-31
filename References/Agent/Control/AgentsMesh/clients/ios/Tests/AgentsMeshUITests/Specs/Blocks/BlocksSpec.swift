import XCTest

/// Blocks feature specs. Tab shows a recursive PAGES tree backed by
/// the Rust blockstore.
final class BlocksSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_blocks_tab_renders_pages_section() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        let dashboard = DashboardPage(app: app)
        dashboard.waitForRender()
        dashboard.switchTo("Blocks")

        // PAGES section header is part of the BlocksTreeView template;
        // it should be visible regardless of whether the workspace is
        // empty or populated.
        XCTAssertTrue(
            app.staticTexts["PAGES"].waitForExistence(timeout: 10),
            "Blocks tab missing the PAGES section header"
        )
    }
}
