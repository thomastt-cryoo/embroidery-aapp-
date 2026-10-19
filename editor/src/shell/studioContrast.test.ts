import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const css = readFileSync(new URL("../studio.css", import.meta.url), "utf8");
const block = (selector: string) => {
  const start = css.indexOf(`${selector} {`);
  return css.slice(start, css.indexOf("\n}", start));
};
const tokens = (s: string) => Object.fromEntries([...s.matchAll(/--([a-z0-9-]+):\s*(#[a-f0-9]{6})\s*;/gi)].map(m => [m[1], m[2]]));
const luminance = (hex: string) => {
  const c = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255).map(s => s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4);
  return c[0] * 0.2126 + c[1] * 0.7152 + c[2] * 0.0722;
};
describe.each(["light", "dark"])("studio contrast (%s)", theme => {
  const v = { ...tokens(block(":root")), ...(theme === "dark" ? tokens(block(':root[data-theme="dark"]')) : {}) };
  for (const [fg, bg] of [["text", "bg"], ["text", "surface"], ["muted", "surface"], ["muted", "surface-2"], ["accent-text", "accent"]]) {
    it(`${fg} on ${bg} passes WCAG AA`, () => {
      const a = luminance(v[fg]), b = luminance(v[bg]);
      expect((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)).toBeGreaterThanOrEqual(4.5);
    });
  }
});
