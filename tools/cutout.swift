// Вирізає людину з фото через вбудований у macOS Vision (macOS 14+).
// swift tools/cutout.swift <вхід.jpg> <вихід.png>
import Vision
import CoreImage

let args = CommandLine.arguments
guard args.count == 3 else { print("Використання: swift cutout.swift <вхід> <вихід.png>"); exit(2) }
let ci = CIImage(contentsOf: URL(fileURLWithPath: args[1]))!
let handler = VNImageRequestHandler(ciImage: ci)
let req = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([req])
guard let res = req.results?.first else { print("Людину на фото не знайдено"); exit(1) }
let buf = try res.generateMaskedImage(ofInstances: res.allInstances, from: handler, croppedToInstancesExtent: false)
try CIContext().writePNGRepresentation(of: CIImage(cvPixelBuffer: buf), to: URL(fileURLWithPath: args[2]),
                                       format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
print("ok")
