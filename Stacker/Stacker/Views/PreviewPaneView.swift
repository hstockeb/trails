import SwiftUI

struct PreviewPaneView: View {
    @Environment(AppState.self) private var state

    var body: some View {
        ZStack {
            Color(nsColor: .windowBackgroundColor)
            if let path = state.previewImagePath,
               let nsImage = NSImage(contentsOfFile: path) {
                Image(nsImage: nsImage)
                    .resizable()
                    .scaledToFit()
                    .padding(8)
                    .transition(.opacity)
            } else {
                VStack(spacing: 8) {
                    Image(systemName: "sparkles")
                        .font(.system(size: 48))
                        .foregroundStyle(.tertiary)
                    Text("Preview will appear here during stacking")
                        .foregroundStyle(.secondary)
                        .font(.caption)
                }
            }
        }
    }
}
