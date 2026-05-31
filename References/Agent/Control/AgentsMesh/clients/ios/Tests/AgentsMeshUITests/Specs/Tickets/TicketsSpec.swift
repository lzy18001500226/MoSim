import XCTest

/// Tickets feature specs. Default mode is Board (5-column Kanban).
final class TicketsSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_board_renders_five_status_columns() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        let dashboard = DashboardPage(app: app)
        dashboard.waitForRender()
        dashboard.switchTo("Tickets")

        for slug in ["backlog", "todo", "in-progress", "in-review", "done"] {
            let id = "board-column-\(slug)"
            let header = app.descendants(matching: .any).matching(identifier: id).firstMatch
            XCTAssertTrue(
                header.waitForExistence(timeout: 10),
                "Board column '\(id)' missing"
            )
        }
    }

    func test_can_switch_to_list_mode() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()
        DashboardPage(app: app).switchTo("Tickets")

        let listSegment = app.buttons["List"]
        XCTAssertTrue(listSegment.waitForExistence(timeout: 5), "List segment missing")
        listSegment.tap()
        let backlogHeader = app.descendants(matching: .any)
            .matching(identifier: "board-column-backlog").firstMatch
        let deadline = Date().addingTimeInterval(2)
        while Date() < deadline {
            if !backlogHeader.exists { return }
            usleep(200_000)
        }
        XCTFail("Board column header still visible after switching to List")
    }
}
