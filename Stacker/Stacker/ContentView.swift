import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "sparkles")
                .font(.system(size: 40))
                .foregroundStyle(.accent)

            Text("Stacker")
                .font(.title2)
                .fontWeight(.semibold)

            Text("SwiftUI shell scaffolded with XcodeGen.")
                .foregroundStyle(.secondary)
        }
        .frame(minWidth: 480, minHeight: 320)
        .padding(32)
    }
}

#Preview {
    ContentView()
}
