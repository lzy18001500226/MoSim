import XCTest

/// Dashboard Page Object. The 5 tabs use SwiftUI's TabView with
/// system-rendered tab bar items, so XCUITest queries them by their
/// visible label rather than an accessibility identifier.
struct DashboardPage {
    let app: XCUIApplication

    var tabBar: XCUIElement { app.tabBars.firstMatch }
    func tab(_ name: String) -> XCUIElement { tabBar.buttons[name] }

    func waitForRender(timeout: TimeInterval = 15) {
        XCTAssertTrue(
            tab("Pods").waitForExistence(timeout: timeout),
            "Dashboard did not render within \(timeout)s"
        )
    }

    func switchTo(_ tabName: String) {
        let target = tab(tabName)
        XCTAssertTrue(target.exists, "Tab '\(tabName)' is not visible")
        target.tap()
    }
}
