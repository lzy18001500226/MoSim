import ComposableArchitecture
import SwiftUI
import DesignSystem

public struct LoginView: View {
    @Perception.Bindable var store: StoreOf<LoginFeature>

    public init(store: StoreOf<LoginFeature>) {
        self.store = store
    }

    public var body: some View {
        ZStack {
            AMColors.background.ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: AMSpacing.l) {
                    header
                    form
                    if let error = store.errorMessage {
                        Text(error)
                            .font(AMTypography.caption)
                            .foregroundStyle(AMColors.destructive)
                            .accessibilityIdentifier("login-error")
                    }
                    submit
                    Spacer(minLength: AMSpacing.xxl)
                }
                .padding(.horizontal, AMSpacing.l)
                .padding(.top, AMSpacing.xxl)
                .frame(maxWidth: 480)
            }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: AMSpacing.xs) {
            Text("AgentsMesh").font(AMTypography.title)
            Text("Sign in to your account")
                .font(AMTypography.body)
                .foregroundStyle(AMColors.mutedForeground)
        }
    }

    private var form: some View {
        VStack(spacing: AMSpacing.m) {
            AMTextField(
                title: "Email",
                placeholder: "you@example.com",
                text: $store.email,
                keyboard: .emailAddress
            )
            .accessibilityIdentifier("login-email")
            AMTextField(
                title: "Password",
                text: $store.password,
                isSecure: true
            )
            .accessibilityIdentifier("login-password")
        }
    }

    private var submit: some View {
        AMPrimaryButton("Sign in", isLoading: store.isSubmitting) {
            store.send(.submitTapped)
        }
        .accessibilityIdentifier("login-submit")
    }
}
