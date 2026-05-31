import XCTest

/// More tab 是半层 sheet，不是 page。
final class MoreSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_more_tab_presents_sheet_with_destinations() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        let dashboard = DashboardPage(app: app)
        dashboard.waitForRender()
        dashboard.switchTo("More")

        let candidates = ["Mesh", "Loops", "Repositories", "Runners", "Settings", "Help"]
        let deadline = Date().addingTimeInterval(10)
        while Date() < deadline {
            for label in candidates where app.staticTexts[label].exists || app.buttons[label].exists {
                return
            }
            usleep(200_000)
        }
        XCTFail("More tab shows none of: \(candidates.joined(separator: ", "))")
    }
}
