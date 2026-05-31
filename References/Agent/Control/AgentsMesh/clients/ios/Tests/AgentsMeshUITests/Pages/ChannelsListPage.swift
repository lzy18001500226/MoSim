import XCTest

/// Channels list Page Object. Cells render as rows; the nav-bar avatar
/// is wired to the org drawer.
struct ChannelsListPage {
    let app: XCUIApplication

    var navAvatar: XCUIElement { app.buttons["nav-avatar"] }
    var emptyStateTitle: XCUIElement { app.staticTexts["No channels yet"] }
    var firstRow: XCUIElement { app.scrollViews.firstMatch.cells.firstMatch }

    /// Either the empty state or a populated scroll view appears once
    /// the initial fetch resolves; both signal "list rendered".
    func waitForLoaded(timeout: TimeInterval = 10) {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            if emptyStateTitle.exists || app.scrollViews.firstMatch.exists {
                return
            }
            usleep(200_000)
        }
        XCTFail("Channels list did not render within \(timeout)s")
    }

    func openDrawer() {
        XCTAssertTrue(navAvatar.waitForExistence(timeout: 5))
        navAvatar.tap()
    }
}
