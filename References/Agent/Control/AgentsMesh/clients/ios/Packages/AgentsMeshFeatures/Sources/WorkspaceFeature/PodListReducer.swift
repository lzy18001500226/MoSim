import ComposableArchitecture
import Foundation
import AgentsMeshCore
import CoreClient

@Reducer
public struct PodListFeature {
    public init() {}

    @ObservableState
    public struct State: Equatable {
        public var pods: [PodDto] = []
        public var runners: [RunnerDto] = []
        public var isLoading: Bool = false
        public var errorMessage: String?
        public var selectedPodKey: String?
        public var showingCompose: Bool = false
        public var searchQuery: String = ""

        public init() {}
    }

    public enum Action: Sendable {
        case onAppear
        case refreshRequested
        case dataLoaded(pods: [PodDto], runners: [RunnerDto])
        case loadFailed(String)
        case podTapped(String)
        case terminatePodRequested(String)
        case logoutTapped
        case avatarTapped
        case composeTapped
        case setComposeVisible(Bool)
        case searchQueryChanged(String)
        case createPodRequested(CreatePodRequestDto)
        case createPodSucceeded(PodDto)
        case createPodFailed(String)
        case delegate(Delegate)

        public enum Delegate: Equatable, Sendable {
            case openTerminal(podKey: String)
            case didLogout
            case requestDrawer
        }
    }

    @Dependency(\.coreClient) var core

    public var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .onAppear, .refreshRequested:
                state.isLoading = true
                state.errorMessage = nil
                return .run { send in
                    do {
                        async let pods = core.listPods(nil)
                        async let runners = core.listRunners()
                        let (p, r) = try await (pods, runners)
                        await send(.dataLoaded(pods: p.pods, runners: r.runners))
                    } catch let err as CoreError {
                        await send(.loadFailed(CoreErrorDescription.describe(err)))
                    } catch {
                        await send(.loadFailed(error.localizedDescription))
                    }
                }

            case .dataLoaded(let pods, let runners):
                state.isLoading = false
                state.pods = pods
                state.runners = runners
                return .none

            case .loadFailed(let message):
                state.isLoading = false
                state.errorMessage = message
                return .none

            case .podTapped(let key):
                state.selectedPodKey = key
                return .send(.delegate(.openTerminal(podKey: key)))

            case .terminatePodRequested(let key):
                return .run { send in
                    do {
                        try await core.terminatePod(key)
                        await send(.refreshRequested)
                    } catch {
                        await send(.loadFailed(error.localizedDescription))
                    }
                }

            case .logoutTapped:
                return .run { send in
                    _ = try? await core.logout()
                    await send(.delegate(.didLogout))
                }

            case .avatarTapped:
                return .send(.delegate(.requestDrawer))

            case .composeTapped:
                state.showingCompose = true
                return .none

            case .setComposeVisible(let visible):
                state.showingCompose = visible
                if !visible {
                    return .send(.refreshRequested)
                }
                return .none

            case .searchQueryChanged(let q):
                state.searchQuery = q
                return .none

            case .createPodRequested(let req):
                return .run { send in
                    do {
                        let resp = try await core.createPod(req)
                        await send(.createPodSucceeded(resp.pod))
                    } catch let err as CoreError {
                        await send(.createPodFailed(CoreErrorDescription.describe(err)))
                    } catch {
                        await send(.createPodFailed(error.localizedDescription))
                    }
                }

            case .createPodSucceeded:
                state.showingCompose = false
                return .send(.refreshRequested)

            case .createPodFailed(let msg):
                state.errorMessage = msg
                return .none

            case .delegate:
                return .none
            }
        }
    }
}
