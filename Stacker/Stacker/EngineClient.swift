import Foundation

@MainActor
final class EngineClient: ObservableObject {
    private var process: Process?
    private var stdinPipe: Pipe?
    private var stdoutPipe: Pipe?
    private var readBuffer = Data()

    var onEvent: ((String, Any?) -> Void)?

    func start() throws {
        let pythonPath = ProcessInfo.processInfo.environment["STACKER_PYTHON"] ?? "/usr/local/bin/python3"
        let engineDir  = ProcessInfo.processInfo.environment["STACKER_ENGINE_DIR"]
            ?? URL(fileURLWithPath: #file)
                .deletingLastPathComponent()
                .deletingLastPathComponent()
                .deletingLastPathComponent()
                .appendingPathComponent("engine")
                .path

        let proc = Process()
        proc.executableURL = URL(fileURLWithPath: pythonPath)
        proc.arguments = ["-m", "engine.server"]
        proc.currentDirectoryURL = URL(fileURLWithPath: engineDir).deletingLastPathComponent()

        let inPipe  = Pipe()
        let outPipe = Pipe()
        proc.standardInput  = inPipe
        proc.standardOutput = outPipe
        proc.standardError  = FileHandle.standardError

        try proc.run()
        process    = proc
        stdinPipe  = inPipe
        stdoutPipe = outPipe

        outPipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            Task { @MainActor in self?.receiveData(data) }
        }
    }

    func stop() {
        process?.terminate()
        process = nil
    }

    func send<T: Encodable>(_ command: T) {
        guard let stdin = stdinPipe else { return }
        do {
            var data = try JSONEncoder().encode(command)
            data.append(contentsOf: [UInt8(ascii: "\n")])
            try stdin.fileHandleForWriting.write(contentsOf: data)
        } catch {
            print("[EngineClient] encode error: \(error)", to: &standardError)
        }
    }

    private func receiveData(_ data: Data) {
        readBuffer.append(data)
        while let newline = readBuffer.firstIndex(of: UInt8(ascii: "\n")) {
            let lineData = readBuffer[readBuffer.startIndex..<newline]
            readBuffer = readBuffer[readBuffer.index(after: newline)...]
            dispatchLine(Data(lineData))
        }
    }

    private func dispatchLine(_ data: Data) {
        guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String else { return }
        onEvent?(type, json["payload"])
    }
}

private var standardError = StandardError()
private struct StandardError: TextOutputStream {
    mutating func write(_ string: String) { fputs(string, stderr) }
}
