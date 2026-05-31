import Foundation

/// Test-runner-side environment. Mirrors `helpers/env.ts` on web/desktop:
/// resolves the dev backend URL + canonical seed credentials.
enum TestEnv {
    /// Backend origin the host app should hit. Override via env var on
    /// the test runner (e.g. CI may inject a worktree-specific port).
    /// Defaults to the local `deploy/dev` HTTP_PORT for the main worktree.
    static let apiURL: String = {
        if let url = ProcessInfo.processInfo.environment["AGENTSMESH_API_URL"],
           !url.isEmpty {
            return url
        }
        return "http://localhost:25350"
    }()

    /// Web dev server origin used by iOS embed mode (`/blocks-embed/*`).
    /// Worktree convention: `WEB_PORT = HTTP_PORT + 7` (deploy/dev/.env).
    static let webURL: String = {
        if let url = ProcessInfo.processInfo.environment["AGENTSMESH_WEB_URL"],
           !url.isEmpty {
            return url
        }
        return "http://localhost:25357"
    }()

    /// Dev seed user (created by `deploy/dev/init-seed.sh`).
    static let devEmail = "dev@agentsmesh.local"
    static let devPassword = "devpass123"
}
