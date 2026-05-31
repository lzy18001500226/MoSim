import XCTest

final class TicketDetailSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_detail_shows_full_metadata_and_spawn_button() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()
        DashboardPage(app: app).switchTo("Tickets")

        let predicate = NSPredicate(format: "identifier BEGINSWITH 'ticket-card-'")
        let firstCard = app.descendants(matching: .any).matching(predicate).firstMatch
        XCTAssertTrue(firstCard.waitForExistence(timeout: 10), "No ticket card visible on board")
        firstCard.tap()

        XCTAssertTrue(
            app.staticTexts["DETAILS"].waitForExistence(timeout: 5),
            "Ticket detail missing DETAILS section header"
        )
        XCTAssertTrue(app.staticTexts["LINKED PODS"].exists, "Missing LINKED PODS section")
        XCTAssertTrue(app.buttons["ticket-spawn-pod"].exists, "Missing Spawn Pod CTA")
    }
}
