import XCTest

final class PodsComposeSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_plus_button_opens_create_pod_sheet() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()

        let compose = app.buttons["nav-compose"]
        if !compose.exists {
            XCTAssertTrue(
                app.buttons.matching(NSPredicate(format: "label == 'New Pod' OR label == '+'"))
                    .firstMatch.waitForExistence(timeout: 5),
                "Pods + button missing"
            )
        }
        compose.firstMatch.tap()

        let cancel = app.buttons["Cancel"]
        let create = app.buttons["Create"]
        let newPodTitle = app.staticTexts["New Pod"]
        let deadline = Date().addingTimeInterval(5)
        while Date() < deadline {
            if cancel.exists || create.exists || newPodTitle.exists { return }
            usleep(200_000)
        }
        XCTFail("CreatePodSheet did not present after tapping +")
    }
}
