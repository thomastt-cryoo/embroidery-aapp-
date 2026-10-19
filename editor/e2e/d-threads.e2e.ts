import { afterAll, describe, expect, it } from "vitest";
import type { Page } from "playwright-core";
import { fixture, openApp, pickFile, stopStack } from "./harness";

afterAll(stopStack);

/** Total stitches in the player bar (0 when there is no plan, the bar then just says to digitize). */
const stitchTotal = async (page: Page): Promise<number> => {
  const totals = page.getByLabel("Design totals");
  if ((await totals.count()) === 0) return 0;
  return Number(/([\d,]+) \/ ([\d,]+) stitches/.exec(await totals.innerText())?.[2].replace(/,/g, "") ?? 0);
};
async function settled(page: Page): Promise<number> {
  let last = -1;
  let stable = 0;
  for (let i = 0; i < 240; i++) {
    await page.waitForTimeout(250);
    const n = await stitchTotal(page);
    const planning = await page.locator(".status-pill").filter({ hasText: "Stitching…" }).count();
    stable = !planning && n === last && n >= 0 ? stable + 1 : 0;
    if (stable >= 3) return n;
    last = n;
  }
  throw new Error(`Stitch planning did not settle; last total was ${last}`);
}
const shelfCodes = (page: Page) => page.getByRole("list", { name: "Spools on my shelf" }).locator("strong").allInnerTexts();

describe("journey d: click to stitch and My Threads", () => {
  it("click-stitches regions of a trace, then fills My Threads three ways and digitizes with them", async () => {
    const j = await openApp("d");
    const { page } = j;
    await j.run(async () => {
      // trace the badge (3 rings and a see-through hole)
      await pickFile(page, "badge.png", fixture("badge.png"));
      await page.getByRole("button", { name: "Digitize a picture…" }).click();
      await page.getByText(/\d[\d,]* \/ [\d,]+ stitches/).waitFor({ timeout: 60_000 });
      const auto = await settled(page);
      expect(auto).toBeGreaterThan(300);

      // click to stitch: leave the automatic result out, then click rings of the trace
      await page.getByRole("button", { name: "Click to stitch…" }).click();
      const panel = page.getByRole("complementary", { name: "Click to stitch" });
      await panel.getByRole("button", { name: "Clear the automatic stitches" }).click();
      expect(await settled(page)).toBeLessThan(auto);
      await j.shot("1-click-stitch-empty");
      const centre = async () => {
        const box = (await page.locator(".canvas-area").boundingBox())!;
        return [box.x + box.width / 2, box.y + box.height / 2] as const;
      };
      const stitchedAt = async (dx: number) => {
        const before = await stitchTotal(page);
        const [cx, cy] = await centre();
        await page.mouse.move(cx + dx, cy);
        await page.mouse.click(cx + dx, cy);
        await page.waitForTimeout(400);
        return (await settled(page)) - before;
      };
      const red = await stitchedAt(5); // the red centre disc
      expect(red).toBeGreaterThan(50);
      await j.shot("2-clicked-red");
      // shift-click two more regions, then stitch them together
      const [cx, cy] = await centre();
      await page.keyboard.down("Shift");
      await page.mouse.click(cx + 43, cy); // gold ring
      await page.mouse.click(cx + 54, cy); // outer navy ring
      await page.keyboard.up("Shift");
      await j.shot("3-two-selected");
      await panel.getByRole("button", { name: /Stitch \d+ selected/ }).click();
      await expect.poll(() => stitchTotal(page), { timeout: 30_000 }).toBeGreaterThan(red + 500);
      await settled(page);
      await j.shot("4-stitched-rings");
      await panel.getByRole("button", { name: "Done" }).click();

      // My Threads: three ways to add a spool
      await page.getByRole("tab", { name: "Threads" }).click();
      const before = await shelfCodes(page);
      expect(before.length).toBe(5);
      // 1. by code, from the catalogue
      await page.getByLabel("Search the catalogue to add a spool").fill("madeira 1000");
      const hits = page.getByRole("list", { name: "Catalogue results" }).getByRole("button");
      await hits.first().waitFor();
      await hits.first().click();
      await expect.poll(async () => (await shelfCodes(page)).length).toBe(before.length + 1);
      await j.shot("5-added-by-code");
      // 2. by photo (the mock platform answers with a Madeira Polyneon 1747 label)
      await page.getByText("Add a spool by photo").click();
      await page.getByRole("button", { name: "Choose a photo…" }).click();
      await page.getByRole("radiogroup").first().waitFor({ timeout: 15_000 });
      await j.shot("6-photo-candidates");
      await page.getByRole("button", { name: "Add this spool" }).click();
      await expect.poll(async () => (await shelfCodes(page)).some((t) => /1747/.test(t))).toBe(true);
      await j.shot("7-added-by-photo");
      // 3. by hand (a spool that is not in any catalogue)
      await page.getByText("Add by hand").click();
      await page.getByLabel("Brand", { exact: true }).fill("Local Mill");
      await page.getByLabel("Code", { exact: true }).fill("B9");
      await page.getByLabel("Name", { exact: true }).fill("Teal");
      await page.getByLabel("Colour", { exact: true }).fill("#118899");
      await page.getByRole("button", { name: "Add to My Threads" }).click();
      await expect.poll(async () => (await shelfCodes(page)).some((t) => /B9/.test(t))).toBe(true);
      const shelf = await shelfCodes(page);
      expect(shelf.length).toBe(before.length + 3);
      await j.shot("8-three-ways");

      // use my threads in Auto digitize: every colour of the result is a spool from the shelf
      await page.getByRole("tab", { name: "Layers" }).click();
      await page.keyboard.press("Escape"); // nothing selected: the Auto digitize panel is back
      await page.getByText("Advanced generation settings", { exact: true }).click();
      await page.getByLabel("Use my threads").check();
      await page.getByRole("button", { name: "Generate stitches", exact: true }).click({ timeout: 120_000 });
      // wait for the NEW result: the button reads "Digitizing…" while it runs, and the old palette is still on screen until then
      await page.getByRole("button", { name: "Digitizing…" }).waitFor({ timeout: 5_000 }).catch(() => undefined);
      await page.getByRole("button", { name: "Generate stitches", exact: true }).waitFor({ timeout: 60_000 });
      await expect.poll(() => page.getByLabel("Palette").getByRole("listitem").count(), { timeout: 60_000 }).toBeGreaterThan(1);
      await settled(page);
      const used = await page.getByLabel("Palette").getByRole("listitem").locator("strong").allInnerTexts();
      const shelfTexts = shelf.map((t) => t.replace(/\s+/g, " ").trim());
      for (const u of used) {
        const code = u.trim().split(" ").pop()!;
        expect(shelfTexts.some((t) => t.endsWith(code)), `${u} should be on the shelf (${shelfTexts.join(" | ")})`).toBe(true);
      }
      await j.shot("9-digitized-with-my-threads");

      j.expectClean();
    });
  });
});
