// Render PDF pages to PNG with macOS PDFKit (no poppler needed).
//   osascript -l JavaScript pdfpage.js <in.pdf> <outDir> [pages e.g. "1,3,5-8" | "all"] [width px, default 1600]
// Prints one line per written PNG. Pages are 1-based.
ObjC.import('PDFKit');
ObjC.import('AppKit');
function run(argv) {
  var inPath = argv[0], outDir = argv[1], spec = argv[2] || 'all', width = parseInt(argv[3] || '1600', 10);
  var doc = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(inPath));
  if (!doc || doc.isNil()) return 'ERROR: cannot open ' + inPath;
  var n = doc.pageCount, pages = [];
  if (spec === 'all') { for (var i = 1; i <= n; i++) pages.push(i); }
  else spec.split(',').forEach(function (part) {
    var m = part.trim().match(/^(\d+)(?:-(\d+))?$/);
    if (!m) return;
    var a = +m[1], b = m[2] ? +m[2] : a;
    for (var p = a; p <= b && p <= n; p++) pages.push(p);
  });
  $.NSFileManager.defaultManager.createDirectoryAtPathWithIntermediateDirectoriesAttributesError(outDir, true, $(), $());
  var out = [];
  pages.forEach(function (p) {
    var page = doc.pageAtIndex(p - 1);
    var box = page.boundsForBox($.kPDFDisplayBoxMediaBox);
    var w = box.size.width, h = box.size.height;
    var scale = width / w;
    var img = page.thumbnailOfSizeForBox($.NSMakeSize(Math.round(w * scale), Math.round(h * scale)), $.kPDFDisplayBoxMediaBox);
    var rep = $.NSBitmapImageRep.imageRepWithData(img.TIFFRepresentation);
    var png = rep.representationUsingTypeProperties($.NSBitmapImageFileTypePNG, $());
    var path = outDir + '/page-' + ('00' + p).slice(-3) + '.png';
    png.writeToFileAtomically(path, true);
    out.push(path);
  });
  return 'pages=' + n + '\n' + out.join('\n');
}
