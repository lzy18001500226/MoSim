import XCTest

/// Org drawer Page Object. The drawer slides in from the leading edge
/// when any tab's nav-bar avatar is tapped.
struct OrgDrawerPage {
    let app: XCUIApplication

    var signOutButton: XCUIElement { app.buttons["drawer-signout"] }

    func waitForVisible(timeout: TimeInterval = 5) {
        XCTAssertTrue(
            signOutButton.waitForExistence(timeout: timeout),
            "Org drawer did not slide in within \(timeout)s"
        )
    }

    func signOut() {
        waitForVisible()
        signOutButton.tap()
    }
}
