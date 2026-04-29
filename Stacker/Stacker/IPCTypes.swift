import Foundation

// MARK: - Outgoing commands (Swift → Python)

struct ScanFolderCommand: Encodable {
    let type = "scan_folder"
    let payload: ScanFolderPayload
    struct ScanFolderPayload: Encodable { let path: String }
}

struct StartStackCommand: Encodable {
    let type = "start_stack"
    let payload: StackJobPayload
}

struct ExportCommand: Encodable {
    let type = "export"
    let payload: ExportPayload
    struct ExportPayload: Encodable {
        let output_path: String
        let format: String
        let quality: Int
        let resize: [Int]?
        let crop: [Int]?
    }
}

struct CancelCommand: Encodable {
    let type = "cancel"
}

// MARK: - Shared payload types

struct FrameRecordPayload: Codable, Identifiable {
    var id: String { path }
    let path: String
    let filename: String
    let index: Int
    let width: Int
    let height: Int
    let is_raw: Bool
    let capture_time: String?
    let exposure_seconds: Double?
}

struct StackOptionsPayload: Encodable {
    var hot_pixel_reduction: Bool = false
    var align_frames: Bool = false
    var output_format: String = "jpeg"
    var jpeg_quality: Int = 85
    var resize: [Int]? = nil
    var crop: [Int]? = nil
    var gpu: Bool = false
    var preview_every_n_frames: Int = 10
    var manual_exposure_seconds: Double? = nil
}

struct StackJobPayload: Encodable {
    let frames: [FrameRecordPayload]
    let method: String
    let options: StackOptionsPayload
    let dark_frame: FrameRecordPayload?
}

// MARK: - Incoming events (Python → Swift)

struct IPCEvent: Decodable {
    let type: String
    let payload: IPCPayload?
}

enum IPCPayload: Decodable {
    case scanComplete([FrameRecordPayload])
    case progress(frame: Int, total: Int)
    case preview(path: String)
    case done(tmpResultPath: String?, totalExposureSeconds: Double?, framesProcessed: Int)
    case exportDone(outputPath: String)
    case error(message: String)
    case cancelled
    case unknown

    init(from decoder: Decoder) throws {
        // Decoded via IPCEvent.init — see EngineClient
        self = .unknown
    }
}
