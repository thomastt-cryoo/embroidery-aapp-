/** Real frontend layout checks, including Tauri's Mac overlay attribute.
 * Browser checks on the current host, not native Mac installation evidence. */
import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import assert from 'node:assert/strict';

const root = resolve(import.meta.dirname, '..');
const require = createRequire(join(root, 'editor/package.json'));
const { chromium } = require('playwright-core');
const baseline = process.env.NAV_BASELINE === '1';
const out = resolve(root, process.env.NAV_EVIDENCE_OUT || 'reports/mac-sidebar-fix');
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
const checks = [], errors = [];
const check = (name, detail) => { checks.push({ name, detail }); console.log('PASS', name); };
try {
  for (const platform of baseline ? ['mac'] : ['mac', 'windows']) {
    const context = await browser.newContext({ viewport: { width: 1024, height: 678 },
      userAgent: platform === 'mac' ? 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/18.5 Safari/605.1.15' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' });
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(`${process.env.NAV_URL || 'http://127.0.0.1:5181'}/?mock`);
    await page.getByRole('button', { name: 'Upload image', exact: true }).waitFor();
    await page.keyboard.press('Escape');
    await page.waitForFunction(expected => document.documentElement.dataset.titlebar === expected, platform === 'mac' ? 'overlay' : 'none');
    const measure = () => page.locator('.app-nav').evaluate(nav => {
      const bounds = nav.getBoundingClientRect();
      const brand = nav.querySelector('.app-wordmark');
      const logo = nav.querySelector('.brand-mark');
      const box = el => { const r = el.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, width: r.width, height: r.height }; };
      const visible = el => getComputedStyle(el).display !== 'none';
      const nodes = [...nav.querySelectorAll('.app-logo, .app-wordmark, :scope > button, .nav-label, :scope > button > svg')].filter(visible);
      return { titlebar: document.documentElement.dataset.titlebar, paddingLeft: parseFloat(getComputedStyle(nav).paddingLeft),
        nav: box(nav), logo: { ...box(logo), objectFit: getComputedStyle(logo).objectFit,
          radius: parseFloat(getComputedStyle(logo).borderRadius), naturalWidth: logo.naturalWidth, naturalHeight: logo.naturalHeight },
        brand: { text: brand.textContent, visible: visible(brand), ...box(brand), scrollWidth: brand.scrollWidth, clientWidth: brand.clientWidth },
        labels: [...nav.querySelectorAll('.nav-label')].filter(visible).map(el => ({ text: el.textContent, lineHeight: parseFloat(getComputedStyle(el).lineHeight), ...box(el) })),
        overflow: nodes.filter(el => { const r = el.getBoundingClientRect(); return r.width && (r.left < bounds.left - 1 || r.right > bounds.right + 1); }).map(el => el.getAttribute('aria-label') || el.textContent),
        documentWidth: document.documentElement.scrollWidth, viewport: innerWidth };
    });
    if (baseline) {
      const before = await measure();
      assert(before.paddingLeft >= 90, JSON.stringify(before));
      assert(before.overflow.length || before.labels.some(l => l.height > l.lineHeight * 1.2), JSON.stringify(before));
      await page.screenshot({ path: join(out, 'before-mac-overlay-1024.png') });
      check('Reproduced Mac overlay sidebar clipping', before);
    } else {
      for (const theme of ['Light', 'Dark']) {
        await page.getByRole('button', { name: 'Appearance', exact: true }).click();
        await page.getByRole('dialog', { name: 'Appearance' }).getByRole('button', { name: theme, exact: true }).click();
        await page.keyboard.press('Escape');
        for (const width of [960, 1000, 1001, 1024, 1280, 1440]) {
          await page.setViewportSize({ width, height: 678 });
          const m = await measure();
          assert.deepEqual(m.overflow, [], JSON.stringify(m));
          assert(m.labels.every(l => l.height <= l.lineHeight * 1.2), JSON.stringify(m));
          assert(m.documentWidth <= m.viewport, JSON.stringify(m));
          assert(m.logo.width <= 36 && m.logo.height <= 36 && m.logo.radius >= 6, JSON.stringify(m));
          assert.equal(m.logo.objectFit, 'contain');
          assert(m.logo.naturalWidth > 0 && m.logo.naturalHeight > 0, 'Logo did not load');
          if (platform === 'mac') assert.equal(m.paddingLeft, width <= 1000 ? 8 : 12);
          if (width > 1000) {
            assert(m.brand.visible && m.brand.width >= m.brand.scrollWidth - 1, JSON.stringify(m));
            assert.equal(m.labels.length, 5);
          }
          check(`${platform} home ${theme} ${width}`, m);
          if (platform === 'mac' && [960, 1024, 1440].includes(width)) await page.screenshot({ path: join(out, `mac-overlay-${width}-${theme.toLowerCase()}.png`) });
        }
      }
      await page.setViewportSize({ width: 1024, height: 678 });
      await page.getByRole('navigation', { name: 'Views' }).getByRole('button', { name: 'Editor', exact: true }).click();
      await page.locator('.app.editor-mode').waitFor();
      const compact = await measure();
      assert.deepEqual(compact.overflow, [], JSON.stringify(compact));
      assert.equal(compact.brand.visible, false);
      if (platform === 'mac') assert.equal(compact.paddingLeft, 8);
      check(`${platform} compact editor rail`, compact);
      if (platform === 'mac') await page.screenshot({ path: join(out, 'mac-editor-rail.png') });
      // Studio Link's label is measured above; opening it requires native IPC
      // that this frontend-only adapter does not provide.
      for (const name of ['Home', 'Pixel art', 'Converter', 'Home']) {
        await page.getByRole('navigation', { name: 'Views' }).getByRole('button', { name, exact: true }).click();
        await page.waitForFunction(id => location.hash === id, { 'Home': '#/', 'Pixel art': '#/pixel', 'Converter': '#/converter', 'Studio Link': '#/link' }[name]);
        await page.locator('.app-loading').waitFor({ state: 'hidden' });
        const m = await measure();
        assert.deepEqual(m.overflow, [], JSON.stringify(m));
        assert(m.labels.every(l => l.height <= l.lineHeight * 1.2), JSON.stringify(m));
        check(`${platform} navigation ${name}`, m);
      }
    }
    await context.close();
  }
  assert.deepEqual(errors, []);
} finally {
  await writeFile(join(out, baseline ? 'baseline.json' : 'browser-results.json'), JSON.stringify({ baseline, nativeMacOS: false, browser: 'Chromium on Windows; real Mac overlay attribute with Tauri development adapter', checks, errors }, null, 2) + '\n');
  await browser.close();
}
