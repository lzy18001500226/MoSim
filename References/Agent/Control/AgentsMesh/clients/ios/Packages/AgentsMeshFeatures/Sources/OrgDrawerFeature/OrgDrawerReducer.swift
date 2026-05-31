import ComposableArchitecture
import Foundation
import AgentsMeshCore
import CoreClient

@Reducer
public struct OrgDrawerFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable {
        public var organizations: [OrganizationDto] = []
        public var currentOrgSlug: String?
        public var isLoading: Bool = false
        public var errorMessage: String?

        public init() {}
    }

    public enum Action: Sendable {
        case onAppear
        case orgsLoaded([OrganizationDto], currentSlug: String?)
        case loadFailed(String)
        case orgTapped(slug: String)
        case signOutTapped
        case delegate(Delegate)

        public enum Delegate: Equatable, Sendable {
            case dismiss
            case didSignOut
        }
    }

    @Dependency(\.coreClient) var core

    public var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .onAppear:
                state.isLoading = true
                return .run { send in
                    do {
                        let orgs = try await core.fetchOrganizations()
                        let cur = core.currentOrg()?.slug
                        await send(.orgsLoaded(orgs, currentSlug: cur))
                    } catch {
                        await send(.loadFailed(error.localizedDescription))
                    }
                }

            case .orgsLoaded(let orgs, let cur):
                state.isLoading = false
                state.organizations = orgs
                state.currentOrgSlug = cur
                return .none

            case .loadFailed(let m):
                state.isLoading = false
                state.errorMessage = m
                return .none

            case .orgTapped(let slug):
                let s = slug
                return .run { send in
                    try? core.switchOrg(s)
                    await send(.delegate(.dismiss))
                }

            case .signOutTapped:
                return .run { send in
                    _ = try? await core.logout()
                    await send(.delegate(.didSignOut))
                }

            case .delegate:
                return .none
            }
        }
    }
}
