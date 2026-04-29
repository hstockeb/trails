import SwiftUI
import UniformTypeIdentifiers

struct StackProgressView: View {
    @Environment(AppState.self) private var state
    @EnvironmentObject private var engine: EngineClient

    var body: some View {
        VStack(spacing: 6) {
            if state.isStacking {
                ProgressView(value: state.stackProgress)
                HStack {
                    Text(state.progressText)
                        .font(.caption).foregroundStyle(.secondary)
                    Spacer()
                    Button("Cancel") { engine.send(CancelCommand()) }
                        .font(.caption)
                        .foregroundStyle(.red)
                }
            } else if let outPath = state.lastOutputPath {
                HStack {
                    Image(systemName: "checkmark.circle.fill").foregroundStyle(.green)
                    Text(URL(fileURLWithPath: outPath).lastPathComponent)
                        .font(.caption).lineLimit(1).truncationMode(.middle)
                    Spacer()
                    Button("Reveal in Finder") {
                        NSWorkspace.shared.activateFileViewerSelecting(
                            [URL(fileURLWithPath: outPath)])
                    }
                    .font(.caption)
                }
                ExportBarView()
            } else if state.lastResultPath != nil {
                ExportBarView()
            }
        }
        .padding(.horizontal)
        .animation(.default, value: state.isStacking)
    }
}

private struct ExportBarView: View {
    @Environment(AppState.self) private var state
    @EnvironmentObject private var engine: EngineClient

    var body: some View {
        Button("Export…") { exportResult() }
            .buttonStyle(.borderedProminent)
            .frame(maxWidth: .infinity)
    }

    private func exportResult() {
        let panel = NSSavePanel()
        panel.nameFieldStringValue = suggestedFilename()
        panel.allowedContentTypes = contentTypes()
        if panel.runModal() == .OK, let url = panel.url {
            engine.send(ExportCommand(payload: .init(
                output_path: url.path,
                format: state.outputFormat,
                quality: state.jpegQuality,
                resize: nil,
                crop: nil
            )))
        }
    }

    private func suggestedFilename() -> String {
        "startrails_export.\(EXT_MAP[state.outputFormat] ?? state.outputFormat)"
    }

    private let EXT_MAP = ["jpeg": "jpg", "png": "png", "tiff": "tif"]

    private func contentTypes() -> [UTType] {
        switch state.outputFormat {
        case "jpeg": return [.jpeg]
        case "png":  return [.png]
        case "tiff": return [.tiff]
        default:     return [.image]
        }
    }
}
