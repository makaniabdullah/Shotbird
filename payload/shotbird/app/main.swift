// Shotbird: a native window for the Shotbird board (http://localhost:8777).
// Starts the board server through launch.sh if it isn't answering. Quitting leaves the server up,
// so orchestrator turns keep running. Build with ./build.sh.
import AppKit
import WebKit

let BOARD = URL(string: "http://localhost:8777/")!
let STATUS = URL(string: "http://127.0.0.1:8777/api/status")!
let HOME = FileManager.default.homeDirectoryForCurrentUser.path
let LAUNCHER = HOME + "/.claude/skills/shotbird/launch.sh"
let LOG = "~/Shotbird/.server.log"

// Window colour follows the board theme base: pure black in dark mode, #f6f6f7 in light.
let BASE_BG = NSColor(name: nil) { a in
    a.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua
        ? NSColor.black : NSColor(srgbRed: 0xf6 / 255, green: 0xf6 / 255, blue: 0xf7 / 255, alpha: 1)
}

// The Shotbird lockup (mark + wordmark) centred in the title bar. Clicks pass through, so the bar still drags the window.
final class TitleLogo: NSView {
    let dark = NSImage(contentsOf: Bundle.main.url(forResource: "titlebar-logo-dark", withExtension: "png") ?? URL(fileURLWithPath: "/"))
    let light = NSImage(contentsOf: Bundle.main.url(forResource: "titlebar-logo-light", withExtension: "png") ?? URL(fileURLWithPath: "/"))
    static let size = NSSize(width: 88, height: 20)
    override var intrinsicContentSize: NSSize { TitleLogo.size }
    override func hitTest(_ point: NSPoint) -> NSView? { nil }
    override func viewDidChangeEffectiveAppearance() { needsDisplay = true }
    override func draw(_ r: NSRect) {
        let isDark = effectiveAppearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua
        (isDark ? dark : light)?.draw(in: bounds, from: .zero, operation: .sourceOver, fraction: 1)
    }
}

func page(_ body: String) -> String {
    """
    <!doctype html><meta charset="utf-8"><style>
    :root{color-scheme:light dark}html,body{margin:0;height:100%;background:#f6f6f7;color:#6b6b74;
    font:14px -apple-system,system-ui,sans-serif;display:grid;place-items:center;text-align:center}
    @media (prefers-color-scheme:dark){html,body{background:#000;color:#a1a1aa}}
    b{display:block;color:#ff6b3d;font-size:15px;margin-bottom:6px}code{font:12px ui-monospace,monospace}
    button{margin-top:14px;font:inherit;padding:6px 14px;border-radius:8px;border:1px solid #888;background:none;color:inherit;cursor:pointer}
    </style><div>\(body)</div>
    """
}

final class AppDelegate: NSObject, NSApplicationDelegate, WKUIDelegate, WKNavigationDelegate, WKScriptMessageHandler {
    var window: NSWindow!
    var web: WKWebView!

    func applicationDidFinishLaunching(_ note: Notification) {
        buildMenu()
        buildWindow()
        start()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ app: NSApplication) -> Bool { false }

    func applicationShouldHandleReopen(_ app: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        if !flag { window.makeKeyAndOrderFront(nil) }
        return true
    }

    // MARK: server

    func start() {
        web.loadHTMLString(page("<b>Shotbird</b>Starting the board…"), baseURL: nil)
        DispatchQueue.global().async {
            var ok = self.serverUp()
            var err = ""
            if !ok {
                let p = Process()
                p.executableURL = URL(fileURLWithPath: "/bin/sh")
                p.arguments = [LAUNCHER, "serve"]
                let pipe = Pipe()
                p.standardError = pipe
                p.standardOutput = FileHandle.nullDevice
                do {
                    try p.run()
                    p.waitUntilExit()
                    err = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
                } catch { err = error.localizedDescription }
                ok = self.serverUp()
            }
            DispatchQueue.main.async {
                if ok { self.web.load(URLRequest(url: BOARD)) } else { self.fail(err) }
            }
        }
    }

    func serverUp() -> Bool {
        var req = URLRequest(url: STATUS)
        req.timeoutInterval = 1.5
        let done = DispatchSemaphore(value: 0)
        var ok = false
        URLSession.shared.dataTask(with: req) { _, resp, _ in
            ok = (resp as? HTTPURLResponse)?.statusCode == 200
            done.signal()
        }.resume()
        _ = done.wait(timeout: .now() + 3)
        return ok
    }

