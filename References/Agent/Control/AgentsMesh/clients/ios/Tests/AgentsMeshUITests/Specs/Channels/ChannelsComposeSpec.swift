import XCTest

/// Channels compose flow — tapping the "+" button in the nav bar
/// should surface a "create channel" sheet. Currently the action is
/// dispatched but DashboardFeature treats `requestCompose` as a no-op,
/// so this spec fails until the sheet is wired.
final class ChannelsComposeSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_compose_button_opens_create_sheet() throws {
        // KNOWN BROKEN: + button dispatches `requestCompose` but
        // DashboardFeature treats it as a no-op. Implement the
        // ChannelComposeFeature (reducer + sheet view) and remove
        // this skip.
        try XCTSkipIf(true, "Channel compose sheet not implemented yet")

        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()
        DashboardPage(app: app).switchTo("Channels")

        let compose = app.buttons["nav-compose"]
        XCTAssertTrue(compose.waitForExistence(timeout: 5))
        compose.tap()

        let createButton = app.buttons["Create"]
        let cancelButton = app.buttons["Cancel"]
        let nameField = app.textFields["compose-channel-name"]

        let deadline = Date().addingTimeInterval(3)
        while Date() < deadline {
            if createButton.exists || cancelButton.exists || nameField.exists {
                return
            }
            usleep(200_000)
        }
        XCTFail("Compose sheet did not present after tapping +")
    }
}
