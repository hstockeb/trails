import SwiftUI

struct FrameListView: View {
    @Environment(AppState.self) private var state

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Label("\(state.frameCount) frames selected", systemImage: "photo.stack")
                    .font(.subheadline)
                Spacer()
                if let exp = state.totalExposureSeconds {
                    Text(formatExposure(exp))
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }

            if !state.frames.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("First: \(state.frames[state.selectedFirstIndex].filename)")
                        .font(.caption).foregroundStyle(.secondary)
                    Slider(
                        value: Binding(
                            get: { Double(state.selectedFirstIndex) },
                            set: { state.selectedFirstIndex = min(Int($0), state.selectedLastIndex) }
                        ),
                        in: 0...Double(state.frames.count - 1),
                        step: 1
                    )

                    Text("Last: \(state.frames[state.selectedLastIndex].filename)")
                        .font(.caption).foregroundStyle(.secondary)
                    Slider(
                        value: Binding(
                            get: { Double(state.selectedLastIndex) },
                            set: { state.selectedLastIndex = max(Int($0), state.selectedFirstIndex) }
                        ),
                        in: 0...Double(state.frames.count - 1),
                        step: 1
                    )
                }
            }

            if state.totalExposureSeconds == nil && !state.frames.isEmpty {
                HStack {
                    Text("Exposure per frame (s):")
                        .font(.caption)
                    TextField("e.g. 25", value: Binding(
                        get: { state.manualExposureSeconds ?? 0 },
                        set: { state.manualExposureSeconds = $0 > 0 ? $0 : nil }
                    ), format: .number)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 70)
                }
            }
        }
        .padding(.horizontal)
    }

    private func formatExposure(_ seconds: Double) -> String {
        let mins = seconds / 60
        if mins < 60 { return "\(Int(mins.rounded()))min total" }
        let h = Int(mins) / 60
        let m = Int(mins) % 60
        return m > 0 ? "\(h)h \(m)min total" : "\(h)h total"
    }
}
