/** Real Canvas 2D integration checks. Run against the Vite development server.
 * No engine, graphics APIs or pixels are mocked. This is never packaged. */
import { createRequire } from "node:module";
import { mkdir, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import assert from "node:assert/strict";
const root=resolve(import.meta.dirname,"..");
const require=createRequire(join(root,"editor/package.json"));
const {chromium}=require("playwright-core");
const out=join(root,"reports/M2/etsy/renderer-integration");
await mkdir(out,{recursive:true});
const lostContext=process.env.LILO_LOST_WEBGL==="1";
const browser=await chromium.launch({executablePath:process.env.LILO_CHROMIUM||chromium.executablePath(),args:lostContext?
  ["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]:["--disable-webgl"]});
const page=await browser.newPage({viewport:{width:900,height:700}});
if(lostContext)await page.addInitScript(()=>{
  const getContext=HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext=function(type,...args){
    const context=getContext.call(this,type,...args);
    if(type.startsWith("webgl")&&context&&!context.isContextLost())context.getExtension("WEBGL_lose_context")?.loseContext();
    return context;
  };
});
const errors=[];page.on("pageerror",e=>errors.push(e.message));
await page.route("**/renderer-check",r=>r.fulfill({contentType:"text/html",body:'<!DOCTYPE html><html><body style="margin:0;background:white"></body></html>'}));
try {
  await page.goto((process.env.LILO_URL||"http://127.0.0.1:5173")+"/renderer-check");
  const checks=await page.evaluate(async()=>{
    const {Scene}=await import("/src/canvas/scene.ts");
    const host=document.createElement("div");host.style.cssText="width:900px;height:700px";document.body.append(host);
    const scene=await Scene.create(host,{grid:0x888888,gridMajor:0x666666,hoop:0x333333,accent:0xff00ff,needle:0xffff00});
    const checks=[];
    const check=(name,condition,detail)=>{if(!condition)throw Error(name+": "+JSON.stringify(detail));checks.push({name,result:"pass",detail});};
    check("Broken WebGL chooses Canvas 2D",!!scene.app.canvas.getContext("2d"),scene.app.renderer.type);
    const frame=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const pixel=(x,y)=>Array.from(scene.app.canvas.getContext("2d").getImageData(x,y,1,1).data);
    const thread=(hex,id)=>({id,brand:"Test",code:id,name:id,hex});
    const s=(x,y,threadIndex=0,type="stitch")=>({x,y,threadIndex,type,objectIndex:0});
    const plan={threads:[thread("#ff0000","r"),thread("#0000ff","b")],stitches:[s(5,10),s(25,10),s(25,20),s(5,20),s(5,30,1,"colorChange"),s(5,30,1),s(25,30,1)],warnings:[]};
    scene.setGridVisible(false);scene.setView({x:100,y:100,zoom:10});
    scene.setPlan(plan,{realistic:false,jumps:false});scene.setProgress(7,false);await frame();
    check("Two thread colours drawn from mesh",pixel(250,200)[0]>240&&pixel(250,400)[2]>240,{red:pixel(250,200),blue:pixel(250,400)});
    scene.setProgress(0,false);await frame();check("Simulation zero clears stitch geometry",pixel(250,200)[3]===0,pixel(250,200));
    scene.setProgress(2,false);await frame();check("Simulation reveals partial geometry",pixel(250,200)[0]>240&&pixel(250,400)[3]===0,{red:pixel(250,200),blue:pixel(250,400)});
    scene.setProgress(7,false);await frame();scene.setProgress(2,false);await frame();
    check("Simulation rewind invalidates cached path",pixel(250,400)[3]===0,pixel(250,400));
    scene.setProgress(7,false);scene.setView({x:200,y:50,zoom:5});await frame();
    check("Pan and zoom transform the existing geometry",pixel(275,100)[0]>240&&pixel(350,200)[3]===0,{moved:pixel(275,100),old:pixel(350,200)});
    scene.setView({x:100,y:100,zoom:10});scene.setStitchAlpha(.5);await frame();
    check("Stitch opacity retained",Math.abs(pixel(250,200)[3]-128)<3,pixel(250,200));scene.setStitchAlpha(1);
    scene.setPlan(plan,{realistic:true,jumps:true});scene.setProgress(7,false);await frame();
    check("Realistic thread shading retained",pixel(250,200)[0]>200&&pixel(250,200)[3]>240,pixel(250,200));
    const source=document.createElement("canvas");source.width=source.height=10;const ctx=source.getContext("2d");ctx.fillStyle="#00ff00";ctx.fillRect(0,0,10,10);
    const picture={src:source,x:10,y:9,widthMm:10,heightMm:2,alpha:1,band:0};
    scene.setRefImages([picture]);await frame();check("Image behind stitches",pixel(250,200)[0]>200,pixel(250,200));
    scene.setRefImages([{...picture,band:1}]);await frame();check("Image above stitches",pixel(250,200)[1]>240,pixel(250,200));
    scene.setRefImages([]);
    let renders=0;const render=scene.app.render.bind(scene.app);scene.app.render=()=>{renders++;render();};
    await frame();renders=0;await new Promise(r=>setTimeout(r,350));
    check("Software canvas stays idle without changes",renders===0,renders);
    scene.setView({x:101,y:100,zoom:10});await frame();check("View change schedules one redraw",renders===1,renders);
    const large={threads:[thread("#0000ff","b")],warnings:[],stitches:Array.from({length:100001},(_,i)=>s((i%200)*.15,Math.floor(i/200)*.06))};
    const start=performance.now();scene.setView({x:100,y:100,zoom:10});scene.setPlan(large,{realistic:true,jumps:true});scene.setProgress(large.stitches.length,false);await frame();
    const milliseconds=performance.now()-start;
    check("Large design draws with chunked geometry",pixel(250,200)[2]>100&&milliseconds<15000,{stitches:100001,initialMilliseconds:Math.round(milliseconds)});
    window.testScene=scene;
    return checks;
  });
  assert.deepEqual(errors,[]);
  await page.screenshot({path:join(out,"large-design-canvas2d.png")});
  await writeFile(join(out,lostContext?"lost-context-results.json":"results.json"),JSON.stringify({result:"pass",checks,errors,webglDisabled:!lostContext,lostWebGLContext:lostContext},null,2)+"\n");
  console.log(JSON.stringify(checks,null,2));
} finally {await browser.close();}
