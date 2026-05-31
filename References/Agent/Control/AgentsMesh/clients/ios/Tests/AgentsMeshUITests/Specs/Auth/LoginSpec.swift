import XCTest

/// Authentication flow specs. Mirrors `e2e-playwright/tests/auth/`.
final class LoginSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_valid_credentials_lands_on_dashboard() throws {
        let app = XCUIApplication.launchFresh()
        let login = LoginPage(app: app)
        let dashboard = DashboardPage(app: app)

        login.loginAsDevUser()
        dashboard.waitForRender()

        for tabName in ["Pods", "Channels", "Tickets", "Blocks", "More"] {
            XCTAssertTrue(
                dashboard.tab(tabName).exists,
                "Tab '\(tabName)' missing on dashboard"
            )
        }
    }

    func test_invalid_credentials_shows_error() throws {
        let app = XCUIApplication.launchFresh()
        let login = LoginPage(app: app)

        login.login(email: "wrong@example.com", password: "wrongpass")
        XCTAssertTrue(
            login.errorBanner.waitForExistence(timeout: 10),
            "Error banner did not appear after invalid login"
        )
    }
}
