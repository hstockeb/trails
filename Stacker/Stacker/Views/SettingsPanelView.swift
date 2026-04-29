import SwiftUI

struct SettingsPanelView: View {
    @Environment(AppState.self) private var state
    @EnvironmentObject private var engine: EngineClient

    private let methods = ["lighten", "maximum", "average", "gapfill", "comet"]
    private let formats = ["jpeg", "png", "tiff"]

    var body: some View {
        @Bindable var state = state
        VStack(alignment: .leading, spacing: 10) {
            Picker("Method", selection: $state.method) {
                ForEach(methods, id: \.self) { Text($0).tag($0) }
            }
            .pickerStyle(.menu)

            Picker("Format", selection: $state.outputFormat) {
                ForEach(formats, id: \.self) { Text($0.uppercased()).tag($0) }
            }
            .pickerStyle(.segmented)

            if state.outputFormat == "jpeg" {
                HStack {
                    Text("Quality")
                    Slider(value: Binding(
                        get: { Double(state.jpegQuality) },
                        set: { state.jpegQuality = Int($0) }
                    ), in: 1...100, step: 1)
                    Text("\(state.jpegQuality)")
                        .monospacedDigit()
                        .frame(width: 30)
                }
            }

            Toggle("Hot-pixel reduction", isOn: $state.hotPixelReduction)
            Toggle("Align frames", isOn: $state.alignFrames)

            HStack {
                Text("Dark frame:")
                    .font(.caption)
                Text(state.darkFramePath.map { URL(fileURLWithPath: $0).lastPathComponent }
                     ?? "None")
                    .font(.caption).foregroundStyle(.secondary)
                Spacer()
                Button("…") { pickDarkFrame() }
                    .font(.caption)
                if state.darkFramePath != nil {
                    Button("✕") { state.darkFramePath = nil }
                        .font(.caption).foregroundStyle(.red)
                }
            }

            Button(state.isStacking ? "Stacking…" : "Stack") {
                startStack()
            }
            .disabled(state.selectedFrames.isEmpty || state.isStacking)
            .buttonStyle(.borderedProminent)
            .frame(maxWidth: .infinity)
        }
        .padding(.horizontal)
    }

    private func pickDarkFrame() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowedContentTypes = [.image]
        if panel.runModal() == .OK {
            state.darkFramePath = panel.url?.path
        }
    }

    private func startStack() {
        let frames = state.selectedFrames
        guard !frames.isEmpty else { return }

        var darkFrame: FrameRecordPayload? = nil
        if let dfPath = state.darkFramePath {
            darkFrame = FrameRecordPayload(path: dfPath,
                filename: URL(fileURLWithPath: dfPath).lastPathComponent,
                index: -1, width: 0, height: 0, is_raw: false,
                capture_time: nil, exposure_seconds: nil)
        }

        let opts = StackOptionsPayload(
            hot_pixel_reduction: state.hotPixelReduction,
            align_frames: state.alignFrames,
            output_format: state.outputFormat,
            jpeg_quality: state.jpegQuality,
            manual_exposure_seconds: state.manualExposureSeconds
        )
        let job = StackJobPayload(frames: frames, method: state.method,
                                  options: opts, dark_frame: darkFrame)
        state.isStacking = true
        state.stackProgress = 0
        state.previewImagePath = nil
        state.errorMessage = nil
        engine.send(StartStackCommand(payload: job))
    }
}
