import XCTest

/// Org drawer specs — covers the slide-in animation, sign-out flow.
final class DrawerSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_avatar_tap_opens_drawer() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()

        // Default tab is Pods — its toolbar has the nav-avatar Button.
        let channels = ChannelsListPage(app: app)
        DashboardPage(app: app).switchTo("Channels")
        channels.openDrawer()

        OrgDrawerPage(app: app).waitForVisible()
    }

    func test_sign_out_returns_to_login() throws {
        let app = XCUIApplication.launchFresh()
        let login = LoginPage(app: app)
        login.loginAsDevUser()
        DashboardPage(app: app).waitForRender()

        DashboardPage(app: app).switchTo("Channels")
        ChannelsListPage(app: app).openDrawer()
        OrgDrawerPage(app: app).signOut()

        // Login email field reappears once we're back on the auth screen.
        XCTAssertTrue(
            login.emailField.waitForExistence(timeout: 10),
            "Did not return to login screen after sign-out"
        )
    }
}
