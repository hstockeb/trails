import Foundation
import SwiftUI
import Observation

@Observable
final class AppState {
    var folderPath: String = ""
    var frames: [FrameRecordPayload] = []
    var selectedFirstIndex: Int = 0
    var selectedLastIndex: Int = 0
    var sortOrder: String = "filename"   // "filename" | "timestamp"
    var manualExposureSeconds: Double? = nil

    var method: String = "lighten"       // lighten|maximum|average|gapfill|comet
    var outputFormat: String = "jpeg"
    var jpegQuality: Int = 85
    var hotPixelReduction: Bool = false
    var alignFrames: Bool = false
    var darkFramePath: String? = nil

    var isStacking: Bool = false
    var stackProgress: Double = 0.0      // 0.0–1.0
    var progressText: String = ""
    var previewImagePath: String? = nil
    var lastResultPath: String? = nil
    var lastOutputPath: String? = nil
    var errorMessage: String? = nil

    var selectedFrames: [FrameRecordPayload] {
        guard !frames.isEmpty else { return [] }
        let last = min(selectedLastIndex, frames.count - 1)
        let first = min(selectedFirstIndex, last)
        return Array(frames[first...last])
    }

    var totalExposureSeconds: Double? {
        let sel = selectedFrames
        if sel.isEmpty { return nil }
        if let manual = manualExposureSeconds {
            return manual * Double(sel.count)
        }
        guard sel.allSatisfy({ $0.exposure_seconds != nil }) else { return nil }
        return sel.compactMap(\.exposure_seconds).reduce(0, +)
    }

    var frameCount: Int { selectedFrames.count }
}
