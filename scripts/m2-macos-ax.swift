// Runner-only native UI driver. Never bundled with the application.
import AppKit
import ApplicationServices
import Foundation

let args = CommandLine.arguments
let operation = args.count > 1 ? args[1] : "snapshot"
guard let running = NSRunningApplication.runningApplications(withBundleIdentifier: "io.github.thomasttcryoo.embroiderystudio").first else { fatalError("Installed app is not running") }
guard AXIsProcessTrusted() else { fatalError("Runner accessibility is unavailable; no permissions were changed") }
let app = AXUIElementCreateApplication(running.processIdentifier)
func attribute(_ e: AXUIElement, _ key: String) -> CFTypeRef? {
    var value: CFTypeRef?
    if AXUIElementCopyAttributeValue(e, key as CFString, &value) != .success { return nil }
    return value
}
func string(_ e: AXUIElement, _ key: String) -> String { attribute(e,key).map { String(describing:$0) } ?? "" }
var elements: [AXUIElement] = []
var rows: [[String: Any]] = []
func visit(_ e: AXUIElement, _ depth: Int) {
    if depth > 35 || elements.count > 12000 { return }
    let index=elements.count
    elements.append(e)
    var row:[String:Any] = ["index":index,"depth":depth,"role":string(e,kAXRoleAttribute),"title":string(e,kAXTitleAttribute),"description":string(e,kAXDescriptionAttribute),"value":string(e,kAXValueAttribute),"help":string(e,kAXHelpAttribute),"identifier":string(e,kAXIdentifierAttribute),"subrole":string(e,kAXSubroleAttribute)]
    if let p=attribute(e,kAXPositionAttribute),let s=attribute(e,kAXSizeAttribute) {
        var position=CGPoint.zero;var size=CGSize.zero
        if AXValueGetValue(p as! AXValue,.cgPoint,&position) && AXValueGetValue(s as! AXValue,.cgSize,&size) {
            row["bounds"]=["x":position.x,"y":position.y,"width":size.width,"height":size.height]
        }
    }
    rows.append(row)
    if let children=attribute(e,kAXChildrenAttribute) as? [AXUIElement] { for child in children { visit(child,depth+1) } }
}
if !["key","type","paste","activate"].contains(operation) { visit(app,0) }
func emit(_ value: Any) { let d=try! JSONSerialization.data(withJSONObject:value,options:[.prettyPrinted,.sortedKeys]); print(String(data:d,encoding:.utf8)!) }
func key(_ code: CGKeyCode, _ flags: CGEventFlags = [], settle:Bool = true) {
    for down in [true,false] { let event=CGEvent(keyboardEventSource:nil,virtualKey:code,keyDown:down)!;event.flags=flags;event.post(tap:.cghidEventTap);usleep(20000) }
    if settle {RunLoop.current.run(until:Date(timeIntervalSinceNow:0.15))}
}
if operation == "activate" {running.activate(options:[.activateIgnoringOtherApps]);emit(["result":"activated"])}
else if operation == "snapshot" { emit(rows) }
else if operation == "key" {
    let flags=CGEventFlags(rawValue:UInt64(args[3])!)
    key(CGKeyCode(args[2])!,flags)
    emit(["result":"sent"])
} else if operation == "type" {
    // The observed runner uses the US keyboard layout. Native XPC Open sheets
    // on macOS 14 ignore injected Unicode strings; send actual physical keys.
    let codes:[Character:CGKeyCode] = ["a":0,"s":1,"d":2,"f":3,"h":4,"g":5,"z":6,"x":7,"c":8,"v":9,"b":11,"q":12,"w":13,"e":14,"r":15,"y":16,"t":17,"1":18,"2":19,"3":20,"4":21,"6":22,"5":23,"=":24,"9":25,"7":26,"-":27,"8":28,"0":29,"]":30,"o":31,"u":32,"[":33,"i":34,"p":35,"l":37,"j":38,"'":39,"k":40,";":41,"\\":42,",":43,"/":44,"n":45,"m":46,".":47," ":49,"`":50]
    for character in args[2] {
        let lower=Character(String(character).lowercased())
        let shifted=character == "_" || character != lower
        let base:Character=character == "_" ? "-" : lower
        guard let code=codes[base] else {fatalError("Unsupported test-fixture character")}
        key(code,shifted ? .maskShift : [],settle:false)
    }
    RunLoop.current.run(until:Date(timeIntervalSinceNow:0.3))
    emit(["result":"typed test data"])
} else if operation == "paste" {
    NSPasteboard.general.clearContents();NSPasteboard.general.setString(args[2],forType:.string)
    key(9,.maskCommand)
    emit(["result":"pasted test data"])
} else if operation == "filename" {
    let fields=rows.filter { row in
        let role=row["role"] as! String
        let label=["title","description","help","identifier"].map{row[$0] as! String}.joined(separator:" ").lowercased()
        return ["AXTextField","AXComboBox"].contains(role) && (label.contains("save as") || label.contains("saveas") || (row["value"] as! String).contains("Native Mac ZIP"))
    }
    guard let row=fields.first,let index=row["index"] as? Int else {emit(["error":"Save filename field unavailable","fields":rows.filter{($0["role"] as? String)=="AXTextField"}]);exit(4)}
    let result=AXUIElementSetAttributeValue(elements[index],kAXValueAttribute as CFString,args[2] as CFString)
    emit(["result":result.rawValue,"observed":row]);if result != .success {exit(5)}
} else {
    let wanted=args[2]
    let matching=rows.filter { row in ["title","description","help","value"].contains { (row[$0] as? String)==wanted } }
    let candidates=matching.filter { row in
        let role=row["role"] as! String
        if operation == "click" {return row["bounds"] != nil}
        if operation == "range" {return role == "AXSlider" && row["bounds"] != nil}
        return operation == "press" ? ["AXButton","AXPopUpButton","AXLink","AXRadioButton","AXCheckBox","AXMenuItem"].contains(role) : ["AXTextField","AXTextArea","AXSlider","AXComboBox"].contains(role)
    }
    guard let row=candidates.first, let index=row["index"] as? Int else { emit(["error":"No matching actionable element","wanted":wanted,"matches":matching]);exit(2) }
    let element=elements[index]
    let result: AXError
    if operation == "click" || operation == "range" {
        let b=row["bounds"] as! [String:CGFloat]
        let fraction=operation == "range" ? CGFloat(Double(args[3])!) : 0.5
        let point=CGPoint(x:b["x"]!+max(1,min(b["width"]!-1,b["width"]!*fraction)),y:b["y"]!+b["height"]!/2)
        for type in [CGEventType.leftMouseDown,CGEventType.leftMouseUp] {CGEvent(mouseEventSource:nil,mouseType:type,mouseCursorPosition:point,mouseButton:.left)!.post(tap:.cghidEventTap);usleep(50000)}
        RunLoop.current.run(until:Date(timeIntervalSinceNow:0.3))
        result = .success
    } else if operation == "press" { result=AXUIElementPerformAction(element,kAXPressAction as CFString) }
    else {
        let value: CFTypeRef = (row["role"] as? String)=="AXSlider" ? NSNumber(value:Double(args[3])!) : args[3] as CFString
        result=AXUIElementSetAttributeValue(element,kAXValueAttribute as CFString,value)
    }
    emit(["result":result.rawValue,"observed":row])
    if result != .success { exit(3) }
}
