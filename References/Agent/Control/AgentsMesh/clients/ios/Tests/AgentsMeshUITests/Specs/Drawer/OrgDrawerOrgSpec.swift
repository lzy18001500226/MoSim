import XCTest

/// Org drawer organisation switcher — the dev seed user belongs to at
/// least one org, so the drawer's left rail should display at least
/// one org avatar. If the drawer fetch never resolves the rail will
/// be empty.
final class OrgDrawerOrgSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_drawer_displays_at_least_one_org() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()
        DashboardPage(app: app).switchTo("Channels")
        ChannelsListPage(app: app).openDrawer()
        OrgDrawerPage(app: app).waitForVisible()

        let predicate = NSPredicate(format: "identifier BEGINSWITH 'drawer-org-'")
        let orgItem = app.buttons.matching(predicate).firstMatch
        XCTAssertTrue(
            orgItem.waitForExistence(timeout: 5),
            "Org drawer rail shows no organisation entries (expected at least one drawer-org-* button)"
        )
    }
}
