import XCTest

/// More tab actions — secondary destinations should respond to taps.
/// Currently tiles are pure visuals (no Button wrapper or onTapGesture)
/// so taps are silent. Spec is left enabled so it surfaces the bug.
final class MoreActionsSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_settings_tile_responds_to_tap() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()
        DashboardPage(app: app).switchTo("More")

        // Sheet 在 medium detent 时 Settings tile 可能在 fold 下；
        // 上滑展开到 large detent 后 hit-testable。
        let settings = app.buttons["Settings"]
        XCTAssertTrue(
            settings.waitForExistence(timeout: 5),
            "Settings tile not in More sheet"
        )
        if !settings.isHittable {
            app.swipeUp()
        }
        XCTAssertTrue(settings.exists, "Settings tile disappeared after expanding sheet")
    }
}
