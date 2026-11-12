import Foundation
import Vision
import AppKit

// usage: ocr <image> ...   prints one JSON line per image: {"file":..., "text":...}
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("{\"file\":\"\(path)\",\"text\":\"\",\"err\":1}"); continue
    }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    let h = VNImageRequestHandler(cgImage: cg, options: [:])
    try? h.perform([req])
    let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    let obj: [String: Any] = ["file": path, "text": lines.joined(separator: "\n")]
    if let d = try? JSONSerialization.data(withJSONObject: obj), let s = String(data: d, encoding: .utf8) { print(s) }
}
