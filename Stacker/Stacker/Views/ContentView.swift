import SwiftUI

struct ContentView: View {
    @Environment(AppState.self) private var state

    var body: some View {
        HSplitView {
            // Left panel
            VStack(alignment: .leading, spacing: 12) {
                FolderPickerView()
                FrameListView()
                SettingsPanelView()
                Spacer()
                StackProgressView()
            }
            .frame(minWidth: 300, maxWidth: 380)
            .padding()

            // Right panel
            PreviewPaneView()
                .frame(minWidth: 400)
        }
        .frame(minWidth: 720, minHeight: 540)
        .alert("Error", isPresented: Binding(
            get: { state.errorMessage != nil },
            set: { if !$0 { state.errorMessage = nil } }
        )) {
            Button("OK", role: .cancel) { state.errorMessage = nil }
        } message: {
            Text(state.errorMessage ?? "")
        }
    }
}
