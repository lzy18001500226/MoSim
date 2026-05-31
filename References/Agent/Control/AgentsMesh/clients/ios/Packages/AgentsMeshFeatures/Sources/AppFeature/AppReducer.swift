import ComposableArchitecture
import SwiftUI
import AuthFeature
import CoreClient
import DashboardFeature
import AgentsMeshCore

/// Root reducer — three phases: (1) loading while we try to restore a
/// Keychain-backed session, (2) login form, (3) authenticated dashboard.
@Reducer
public struct AppFeature {
    public init() {}

    @ObservableState
    public enum State: Equatable {
        case loading
        case login(LoginFeature.State)
        case dashboard(DashboardFeature.State)

        public init() { self = .loading }
    }

    public enum Action: Sendable {
        case onLaunch
        case sessionRestored(Bool)
        case login(LoginFeature.Action)
        case dashboard(DashboardFeature.Action)
    }

    @Dependency(\.coreClient) var core

    public var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .onLaunch:
                return .run { send in
                    // Bootstrap = read storage + verify token + fetch identity
                    // in one round-trip. Returns a strongly-typed
                    // BootstrapResult enum — pattern match on the variant
                    // to decide login vs dashboard.
                    let result = (try? await core.bootstrap()) ?? .anonymous
                    let restored: Bool
                    switch result {
                    case .authenticated:
                        restored = true
                        _ = try? await core.fetchOrganizations()
                    case .anonymous, .anonymousAfterCleanup:
                        restored = false
                    }
                    await send(.sessionRestored(restored))
                }

            case .sessionRestored(true):
                state = .dashboard(DashboardFeature.State())
                return .none

            case .sessionRestored(false):
                state = .login(LoginFeature.State())
                return .none

            case .login(.delegate(.didAuthenticate)):
                state = .dashboard(DashboardFeature.State())
                return .none

            case .dashboard(.delegate(.didSignOut)):
                state = .login(LoginFeature.State())
                return .none

            case .login, .dashboard:
                return .none
            }
        }
        .ifCaseLet(\.login, action: \.login) { LoginFeature() }
        .ifCaseLet(\.dashboard, action: \.dashboard) { DashboardFeature() }
    }
}
