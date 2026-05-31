import SwiftUI
import ComposableArchitecture
import AgentsMeshCore
import AppFeature

@main
struct AgentsMeshApp: App {
    init() {
        let env = ProcessInfo.processInfo.environment
        // Bootstrap Rust core once per process. Resolution order:
        //   1. AGENTSMESH_API_URL env (lets XCUITest launchEnvironment swap)
        //   2. Info.plist (build-config default)
        //   3. production fallback
        let baseURL = env["AGENTSMESH_API_URL"]
            ?? Bundle.main.object(forInfoDictionaryKey: "AGENTSMESH_API_URL") as? String
            ?? "https://api.agentsmesh.ai"

        let storage = KeychainStorage()
        // E2E hook: forces the app onto the login screen on launch
        // by wiping the keychain-backed session before bootstrap.
        if env["AGENTSMESH_RESET_SESSION"] == "1" {
            storage.clear()
        }

        CoreBridge.shared.bootstrap(baseURL: baseURL, storage: storage)
    }

    var body: some Scene {
        WindowGroup {
            AppView(store: Store(initialState: AppFeature.State()) { AppFeature() })
        }
    }
}
