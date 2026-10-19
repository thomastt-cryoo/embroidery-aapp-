// Standalone diagnostic only. No embroidery application code is loaded or changed.
import AppKit
import WebKit
import Metal
import CoreGraphics
import Foundation

let destination=CommandLine.arguments[1]
let devices=MTLCopyAllDevices().map { ["name":$0.name,"lowPower":$0.isLowPower,"removable":$0.isRemovable] as [String:Any] }
let script="""
(()=>{
 const observations=[];
 for(const type of ['webgl','webgl2']) for(const antialias of [false,true]){
  const canvas=document.createElement('canvas');canvas.width=128;canvas.height=128;document.body.append(canvas);
  const row={type,antialias};observations.push(row);
  try{
   const gl=canvas.getContext(type,{antialias,alpha:true,preserveDrawingBuffer:true});row.created=!!gl;
   if(!gl)continue;
   row.contextLostBefore=gl.isContextLost();row.errorBefore=gl.getError();
   row.version=gl.getParameter(gl.VERSION);row.renderer=gl.getParameter(gl.RENDERER);row.vendor=gl.getParameter(gl.VENDOR);
   const precision=gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER,gl.HIGH_FLOAT);
   row.fragmentHighFloat=precision?{precision:precision.precision,rangeMin:precision.rangeMin,rangeMax:precision.rangeMax}:null;
   row.errorAfterPrecision=gl.getError();
   const extension=gl.getExtension('WEBGL_debug_renderer_info');
   if(extension){row.unmaskedRenderer=gl.getParameter(extension.UNMASKED_RENDERER_WEBGL);row.unmaskedVendor=gl.getParameter(extension.UNMASKED_VENDOR_WEBGL);}
   gl.clearColor(0,1,0,1);gl.clear(gl.COLOR_BUFFER_BIT);
   const pixel=new Uint8Array(4);gl.readPixels(64,64,1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixel);row.readPixel=Array.from(pixel);
   row.contextLostAfter=gl.isContextLost();row.errorAfterRead=gl.getError();
  }catch(error){row.exception=String(error);}
 }
 window.graphicsProbe=observations;return JSON.stringify({userAgent:navigator.userAgent,observations});
})()
"""
class Probe: NSObject, WKNavigationDelegate {
 var window:NSWindow!
 var view:WKWebView!
 func start(){
  window=NSWindow(contentRect:NSRect(x:100,y:100,width:700,height:500),styleMask:[.titled,.closable],backing:.buffered,defer:false)
  window.title="M2 standalone graphics diagnostic"
  view=WKWebView(frame:window.contentView!.bounds)
  view.navigationDelegate=self;window.contentView=view
  window.makeKeyAndOrderFront(nil);NSApp.activate(ignoringOtherApps:true)
  view.loadHTMLString("<html><body><h1>Standalone WebKit graphics probe</h1><p>No embroidery application code or assets are loaded.</p></body></html>",baseURL:nil)
 }
 func webView(_ webView:WKWebView,didFinish navigation:WKNavigation!){
  DispatchQueue.main.asyncAfter(deadline:.now()+2){
   webView.evaluateJavaScript(script){value,error in
    var result:[String:Any] = ["metalDevices":devices,"defaultMetalDevice":MTLCreateSystemDefaultDevice()?.name ?? "none","appCodeLoaded":false,"source":"separate default WKWebView; default public configuration","os":ProcessInfo.processInfo.operatingSystemVersionString]
    if let data=(value as? String)?.data(using:.utf8),let observed=try? JSONSerialization.jsonObject(with:data){result["webgl"]=observed}
    if let error=error{result["error"]=String(describing:error)}
    let output=try! JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys])
    try! output.write(to:URL(fileURLWithPath:destination));print(String(data:output,encoding:.utf8)!)
    NSApp.terminate(nil)
   }
  }
 }
}
let application=NSApplication.shared
application.setActivationPolicy(.regular)
let probe=Probe();probe.start()
DispatchQueue.main.asyncAfter(deadline:.now()+60){fputs("Standalone graphics probe timed out\n",stderr);exit(2)}
application.run()
