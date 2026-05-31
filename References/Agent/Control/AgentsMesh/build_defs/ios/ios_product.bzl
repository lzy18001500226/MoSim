"""Declarative iOS app target for AgentsMesh.

A lighter take on the AIO project's `ios_product()` — most AgentsMesh
iOS surface (single app, no extensions, no analytics plists, no
entitlements gymnastics) doesn't need the full AIO machinery. This macro
handles the 90% case:

  - `ios_application` with the Rust-backed XCFramework as a dep
  - `xcodeproj` target for day-to-day development in Xcode
  - Plist + Info.plist shape defaults aligned with
    clients/ios/App/Info.plist

Usage:
    load("//build_defs/ios:ios_product.bzl", "ios_app")

    ios_app(
        name = "AgentsMesh",
        bundle_id = "ai.agentsmesh.ios",
        minimum_os_version = "16.0",
        deps = [
            "//clients/ios/Packages/AgentsMeshCore:AgentsMeshCore",
            "//clients/ios/Packages/AgentsMeshFeatures/Sources/AppFeature:AppFeature",
        ],
        launch_storyboard = None,
    )
"""

load("@build_bazel_rules_apple//apple:ios.bzl", "ios_application", "ios_ui_test")
load("@build_bazel_rules_swift//swift:swift.bzl", "swift_library")
load("@rules_xcodeproj//xcodeproj:defs.bzl", "top_level_target", "xcodeproj")

def ios_app(
        name,
        bundle_id,
        deps,
        minimum_os_version = "16.0",
        infoplists = None,
        families = ["iphone", "ipad"],
        launch_storyboard = None,
        visibility = None):
    """Produce an iOS app binary + xcodeproj target.

    Args:
        name: Application target name. Also the xcodeproj name.
        bundle_id: CFBundleIdentifier.
        deps: Swift libraries the app depends on (typically a chain that
            transitively brings in the AgentsMeshCore XCFramework).
        minimum_os_version: Minimum iOS deployment target.
        infoplists: List of plist labels. Defaults to `[//clients/ios/App:Info.plist]`.
        families: Target device families (iPhone + iPad by default).
        launch_storyboard: Optional storyboard label.
        visibility: Standard visibility.
    """
    if infoplists == None:
        infoplists = ["//clients/ios/App:Info.plist"]

    ios_application(
        name = name,
        bundle_id = bundle_id,
        deps = deps,
        families = families,
        infoplists = infoplists,
        launch_storyboard = launch_storyboard,
        minimum_os_version = minimum_os_version,
        visibility = visibility or ["//visibility:public"],
    )

    # `bazel run :<name>_sim` installs + launches the `.app` on a booted
    # iOS Simulator. Wraps `sim_runner.sh` and pipes the app bundle path
    # + bundle id in via env vars.
    native.sh_binary(
        name = "{}_sim".format(name),
        srcs = ["//build_defs/ios:sim_runner.sh"],
        data = [":{}".format(name)],
        env = {
            "APP_BUNDLE_PATH": "$(rootpath :{})".format(name),
            "APP_BUNDLE_ID": bundle_id,
        },
        tags = ["manual", "requires-darwin"],
        visibility = visibility or ["//visibility:public"],
    )

    # `bazel run :xcodeproj` materializes an `.xcodeproj` so Xcode can
    # debug/profile the app normally. Replaces `xcodegen generate`.
    xcodeproj(
        name = "{}_xcodeproj".format(name),
        project_name = name,
        tags = ["manual"],
        top_level_targets = [
            top_level_target(
                label = ":{}".format(name),
                target_environments = ["simulator", "device"],
            ),
        ],
    )

def ios_e2e_tests(
        name,
        host_application,
        srcs,
        bundle_id,
        minimum_os_version = "16.0",
        deps = None,
        visibility = None):
    """XCUITest target hosted by an `ios_application`.

    Mirrors the playwright e2e setup on web/desktop: the test target
    drives the app through XCUIApplication queries, talking to the
    same dev backend the simulator uses for normal development. Tests
    are tagged `manual + requires-darwin` so a stray `bazel test //...`
    on Linux skips them; CI invokes the target explicitly on a macOS
    runner.

    Args:
        name: Test target name.
        host_application: Label of the `ios_application` (or `ios_app`)
            target the tests will drive.
        srcs: Swift test sources (the `XCTestCase` files + Page Objects
            + helpers).
        bundle_id: CFBundleIdentifier for the .xctest bundle. Must be
            distinct from the host app's bundle id.
        minimum_os_version: Should match the host app.
        deps: Extra Swift dependencies (e.g. shared test fixtures).
        visibility: Standard visibility.
    """
    lib_name = "{}_lib".format(name)
    swift_library(
        name = lib_name,
        srcs = srcs,
        module_name = name,
        testonly = True,
        deps = deps or [],
        tags = ["manual", "requires-darwin"],
    )

    ios_ui_test(
        name = name,
        bundle_id = bundle_id,
        minimum_os_version = minimum_os_version,
        test_host = host_application,
        deps = [":{}".format(lib_name)],
        tags = ["manual", "requires-darwin"],
        visibility = visibility or ["//visibility:public"],
    )
