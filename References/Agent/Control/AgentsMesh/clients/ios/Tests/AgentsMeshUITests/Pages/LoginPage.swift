import XCTest

/// Login screen Page Object. Selectors map to accessibility identifiers
/// set in `LoginView.swift`.
struct LoginPage {
    let app: XCUIApplication

    var emailField: XCUIElement { app.textFields["login-email"] }
    var passwordField: XCUIElement { app.secureTextFields["login-password"] }
    var submitButton: XCUIElement { app.buttons["login-submit"] }
    var errorBanner: XCUIElement { app.staticTexts["login-error"] }

    func waitForRender(timeout: TimeInterval = 10) {
        XCTAssertTrue(
            emailField.waitForExistence(timeout: timeout),
            "Login screen did not render within \(timeout)s"
        )
    }

    func login(email: String, password: String) {
        waitForRender()
        emailField.tap()
        emailField.typeText(email)
        passwordField.tap()
        passwordField.typeText(password)
        submitButton.tap()
    }

    func loginAsDevUser() {
        login(email: TestEnv.devEmail, password: TestEnv.devPassword)
    }
}
