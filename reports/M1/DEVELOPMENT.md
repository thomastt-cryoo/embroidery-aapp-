# Reproducing M1 checks

Use the repository's locked dependencies and prepare its bundled fonts with the existing scripts. No embroidery engine, editor state, project manager, platform I/O or native Rust implementation was changed.

## Build

```powershell
pnpm install --frozen-lockfile
pnpm guide
pnpm guide:check
pnpm --filter editor build
pnpm tauri build --no-bundle --config src-tauri/tauri.m1.conf.json
```

The preview configuration has its own app identifier and does not register the installed app's URL scheme. The normal Tauri configuration remains available for the standard Windows/macOS application. `.cargo/config.toml` limits native builds to two jobs to reduce memory pressure.

## Tests

Run heavy suites sequentially on a machine with limited free memory. M1 verification used Node 24.19.0, a single Vitest worker and the thread pool:

```powershell
pnpm test:scripts
pnpm --filter editor test --pool=threads --maxWorkers=1 --testTimeout=120000
pnpm --filter @lilo/engine test --pool=threads --maxWorkers=1 --testTimeout=120000
```

The existing browser journeys use `LILO_CHROMIUM` to locate Chrome and `LILO_SHOTS` to choose their evidence folder. Their Vite cache is isolated from a running development server.

## Production acceptance check

Serve `editor/dist` on local port 4173, then run:

```powershell
$env:LILO_PRODUCTION='1'
$env:LILO_URL='http://127.0.0.1:4173'
$env:LILO_CHROMIUM='C:\Program Files\Google\Chrome\Application\chrome.exe'
node scripts/m1-ui-check.mjs
```

This uses real file inputs and downloads, blocks external HTTP(S), checks three window sizes, generates embroidery, changes the hoop while editing, runs simulation, exports every format, reopens every readable machine file, and saves/reopens a Lilo project. It writes screenshots, the actual files and `results.json` to `reports/M1/evidence/acceptance`.

For development with the repository's sample projects and in-memory file dialogs, run `pnpm dev` and omit `LILO_PRODUCTION` and `LILO_URL` before running the same script. That mode still uses the real embroidery engine.

## Protected source audit

```powershell
git diff c82a9d7 -- engine editor/src/state editor/src/platform editor/src/project app/src-tauri/src
```

The result must be empty. The final report records the commit and the native preview checksum.
