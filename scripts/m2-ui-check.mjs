/** Reproducible M1 acceptance checks against the real frontend and engine.
 * Start `pnpm dev` first. `?mock` replaces only desktop dialogs/storage with the upstream test platform.
 * No engine results are mocked. Run: node scripts/m1-ui-check.mjs
 */
import { createRequire } from "node:module";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve, join } from "node:path";
import assert from "node:assert/strict";

const repo = resolve(import.meta.dirname, "..");
const require = createRequire(join(repo, "editor/package.json"));
const { chromium } = require("playwright-core");
const out = join(repo, "reports/M2/evidence/acceptance");
const production = process.env.LILO_PRODUCTION === "1";
const appUrl = `${process.env.LILO_URL || "http://localhost:5173"}/${production ? "" : "?mock"}`;
await mkdir(join(out, "exports"), { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.LILO_CHROMIUM || chromium.executablePath(), args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const context = await browser.newContext({ viewport: { width: 1440, height: 960 } });
const remoteRequests = [];
await context.route(/^https?:/, route => {
  const host = new URL(route.request().url()).hostname;
  if (["localhost", "127.0.0.1", "[::1]"].includes(host)) return route.continue();
  remoteRequests.push(route.request().url());
  return route.abort();
});
const page = await context.newPage();
page.setDefaultTimeout(60_000);
page.setDefaultNavigationTimeout(120_000);
const problems = [];
const checks = [];
page.on("pageerror", e => problems.push(e.message));
page.on("console", m => { if (m.type() === "error") problems.push(m.text()); });
const check = (name, detail) => { checks.push({ name, result: "pass", detail }); console.log(`PASS ${name}: ${detail}`); };
const shot = name => page.screenshot({ path: join(out, `${name}.png`) });
try {
  await page.goto(appUrl);
  await page.getByRole("button", { name: "Upload image", exact: true }).waitFor();
  // A clean production profile offers the first-launch tour. Esc dismisses its welcome dialog.
  await page.keyboard.press("Escape");
  await shot("home-light");
  const png = await readFile(join(repo, "engine/test/fixtures/k-logo.png"));
  if (production) {
    // The production build uses real browser file inputs and downloads; no test platform is installed.
    const [chosen] = await Promise.all([page.waitForEvent("filechooser"), page.getByRole("button", { name: "Upload image", exact: true }).click()]);
    await chosen.setFiles({ name: "k-logo.png", mimeType: "image/png", buffer: png });
  } else {
    await page.evaluate(b => { window.__lilo.state.pickFiles = [{ name: "k-logo.png", bytes: new Uint8Array(b) }]; }, [...png]);
    await page.getByRole("button", { name: "Upload image", exact: true }).click();
  }
  await page.getByLabel("Design totals").waitFor({ timeout: 90_000 });
  await page.getByRole("button", { name: "Skip", exact: true }).click({ timeout: 1000 }).catch(() => {});
  const totals = await page.getByLabel("Design totals").innerText();
  assert.match(totals, /stitches/);
  check("PNG conversion", totals.replaceAll("\n", "; "));
  await shot("generated-light");

  // Select a real generated object; the contextual editor and hoop remain available together.
  await page.locator("li.seq-row").last().click();
  const workspace = page.getByRole("region", { name: "Hoop and workspace" });
  await workspace.getByRole("button", { name: /^Hoop:/ }).click();
  const picker = page.getByRole("dialog", { name: "Choose a hoop" });
  await picker.getByLabel("Search hoops").fill("100x100");
  await shot("hoop-picker");
  await picker.getByRole("list", { name: "Search results" }).getByRole("button").first().click();
  await picker.waitFor({ state: "detached" });
  assert.match(await workspace.getByRole("button", { name: /^Hoop:/ }).getAttribute("aria-label"), /100 × 100/);
  check("Hoop while editing", "Selected a 100 × 100 mm hoop with a generated shape selected");
  await page.getByRole("button", { name: "Fit", exact: true }).click();
  await shot("editing-and-hoop");
  await page.keyboard.press("Escape");

  for (const size of [{ width: 960, height: 600 }, { width: 1280, height: 800 }, { width: 1440, height: 960 }]) {
    await page.setViewportSize(size);
    await page.getByRole("button", { name: "Appearance", exact: true }).click();
    const menu = page.getByRole("dialog", { name: "Appearance" });
    const box = await menu.boundingBox();
    assert(box && box.x >= 0 && box.y >= 0 && box.x + box.width <= size.width && box.y + box.height <= size.height);
    await menu.getByRole("button", { name: "Dark", exact: true }).click();
    await page.keyboard.press("Escape");
    const layout = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, viewport: innerWidth, canvas: document.querySelector(".canvas").getBoundingClientRect().width, theme: document.documentElement.dataset.theme }));
    assert(layout.width <= layout.viewport);
    assert(layout.canvas >= 300);
    assert.equal(layout.theme, "dark");
    await shot(`dark-${size.width}x${size.height}`);
    check(`Layout ${size.width} × ${size.height}`, `No horizontal overflow; canvas ${layout.canvas}px; appearance menu inside window`);
  }

  // Real player and realistic preview.
  const player = page.getByRole("group", { name: "Stitch player" });
  await player.getByLabel("Scrub stitches").fill("0");
  await player.getByLabel("Playback speed").fill("50");
  await player.getByRole("checkbox", { name: "Auto-continue" }).check();
  await player.getByRole("button", { name: "Play", exact: true }).click();
  await player.getByRole("button", { name: "Play", exact: true }).waitFor({ timeout: 90_000 });
  check("Simulation", "Playback completed at 50× with auto-continue enabled");
  await shot("preview-dark");

  // Export every currently offered format, then reopen each machine file through the existing reader.
  const exports = [];
  for (let i = 0; i < 13; i++) {
    await page.getByRole("button", { name: "Export", exact: true }).first().click();
    const dialog = page.getByRole("dialog", { name: "Export" });
    const choices = dialog.getByRole("radiogroup", { name: "File format" }).getByRole("radio");
    assert.equal(await choices.count(), 13);
    await choices.nth(i).click();
    await dialog.getByLabel("Export stats").waitFor({ timeout: 60_000 });
    if (i === 0 || i === 12) await shot(`export-${i}`);
    const downloading = production ? page.waitForEvent("download") : null;
    await dialog.getByRole("button", { name: /^Save/ }).click();
    await dialog.waitFor({ state: "detached" });
    let file;
    if (downloading) {
      const download = await downloading;
      const name = download.suggestedFilename();
      await download.saveAs(join(out, "exports", name));
      file = { name, bytes: [...await readFile(join(out, "exports", name))] };
    } else file = await page.evaluate(() => { const s = window.__lilo.state.saved.at(-1); return { name: s.name, bytes: [...s.bytes] }; });
    await writeFile(join(out, "exports", file.name), new Uint8Array(file.bytes));
    let stitches = null;
    if (file.name.endsWith(".gcode")) {
      const text = new TextDecoder().decode(new Uint8Array(file.bytes));
      assert.match(text, /G[01].*X/);
      assert(text.split("\n").length > 500);
    } else if (!file.name.endsWith(".png")) {
      if (!production) {
        stitches = await page.evaluate(async ({ bytes, name, root }) => { const engine = await import(`/@fs/${root}/engine/src/index.ts`); const r = engine.readEmbroidery(new Uint8Array(bytes), name.split(".").pop()); return r.plan.stitches.filter(s => s.type === "stitch").length; }, { ...file, root: repo.replaceAll("\\", "/") });
        assert(stitches > 500);
      }
    } else assert.deepEqual(file.bytes.slice(0, 8), [137, 80, 78, 71, 13, 10, 26, 10]);
    exports.push({ name: file.name, bytes: file.bytes.length, stitches });
  }
  if (production) {
    for (const file of exports.filter(f => !/\.(png|gcode)$/.test(f.name))) {
      const reader = await context.newPage();
      reader.setDefaultNavigationTimeout(120_000);
      await reader.goto(appUrl);
      const [chosen] = await Promise.all([reader.waitForEvent("filechooser"), reader.getByRole("button", { name: "Open…", exact: true }).click()]);
      await chosen.setFiles(join(out, "exports", file.name));
      const totals = await reader.getByLabel("Design totals").innerText({ timeout: 120_000 });
      file.stitches = Number(/\/ ([\d,]+) stitches/.exec(totals)?.[1].replaceAll(",", ""));
      assert(file.stitches > 500, `${file.name}: ${totals}`);
      await reader.close();
    }
  }
  check("All exports", `${exports.length} files written; 11 readable machine formats re-read, write-only G-code checked, and PNG signature verified`);
  if (production) {
    const downloading = page.waitForEvent("download");
    await page.keyboard.press("Control+s");
    const download = await downloading;
    const name = download.suggestedFilename();
    assert(name.endsWith(".lilo"));
    const projectPath = join(out, "exports", name);
    await download.saveAs(projectPath);
    const reopened = await context.newPage();
    reopened.setDefaultNavigationTimeout(120_000);
    await reopened.goto(appUrl);
    const [chosen] = await Promise.all([reopened.waitForEvent("filechooser"), reopened.getByRole("button", { name: "Open…", exact: true }).click()]);
    await chosen.setFiles(projectPath);
    const reopenedTotals = await reopened.getByLabel("Design totals").innerText({ timeout: 120_000 });
    assert.match(reopenedTotals, /1,374 stitches/);
    await reopened.screenshot({ path: join(out, "project-reopened.png") });
    await reopened.close();
    check("Project save and reopen", `${name}: ${reopenedTotals.replaceAll("\n", "; ")}`);
  }
  assert.equal(problems.length, 0, problems.join("\n"));
  check("Offline processing", "External HTTP(S) blocked throughout conversion, editing, simulation, export and project round-trip");
  await writeFile(join(out, "results.json"), JSON.stringify({ production, externalNetworkBlocked: true, remoteRequests, checks, exports, problems }, null, 2));
} catch (error) {
  await shot("FAILED").catch(() => {});
  await writeFile(join(out, "results.json"), JSON.stringify({ checks, problems, failure: String(error) }, null, 2));
  throw error;
} finally { await browser.close(); }
