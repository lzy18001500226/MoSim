import SwiftUI
import ComposableArchitecture
import AgentsMeshCore
import DesignSystem

#if canImport(UIKit)
import UIKit
import SwiftTerm

/// SwiftUI wrapper over SwiftTerm's UIKit `TerminalView`.
/// Registers itself with `PodOutputDispatcher` to receive bytes from the
/// relay WebSocket and writes them into the xterm buffer. User input and
/// resize events are plumbed back into TCA via the provided callbacks.
public struct TerminalView: View {
    let store: StoreOf<TerminalFeature>

    public init(store: StoreOf<TerminalFeature>) {
        self.store = store
    }

    public var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            if store.isConnecting {
                ProgressView().controlSize(.large).tint(.white)
            } else if let error = store.errorMessage {
                Text(error)
                    .font(AMTypography.body)
                    .foregroundStyle(AMColors.destructive)
                    .padding(AMSpacing.l)
            } else {
                SwiftTermRepresentable(
                    podKey: store.podKey,
                    onInput: { data in store.send(.inputEntered(data)) },
                    onResize: { cols, rows in
                        store.send(.resized(cols: UInt16(cols), rows: UInt16(rows)))
                    }
                )
                .ignoresSafeArea(.keyboard, edges: .bottom)
            }
        }
        .navigationTitle(store.podKey)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { store.send(.onAppear) }
    }
}

private struct SwiftTermRepresentable: UIViewRepresentable {
    let podKey: String
    let onInput: (Data) -> Void
    let onResize: (Int, Int) -> Void

    func makeUIView(context: Context) -> SwiftTerm.TerminalView {
        let view = SwiftTerm.TerminalView()
        view.backgroundColor = .black
        view.terminalDelegate = context.coordinator

        // Route Rust-produced bytes into SwiftTerm. Dispatcher holds a
        // weak-ish sink closure keyed by podKey so the view can be
        // deallocated safely when dismissed.
        let key = podKey
        PodOutputDispatcher.shared.register(podKey: key) { [weak view] data in
            DispatchQueue.main.async {
                // SwiftTerm's `feed` takes a Swift byte array.
                view?.feed(byteArray: ArraySlice(Array(data)))
            }
        }
        context.coordinator.podKey = key
        return view
    }

    func updateUIView(_ uiView: SwiftTerm.TerminalView, context: Context) {
        // Resize on layout change is driven by SwiftTerm's own size delegate
        // callback, not via SwiftUI updates.
    }

    static func dismantleUIView(_ uiView: SwiftTerm.TerminalView, coordinator: Coordinator) {
        if let key = coordinator.podKey {
            PodOutputDispatcher.shared.unregister(podKey: key)
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(onInput: onInput, onResize: onResize)
    }

    final class Coordinator: NSObject, TerminalViewDelegate {
        var podKey: String?
        let onInput: (Data) -> Void
        let onResize: (Int, Int) -> Void

        init(onInput: @escaping (Data) -> Void, onResize: @escaping (Int, Int) -> Void) {
            self.onInput = onInput
            self.onResize = onResize
        }

        // ── TerminalViewDelegate ──

        func sizeChanged(source: SwiftTerm.TerminalView, newCols: Int, newRows: Int) {
            onResize(newCols, newRows)
        }

        func send(source: SwiftTerm.TerminalView, data: ArraySlice<UInt8>) {
            onInput(Data(data))
        }

        func setTerminalTitle(source: SwiftTerm.TerminalView, title: String) {}
        func scrolled(source: SwiftTerm.TerminalView, position: Double) {}
        func hostCurrentDirectoryUpdate(source: SwiftTerm.TerminalView, directory: String?) {}
        func clipboardCopy(source: SwiftTerm.TerminalView, content: Data) {}
        func rangeChanged(source: SwiftTerm.TerminalView, startY: Int, endY: Int) {}
        func requestOpenLink(source: SwiftTerm.TerminalView, link: String, params: [String: String]) {}
        func bell(source: SwiftTerm.TerminalView) {}
        func iTermContent(source: SwiftTerm.TerminalView, content: ArraySlice<UInt8>) {}
    }
}

#else

// Non-iOS stub — keeps the package buildable on macOS CLI for unit tests
// that don't exercise the actual terminal surface.
public struct TerminalView: View {
    let store: StoreOf<TerminalFeature>
    public init(store: StoreOf<TerminalFeature>) { self.store = store }
    public var body: some View {
        Text("TerminalView is iOS-only").padding()
    }
}

#endif
