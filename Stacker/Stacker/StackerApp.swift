import SwiftUI

@main
struct StackerApp: App {
    @State private var appState = AppState()
    @StateObject private var engine = EngineClient()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(appState)
                .environmentObject(engine)
                .onAppear {
                    try? engine.start()
                    engine.onEvent = { type, payload in
                        handleEngineEvent(type: type, payload: payload,
                                          state: appState)
                    }
                }
                .onDisappear { engine.stop() }
        }
        .windowResizability(.contentSize)
    }
}

private func handleEngineEvent(type: String, payload: Any?, state: AppState) {
    switch type {
    case "scan_complete":
        if let arr = payload as? [[String: Any]] {
            let decoder = JSONDecoder()
            if let data = try? JSONSerialization.data(withJSONObject: arr),
               let frames = try? decoder.decode([FrameRecordPayload].self, from: data) {
                state.frames = frames
                state.selectedFirstIndex = 0
                state.selectedLastIndex = max(0, frames.count - 1)
            }
        }
    case "progress":
        if let p = payload as? [String: Any],
           let frame = p["frame"] as? Int, let total = p["total"] as? Int, total > 0 {
            state.stackProgress = Double(frame) / Double(total)
            state.progressText = "\(frame) / \(total) frames"
        }
    case "preview":
        if let p = payload as? [String: Any], let path = p["path"] as? String {
            state.previewImagePath = path
        }
    case "done":
        if let p = payload as? [String: Any] {
            state.lastResultPath = p["tmp_result_path"] as? String
        }
        state.isStacking = false
        state.stackProgress = 1.0
    case "export_done":
        if let p = payload as? [String: Any] {
            state.lastOutputPath = p["output_path"] as? String
        }
    case "error":
        if let p = payload as? [String: Any] {
            state.errorMessage = p["message"] as? String
        }
        state.isStacking = false
    case "cancelled":
        state.isStacking = false
    default:
        break
    }
}