    func fail(_ why: String) {
        let msg = why.trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: "&", with: "&amp;").replacingOccurrences(of: "<", with: "&lt;")
        web.loadHTMLString(page("""
            <b>Shotbird couldn't start the board</b>\(msg.isEmpty ? "" : msg + "<br>")Details: <code>\(LOG)</code><br>
            <button onclick="webkit.messageHandlers.shotbird.postMessage('retry')">Try again</button>
            """), baseURL: nil)
    }

    func userContentController(_ c: WKUserContentController, didReceive m: WKScriptMessage) {
        if m.body as? String == "retry" { start() }
    }

    // MARK: window

    func buildWindow() {
        let cfg = WKWebViewConfiguration()
        cfg.applicationNameForUserAgent = "ShotbirdApp/2.0"
        cfg.userContentController.add(self, name: "shotbird")
        web = WKWebView(frame: .zero, configuration: cfg)
        web.uiDelegate = self
        web.navigationDelegate = self
        web.allowsBackForwardNavigationGestures = false
        web.setValue(false, forKey: "drawsBackground")  // no white flash; the window colour shows through
        web.underPageBackgroundColor = BASE_BG
        if #available(macOS 13.3, *) { web.isInspectable = true }

        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1440, height: 900),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "Shotbird"  // still names the window in the Window menu and Mission Control
        window.titleVisibility = .hidden
        window.titlebarAppearsTransparent = true
        window.backgroundColor = BASE_BG
        window.minSize = NSSize(width: 960, height: 620)
        window.isReleasedWhenClosed = false
        window.contentView = web
        window.center()
        window.setFrameAutosaveName("ShotbirdMain")
        if let bar = window.standardWindowButton(.closeButton)?.superview {
            let logo = TitleLogo()
            logo.translatesAutoresizingMaskIntoConstraints = false
            bar.addSubview(logo)
            NSLayoutConstraint.activate([
                logo.centerXAnchor.constraint(equalTo: bar.centerXAnchor),
                logo.centerYAnchor.constraint(equalTo: bar.centerYAnchor),
                logo.widthAnchor.constraint(equalToConstant: TitleLogo.size.width),
                logo.heightAnchor.constraint(equalToConstant: TitleLogo.size.height),
            ])
        }
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        // Debug hook: SHOTBIRD_SNAPSHOT=<png> saves the window frame (title bar included) once, then quits.
        if let out = ProcessInfo.processInfo.environment["SHOTBIRD_SNAPSHOT"] {
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                guard let frame = self.window.contentView?.superview,
                      let rep = frame.bitmapImageRepForCachingDisplay(in: frame.bounds) else { return }
                frame.cacheDisplay(in: frame.bounds, to: rep)
                try? rep.representation(using: .png, properties: [:])?.write(to: URL(fileURLWithPath: out))
                NSApp.terminate(nil)
            }
        }
    }

    // MARK: navigation

    func webView(_ w: WKWebView, decidePolicyFor action: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = action.request.url else { return decisionHandler(.allow) }
        if url.isFileURL { return decisionHandler(.cancel) }  // a file dropped outside a drop zone
        let local = ["localhost", "127.0.0.1"].contains(url.host ?? "")
        if (url.scheme == "http" || url.scheme == "https") && !local && action.targetFrame?.isMainFrame == true {
            NSWorkspace.shared.open(url)
            return decisionHandler(.cancel)
        }
        decisionHandler(.allow)
    }

    func webView(_ w: WKWebView, decidePolicyFor response: WKNavigationResponse,
                 decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void) {
        if !response.canShowMIMEType, let url = response.response.url {
            NSWorkspace.shared.open(url)
            return decisionHandler(.cancel)
        }
        decisionHandler(.allow)
    }

    func webView(_ w: WKWebView, didFailProvisionalNavigation n: WKNavigation!, withError e: Error) {
        let err = e as NSError
        if err.code == NSURLErrorCancelled { return }
        if (err.userInfo[NSURLErrorFailingURLErrorKey] as? URL)?.host == "localhost" { fail("The board server stopped answering.") }
    }

    func webViewWebContentProcessDidTerminate(_ w: WKWebView) { w.reload() }

    func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
        // Debug hook for build.sh tests: SHOTBIRD_SELFTEST=<file> writes page capabilities, then quits.
        guard let out = ProcessInfo.processInfo.environment["SHOTBIRD_SELFTEST"], w.url?.host == "localhost" else { return }
        let js = "JSON.stringify({ua:navigator.userAgent,secure:isSecureContext,clipboard:!!(navigator.clipboard&&navigator.clipboard.writeText),title:document.title})"
        w.evaluateJavaScript(js) { r, e in
            try? ((r as? String) ?? "error: \(String(describing: e))").write(toFile: out, atomically: true, encoding: .utf8)
            NSApp.terminate(nil)
        }
    }

    // MARK: UI delegate (file pickers, new windows, JS dialogs)

    func webView(_ w: WKWebView, runOpenPanelWith p: WKOpenPanelParameters, initiatedByFrame f: WKFrameInfo,
                 completionHandler done: @escaping ([URL]?) -> Void) {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = p.allowsMultipleSelection
        panel.beginSheetModal(for: window) { done($0 == .OK ? panel.urls : nil) }
    }

    func webView(_ w: WKWebView, createWebViewWith c: WKWebViewConfiguration, for action: WKNavigationAction,
                 windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = action.request.url { NSWorkspace.shared.open(url) }  // target=_blank / window.open
        return nil
    }

    func webView(_ w: WKWebView, runJavaScriptAlertPanelWithMessage msg: String, initiatedByFrame f: WKFrameInfo,
                 completionHandler done: @escaping () -> Void) {
        let a = NSAlert()
        a.messageText = msg
        a.beginSheetModal(for: window) { _ in done() }
    }

    func webView(_ w: WKWebView, runJavaScriptConfirmPanelWithMessage msg: String, initiatedByFrame f: WKFrameInfo,
                 completionHandler done: @escaping (Bool) -> Void) {
        let a = NSAlert()
        a.messageText = msg
        a.addButton(withTitle: "OK")
        a.addButton(withTitle: "Cancel")
        a.beginSheetModal(for: window) { done($0 == .alertFirstButtonReturn) }
    }

    func webView(_ w: WKWebView, runJavaScriptTextInputPanelWithPrompt prompt: String, defaultText: String?,
                 initiatedByFrame f: WKFrameInfo, completionHandler done: @escaping (String?) -> Void) {
        let a = NSAlert()
        a.messageText = prompt
        let field = NSTextField(frame: NSRect(x: 0, y: 0, width: 300, height: 24))
        field.stringValue = defaultText ?? ""
        a.accessoryView = field
        a.addButton(withTitle: "OK")
        a.addButton(withTitle: "Cancel")
        a.beginSheetModal(for: window) { done($0 == .alertFirstButtonReturn ? field.stringValue : nil) }
    }

    // MARK: menus

    @objc func reload() { if web.url?.host == "localhost" { web.reload() } else { start() } }
    @objc func zoomIn() { web.pageZoom = min(web.pageZoom + 0.1, 2) }
    @objc func zoomOut() { web.pageZoom = max(web.pageZoom - 0.1, 0.5) }
    @objc func zoomReset() { web.pageZoom = 1 }
    @objc func stopServer() {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/bin/sh")
        p.arguments = [LAUNCHER, "stop"]
        try? p.run()
        p.waitUntilExit()
        NSApp.terminate(nil)
    }

    func buildMenu() {
        let bar = NSMenu()
        func menu(_ title: String, _ items: [NSMenuItem]) {
            let top = NSMenuItem()
            let m = NSMenu(title: title)
            items.forEach(m.addItem)
            top.submenu = m
            bar.addItem(top)
        }
        func item(_ t: String, _ a: Selector?, _ k: String = "", _ mods: NSEvent.ModifierFlags = .command,
                  target: AnyObject? = nil) -> NSMenuItem {
            let i = NSMenuItem(title: t, action: a, keyEquivalent: k)
            i.keyEquivalentModifierMask = mods
            i.target = target
            return i
        }
        let hideOthers = item("Hide Others", #selector(NSApplication.hideOtherApplications(_:)), "h", [.command, .option])
        menu("Shotbird", [
            item("About Shotbird", #selector(NSApplication.orderFrontStandardAboutPanel(_:)), ""),
            .separator(),
            item("Stop Shotbird Server", #selector(stopServer), "", target: self),
            .separator(),
            item("Hide Shotbird", #selector(NSApplication.hide(_:)), "h"),
            hideOthers,
            .separator(),
            item("Quit Shotbird", #selector(NSApplication.terminate(_:)), "q"),
        ])
        menu("Edit", [
            item("Undo", Selector(("undo:")), "z"),
            item("Redo", Selector(("redo:")), "z", [.command, .shift]),
            .separator(),
            item("Cut", #selector(NSText.cut(_:)), "x"),
            item("Copy", #selector(NSText.copy(_:)), "c"),
            item("Paste", #selector(NSText.paste(_:)), "v"),
            item("Select All", #selector(NSText.selectAll(_:)), "a"),
        ])
        menu("View", [
            item("Reload", #selector(reload), "r", target: self),
            .separator(),
            item("Actual Size", #selector(zoomReset), "0", target: self),
            item("Zoom In", #selector(zoomIn), "=", target: self),
            item("Zoom Out", #selector(zoomOut), "-", target: self),
        ])
        menu("Window", [
            item("Minimize", #selector(NSWindow.performMiniaturize(_:)), "m"),
            item("Zoom", #selector(NSWindow.performZoom(_:)), ""),
            .separator(),
            item("Close", #selector(NSWindow.performClose(_:)), "w"),
        ])
        NSApp.mainMenu = bar
        NSApp.windowsMenu = bar.items.last?.submenu
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
