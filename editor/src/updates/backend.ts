import { invoke } from "@tauri-apps/api/core";
import { relaunch } from "@tauri-apps/plugin-process";
import { check } from "@tauri-apps/plugin-updater";
import { getPlatform } from "../platform";
import type { AvailableUpdate, UpdaterBackend } from "./updates";

/** Network timeout for the check, so a dead connection can't leave "Checking…" up forever. */
const CHECK_TIMEOUT_MS = 20_000;

/**
 * The real thing: tauri-plugin-updater against `plugins.updater.endpoints` (GitHub Releases
 * `latest.json`), signature-checked against `app/src-tauri/updater.pub`.
 * https://v2.tauri.app/plugin/updater/#checking-for-updates
 */
export const tauriUpdater: UpdaterBackend = {
  async unavailableReason() {
    // The shell says no while updater.pub is still the placeholder (a build from source or a fork).
    const enabled = await invoke<boolean>("updater_enabled");
    return enabled ? null : "Automatic updates are disabled for this private review build. Install only an Embroidery Studio package supplied for review.";
  },

  async check() {
    if (await tauriUpdater.unavailableReason()) throw new Error("Updates are disabled in this distribution.");
    const update = await check({ timeout: CHECK_TIMEOUT_MS });
    if (!update) return null;
    const found: AvailableUpdate = {
      version: update.version,
      currentVersion: update.currentVersion,
      notes: update.body ?? null,
      async downloadAndInstall(onProgress) {
        let total: number | null = null;
        let done = 0;
        await update.downloadAndInstall((e) => {
          if (e.event === "Started") total = e.data.contentLength ?? null;
          else if (e.event === "Progress") {
            done += e.data.chunkLength;
            onProgress(done, total);
          }
        });
      },
    };
    return found;
  },

  relaunch: () => relaunch(),
};

/** Where there is nothing to update (the browser build). */
export const noUpdater: UpdaterBackend = {
  unavailableReason: async () => "Updates are only available in the Embroidery Studio desktop app.",
  check: async () => null,
  relaunch: async () => {},
};

export const currentBackend = (): UpdaterBackend => (getPlatform().kind === "tauri" ? tauriUpdater : noUpdater);
