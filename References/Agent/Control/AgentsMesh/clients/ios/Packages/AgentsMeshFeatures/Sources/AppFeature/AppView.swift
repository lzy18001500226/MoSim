import ComposableArchitecture
import SwiftUI
import AuthFeature
import DashboardFeature
import DesignSystem

/// Root SwiftUI view dispatching on `AppFeature.State`. Thin —
/// delegates the heavy lifting to LoginView / DashboardView.
public struct AppView: View {
    @Perception.Bindable var store: StoreOf<AppFeature>

    public init(store: StoreOf<AppFeature>) { self.store = store }

    public var body: some View {
        Group {
            switch store.state {
            case .loading:
                ProgressView().controlSize(.large).tint(AMColors.primary)
            case .login:
                if let loginStore = store.scope(state: \.login, action: \.login) {
                    LoginView(store: loginStore)
                }
            case .dashboard:
                if let dashStore = store.scope(state: \.dashboard, action: \.dashboard) {
                    DashboardView(store: dashStore)
                }
            }
        }
        .onAppear { store.send(.onLaunch) }
    }
}
