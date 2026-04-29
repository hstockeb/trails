import SwiftUI

struct FolderPickerView: View {
    @Environment(AppState.self) private var state
    @EnvironmentObject private var engine: EngineClient

    var body: some View {
        HStack {
            Text(state.folderPath.isEmpty ? "No folder selected" : state.folderPath)
                .lineLimit(1)
                .truncationMode(.middle)
                .foregroundStyle(state.folderPath.isEmpty ? .secondary : .primary)
                .frame(maxWidth: .infinity, alignment: .leading)

            Button("Choose Folder…") { pickFolder() }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 8))
        .onDrop(of: [.fileURL], isTargeted: nil) { providers in
            handleDrop(providers)
        }
    }

    private func pickFolder() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = true          // allow picking a file inside the folder
        panel.allowsMultipleSelection = false
        panel.message = "Select a folder or any image inside it"
        if panel.runModal() == .OK, let url = panel.url {
            let folder = url.hasDirectoryPath ? url : url.deletingLastPathComponent()
            scanFolder(folder.path)
        }
    }

    private func handleDrop(_ providers: [NSItemProvider]) -> Bool {
        guard let provider = providers.first else { return false }
        provider.loadItem(forTypeIdentifier: "public.file-url") { item, _ in
            if let data = item as? Data,
               let url = URL(dataRepresentation: data, relativeTo: nil) {
                DispatchQueue.main.async { self.scanFolder(url.path) }
            }
        }
        return true
    }

    private func scanFolder(_ path: String) {
        state.folderPath = path
        engine.send(ScanFolderCommand(payload: .init(path: path)))
    }
}
