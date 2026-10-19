import { beforeEach, expect, it, vi } from "vitest";
const invoke = vi.hoisted(() => vi.fn());
const check = vi.hoisted(() => vi.fn());
vi.mock("@tauri-apps/api/core", () => ({ invoke }));
vi.mock("@tauri-apps/plugin-updater", () => ({ check }));
vi.mock("@tauri-apps/plugin-process", () => ({ relaunch: vi.fn() }));
import { tauriUpdater } from "./backend";
beforeEach(() => { vi.clearAllMocks(); invoke.mockResolvedValue(false); });
it("explains that private review updates are disabled", async () => {
  expect(await tauriUpdater.unavailableReason()).toContain("disabled");
});
it("refuses a direct updater check before contacting any update service", async () => {
  await expect(tauriUpdater.check()).rejects.toThrow("disabled");
  expect(check).not.toHaveBeenCalled();
});
