import XCTest

/// Pods feature specs. Default view is the Lark-style time-sorted list
/// with a Mine/Others/Completed segment.
final class PodsSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_pods_tab_renders_segment_filter() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        let dashboard = DashboardPage(app: app)
        dashboard.waitForRender()
        // Default tab is Pods; switch away then back to ensure render.
        dashboard.switchTo("Channels")
        dashboard.switchTo("Pods")

        for segment in ["Mine", "Others", "Completed"] {
            XCTAssertTrue(
                app.buttons[segment].waitForExistence(timeout: 10),
                "Pods segment '\(segment)' missing"
            )
        }
    }

    func test_pods_tab_shows_list_or_empty_state() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()

        // Either a populated list or the empty state is acceptable; the
        // failure mode this guards against is a blank/crashing view.
        let empty = app.staticTexts["No pods"]
        let any = app.scrollViews.firstMatch
        let deadline = Date().addingTimeInterval(10)
        while Date() < deadline {
            if empty.exists || any.exists { return }
            usleep(200_000)
        }
        XCTFail("Pods tab rendered neither list nor empty state")
    }
}
