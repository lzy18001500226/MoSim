// swift-tools-version: 5.9
//
// External Swift packages consumed by AgentsMesh. This file is **not** an
// SPM target layout — it's only a declaration of SPM deps that
// `rules_swift_package_manager` reads to generate `@swiftpkg_<name>`
// Bazel repos.
//
// Runtime app targets live in `clients/ios/` and declare their own
// `swift_library` BUILD targets that depend on these packages by name:
//
//     @swiftpkg_swift_composable_architecture//:ComposableArchitecture
//     @swiftpkg_swiftterm//:SwiftTerm
import PackageDescription

let package = Package(
    name: "ThirdLibraries",
    platforms: [.iOS(.v16)],
    dependencies: [
        .package(
            url: "https://github.com/pointfreeco/swift-composable-architecture",
            exact: "1.15.2"
        ),
        // Pin to a version that does NOT pull in swift-sharing (introduced
        // in 2.8.0). 2.7.x is the last 2.x that works without it.
        .package(
            url: "https://github.com/pointfreeco/swift-navigation",
            exact: "2.7.0"
        ),
        // Pin SwiftTerm to 1.2.x — the 1.5.x release reshaped
        // TerminalViewDelegate / UIViewRepresentable bindings.
        .package(
            url: "https://github.com/migueldeicaza/SwiftTerm",
            exact: "1.2.5"
        ),
    ],
    targets: []
)
