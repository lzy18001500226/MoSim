import ComposableArchitecture
import Foundation
import AgentsMeshCore
import CoreClient

@Reducer
public struct LoginFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable {
        public var email: String = ""
        public var password: String = ""
        public var isSubmitting: Bool = false
        public var errorMessage: String?

        public init() {}

        var canSubmit: Bool {
            !email.isEmpty && !password.isEmpty && !isSubmitting
        }
    }

    public enum Action: BindableAction, Sendable {
        case binding(BindingAction<State>)
        case submitTapped
        case loginSucceeded(AuthSessionDto)
        case loginFailed(String)
        /// Emitted to the parent reducer (AppFeature) after a successful
        /// login so it can transition to the dashboard.
        case delegate(Delegate)

        public enum Delegate: Equatable, Sendable {
            case didAuthenticate
        }
    }

    @Dependency(\.coreClient) var core

    public var body: some ReducerOf<Self> {
        BindingReducer()
        Reduce { state, action in
            switch action {
            case .binding:
                return .none

            case .submitTapped:
                guard state.canSubmit else { return .none }
                state.isSubmitting = true
                state.errorMessage = nil
                let email = state.email
                let password = state.password
                return .run { send in
                    do {
                        let session = try await core.login(email, password)
                        _ = try? await core.fetchOrganizations()
                        await send(.loginSucceeded(session))
                    } catch let err as CoreError {
                        await send(.loginFailed(Self.describe(err)))
                    } catch {
                        await send(.loginFailed(error.localizedDescription))
                    }
                }

            case .loginSucceeded:
                state.isSubmitting = false
                state.password = ""
                return .send(.delegate(.didAuthenticate))

            case .loginFailed(let message):
                state.isSubmitting = false
                state.errorMessage = message
                return .none

            case .delegate:
                return .none
            }
        }
    }

    public static func describe(_ err: CoreError) -> String {
        CoreErrorDescription.describe(err)
    }
}
