import XCTest

final class BlocksPagesSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_pages_tree_populates_from_dev_workspace() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()
        DashboardPage(app: app).switchTo("Blocks")

        let predicate = NSPredicate(format: "identifier BEGINSWITH 'page-row-'")
        let firstPage = app.descendants(matching: .any).matching(predicate).firstMatch
        XCTAssertTrue(
            firstPage.waitForExistence(timeout: 10),
            "Blocks pages tree shows no page-row-* entries despite dev seed having 'nest' refs"
        )
    }
}
