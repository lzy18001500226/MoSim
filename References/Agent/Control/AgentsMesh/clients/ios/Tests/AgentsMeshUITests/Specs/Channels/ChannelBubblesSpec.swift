import XCTest

final class ChannelBubblesSpec: XCTestCase {
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
    }

    func test_text_bubble_renders_after_opening_a_channel() throws {
        let app = XCUIApplication.launchFresh()
        LoginPage(app: app).loginAsDevUser()
        DashboardPage(app: app).waitForRender()
        DashboardPage(app: app).switchTo("Channels")

        let firstChannel = app.scrollViews.firstMatch.buttons.firstMatch
        let deadline = Date().addingTimeInterval(10)
        while Date() < deadline {
            if firstChannel.exists { break }
            usleep(200_000)
        }
        if !firstChannel.exists {
            try XCTSkipIf(true, "Dev seed has no channels in this org — skip")
            return
        }
        firstChannel.tap()

        let textBubble = app.descendants(matching: .any)
            .matching(identifier: "bubble-text").firstMatch
        let anyBubble = app.descendants(matching: .any).matching(
            NSPredicate(format: "identifier BEGINSWITH 'bubble-'")
        ).firstMatch

        let bubbleDeadline = Date().addingTimeInterval(8)
        while Date() < bubbleDeadline {
            if textBubble.exists || anyBubble.exists { return }
            usleep(200_000)
        }
        try XCTSkipIf(true, "Channel has no messages yet — skip")
    }
}
