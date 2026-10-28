import Foundation
import AVFoundation
import Vision

// Offline OCR of every encoded frame, including image-embedded writing.
guard CommandLine.arguments.count == 4 else {
    fatalError("Usage: ocr-v12-final movie.mp4 frame-text.jsonl summary.json")
}
let source = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2])
let summary = URL(fileURLWithPath: CommandLine.arguments[3])
let asset = AVURLAsset(url: source)
let track = asset.tracks(withMediaType: .video)[0]
let reader = try AVAssetReader(asset: asset)
let video = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
video.alwaysCopiesSampleData = false
reader.add(video)
guard reader.startReading() else { fatalError("Unable to read movie") }
FileManager.default.createFile(atPath: output.path, contents: nil)
let stream = try FileHandle(forWritingTo: output)
defer { try? stream.close() }
let terms = ["專業，由人而來", "专业，由人而来", "劉天生", "刘天生", "李冠成", "鄭健麗", "郑健丽", "陳萬里", "陈万里", "楊金印", "杨金印", "王浩", "谷林丽", "谷林麗", "張志凌", "张志凌", "羅英姿", "罗英姿", "胡忠瑶", "胡忠瑤", "王娟", "David Lau", "Patrick Li", "Pamela Cheng", "Manli Chan", "Ken Yeung", "David Wang", "Lily Ku", "Noah Cheung", "Catherine Luo", "Vivian Mau", "Crystal Wang"]
var faceMatches: [[String: Any]] = []
var frame = 0
var matches: [[String: Any]] = []
let start = Date()
while let sample = video.copyNextSampleBuffer() {
    try autoreleasepool {
        guard let buffer = CMSampleBufferGetImageBuffer(sample) else { fatalError("Missing video buffer") }
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["zh-Hant", "zh-Hans", "en-US"]
        request.usesLanguageCorrection = false
        request.minimumTextHeight = 0.009
        let handler = VNImageRequestHandler(cvPixelBuffer: buffer, options: [:])
        let faces = VNDetectFaceRectanglesRequest()
        try handler.perform([request, faces])
        if !(faces.results ?? []).isEmpty { faceMatches.append(["frame": frame, "count": faces.results!.count]) }
        let strings = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
        let normalized = strings.joined().filter { !$0.isWhitespace }
        let hits = terms.filter { normalized.lowercased().contains($0.filter { !$0.isWhitespace }.lowercased()) }
        let record: [String: Any] = ["frame": frame, "pts": CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(sample)), "text": strings, "hits": hits]
        var data = try JSONSerialization.data(withJSONObject: record, options: [.sortedKeys])
        data.append(10)
        try stream.write(contentsOf: data)
        if !hits.isEmpty { matches.append(record) }
    }
    frame += 1
    if frame % 120 == 0 { print("OCR \(frame) frames, hits \(matches.count), \(Int(Date().timeIntervalSince(start)))s"); fflush(stdout) }
}
guard reader.status == .completed else { fatalError("Video read error: \(String(describing: reader.error))") }
let result: [String: Any] = ["frames": frame, "all_frames_processed": reader.status == .completed, "faceMatches": faceMatches, "terms": terms, "matches": matches, "seconds": Date().timeIntervalSince(start), "engine": "Apple Vision accurate; zh-Hant/zh-Hans/en-US; all encoded frames at source resolution", "limit": "OCR is probabilistic; corroborate with per-frame DOM audit, source/image inspection and visual QA."]
try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys]).write(to: summary)
print("OCR COMPLETE: \(frame) frames, \(matches.count) matching frames")
