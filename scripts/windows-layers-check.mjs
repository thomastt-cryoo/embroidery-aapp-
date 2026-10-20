/** Desktop Sew order regression checks. Real UI and engine; desktop storage/dialogs use
 * the development adapter. LAYERS_PLATFORM=mac checks a Mac user agent and Command undo
 * in a local browser (not native macOS). WINDOWS_CDP checks a native WebView2 instead. */
import {createRequire} from 'node:module';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import assert from 'node:assert/strict';
const root=resolve(import.meta.dirname,'..');
const require=createRequire(join(root,'editor/package.json'));
const {chromium}=require('playwright-core');
const mac=process.env.LAYERS_PLATFORM==='mac';
const platform=mac?'mac':'windows';
const out=process.env.LAYERS_OUT?resolve(process.env.LAYERS_OUT):join(root,mac?'reports/mac-ui-fix':'reports/windows-ui-fix'); await mkdir(out,{recursive:true});
const native=!!process.env.WINDOWS_CDP;
assert(!(native&&mac),'Mac emulation cannot attach to Windows WebView2');
const browser=native?await chromium.connectOverCDP(process.env.WINDOWS_CDP):await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const context=native?browser.contexts()[0]:await browser.newContext({viewport:{width:1440,height:900},...(mac?{userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/18.5 Safari/605.1.15'}:{})});
if(mac)await context.addInitScript(()=>Object.defineProperty(navigator,'platform',{get:()=> 'MacIntel'}));
const page=native?context.pages()[0]:await context.newPage(); page.setDefaultTimeout(60000);
const checks=[],errors=[];page.on('pageerror',e=>errors.push(e.message));
const check=(name,detail)=>{checks.push({name,result:'pass',detail});console.log('PASS',name,JSON.stringify(detail));};
const rows=()=>page.locator('.seq-row');
const names=()=>rows().locator(':scope > .seq-name').allTextContents();
try{
  if(!native){
    await page.goto(`${process.env.LAYERS_URL||'http://127.0.0.1:5173'}/?mock`);
    await page.getByRole('button',{name:'Upload image',exact:true}).waitFor();
    await page.keyboard.press('Escape');
    const bytes=await readFile(join(root,'engine/test/fixtures/k-logo.png'));
    await page.evaluate(b=>{window.__lilo.state.pickFiles=[{name:'k-logo.png',bytes:new Uint8Array(b)}];},[...bytes]);
    await page.getByRole('button',{name:'Upload image',exact:true}).click();
    await page.getByLabel('Design totals').waitFor();
    await page.getByRole('button',{name:'Skip',exact:true}).click({timeout:1000}).catch(()=>{});
  }
  if(native){
    await page.getByRole('button',{name:'Appearance',exact:true}).click();
    await page.getByRole('dialog',{name:'Appearance'}).getByRole('button',{name:'Light',exact:true}).click();
    await page.keyboard.press('Escape');
  }
  await page.locator('.desktop-layers').waitFor();
  check(`${platform} layout applied${mac?' (browser emulation)':''}`,await page.getByLabel('Design totals').innerText());
  const initial=await names();assert(initial.length>0);
  await page.getByRole('button',{name:'Collapse layer Stitches',exact:true}).click();
  assert.equal(await rows().count(),0);
  await page.getByRole('button',{name:'Expand layer Stitches',exact:true}).click();
  assert.deepEqual(await names(),initial);
  check('Top Stitches expand/collapse',initial);
  await page.locator('.layer-head > .seq-name').click();assert.equal(await rows().count(),0);
  await page.locator('.layer-head > .seq-name').click();assert.deepEqual(await names(),initial);
  check('Clicking the active Stitches heading responds','Clicking the heading collapses and expands its contents');
  assert(await page.getByRole('button',{name:'Move layer Stitches up',exact:true}).isDisabled());
  assert.match(await page.getByRole('button',{name:'Move layer Stitches up',exact:true}).getAttribute('title'),/Only one layer/);
  check('Single-layer arrows explained','No other layer exists to move above/below');
  await page.getByRole('button',{name:'Hide layer Stitches',exact:true}).click();
  await page.getByRole('button',{name:'Show layer Stitches',exact:true}).click();
  await page.getByRole('button',{name:'Lock layer Stitches',exact:true}).click();
  await page.getByRole('button',{name:'Unlock layer Stitches',exact:true}).click();
  check('Layer visibility and locking','Both toggled and restored');
  const first=initial[0];
  await page.getByRole('button',{name:`Move ${first} down`,exact:true}).click();
  assert.notDeepEqual(await names(),initial);
  await page.keyboard.press(mac?'Meta+z':'Control+z'); assert.deepEqual(await names(),initial);
  await page.getByRole('button',{name:`Details for ${first}`,exact:true}).click();
  assert(await page.locator('.row-details').isVisible());
  await page.getByRole('button',{name:`Details for ${first}`,exact:true}).click();
  check('Shape reorder, undo and details',first);
  const blockButton=page.locator('.colour-block button[aria-label$="block down"]:enabled').first();
  await blockButton.click();assert.notDeepEqual(await names(),initial);
  await page.keyboard.press(mac?'Meta+z':'Control+z');assert.deepEqual(await names(),initial);
  check('Colour-block reorder and undo','Whole block reordered then restored');
  await page.locator('.layers-options > summary').click();
  await page.getByRole('button',{name:'New stitch layer',exact:true}).click();
  assert.equal(await page.locator('.layer-head').count(),2);
  assert(await page.locator('.layer-head').first().locator('.layer-move-up').isDisabled());
  assert(await page.locator('.layer-head').first().locator('.layer-move-down').isEnabled());
  await page.locator('.layer-head').first().locator('.layer-move-down').click();
  assert(await page.locator('.layer-head').last().locator('.layer-move-up').isEnabled());
  await page.keyboard.press(mac?'Meta+z':'Control+z');await page.keyboard.press(mac?'Meta+z':'Control+z');
  assert.equal(await page.locator('.layer-head').count(),1);
  await page.locator('.layers-options > summary').click();
  check('Layer options and whole-layer reordering','Added a layer, moved it, undid both operations');
  const sizes=native?[null]:[{width:960,height:600},{width:1280,height:800},{width:1440,height:900}];
  for(const size of sizes){
    if(size)await page.setViewportSize(size);
    const measurements=await page.locator('.desktop-layers').evaluate(el=>{
      const nameEls=[...el.querySelectorAll('.seq-row > .seq-name')];
      const rect=el.getBoundingClientRect();
      return {panelWidth:rect.width,viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,
        names:nameEls.map(e=>({name:e.textContent,width:e.getBoundingClientRect().width})),
        overflow:[...el.querySelectorAll('button,.seq-name')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&getComputedStyle(e).visibility!=='hidden'&&(r.right>rect.right+1||r.left<rect.left-1);}).map(e=>e.getAttribute('aria-label')||e.textContent)};
    });
    assert(measurements.names.every(n=>n.width>=85),JSON.stringify(measurements));
    assert.deepEqual(measurements.overflow,[]);assert(measurements.documentWidth<=measurements.viewport);
    check(`Readable rows ${size?.width||'native'}`,measurements);
    await page.screenshot({path:join(out,`${platform}-${native?'native':size.width}-light.png`)});
  }
  await page.getByRole('button',{name:'Appearance',exact:true}).click();
  await page.getByRole('dialog',{name:'Appearance'}).getByRole('button',{name:'Dark',exact:true}).click();
  await page.keyboard.press('Escape');
  await page.screenshot({path:join(out,`${platform}-${native?'native':'1440'}-dark.png`)});
  check('Dark theme','Same layout rendered in dark mode');
  assert.deepEqual(errors,[]);
}finally{
  await writeFile(join(out,native?'native-ui-results.json':'browser-ui-results.json'),JSON.stringify({platform,nativeMacOS:false,browserEmulation:mac,passed:checks.length,checks,errors},null,2)+'\n');
  await browser.close();
}
