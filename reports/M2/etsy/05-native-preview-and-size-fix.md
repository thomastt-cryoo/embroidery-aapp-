# M2 checkpoint 5 — native Mac preview and package size fixed

20 October 2026. This checkpoint supersedes the size and preview blockers described in checkpoints 3 and 4. It does not describe those earlier failed tests as passing.

## Completed

The application now uses its existing WebGL renderer when graphics are healthy and a Canvas 2D renderer when WebGL is missing or already lost. The fallback draws the existing stitch mesh, using its existing coordinates, triangles and colours. It also preserves images, layers, selection, hoop graphics, zoom/pan and stitch simulation. It caches paths and draws on demand, avoiding continuous idle rendering. The embroidery engine, stitch geometry and approved M1 layout were preserved.

An independent native WebKit probe reproduced immediately lost WebGL contexts without loading any embroidery code. This exposed a second Pixi shader-probe path on Intel: the final startup adapter prevents the software renderer's own canvases from requesting failed WebGL contexts. It does not change the browser's global canvas API or engine processing.

The complete universal Mac ZIP now measures **19,870,862 bytes**, below 20,000,000. A build-only compressor uses a longer compression window across the duplicated assets in the Intel and Apple Silicon executable slices. The decoded installer payload is byte-identical before and after compression. Native extraction verified identical files, permissions and signatures. Customers receive a normal Apple PKG installer, with no scripts to run and no application-component downloads.

The final Windows ZIP measures **16,955,299 bytes**. Both final packages contain application source `2204598af6c3bfcd9667d68d91958e21cd8d1fc5`. Later commits change test drivers and reports only.

## Tests and results

- Native final-ZIP installation and project/PES loading passed on Apple Silicon and Intel macOS runners.
- The final Mac app visibly drew red and blue stitches with the original reference picture hidden on both architectures. Intel's actual screenshot contained 1,176 red and 3,486 blue pixels in the central drawing area; conversion, simulation and hoop selection also passed there. Complete workflow reruns continue in checkpoint 6.
- Final Windows ZIP: 11 native checks passed, including healthy GPU rendering, deliberately lost-WebGL fallback, PNG conversion, editing/undo, hoop, simulation, save/reopen, native PES export and normal launch without debugging.
- Software rendering integration passed 13 checks; a genuinely created then lost WebGL context passed 14 checks. These cover partial simulation/rewind, colours, transparency, pictures above/below stitches, pan/zoom, idle redraw and a 100,001-stitch fixture.
- Production browser fallback checks passed conversion, editing, hoop, simulation, project save/reopen and all 13 export formats while external HTTP(S) was blocked. These are supporting browser tests, separately recorded from native app tests.
- Source preservation/identity guard passed. All 458 frontend runtime files remain; 137 preview optimizations retain exact pixels and colour profiles.

## Problems and limitations

Earlier Mac native test runs failed for several reasons: a native driver CGFloat cast, Safari slider keyboard differences, clipboard timing and a restore-edit assertion. Those failures are retained. Runner-only fixes do not change the sealed customer ZIP. Final workflow completion is still required before the final report.

Windows is unsigned. Mac has an ad-hoc signature, without Developer ID or notarization. Consumer trust-prompt journeys, physical Mac GPU rendering and physical embroidery-machine sew-out are not certified by runner tests.

## Evidence and next step

[Lossless Mac payload verification](macos-fixed/mac-lossless-pkg-compression.json), [Mac package manifest](macos-fixed/mac-selected-package.json), [final Windows native checks](windows-native-final/results.json), [real lost-context tests](renderer-integration/lost-context-results.json), [fallback workflow checks](graphics-fallback-browser/results.json).

![Final installed Windows app](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/windows-native-final/normal-launch.jpg>)

Actual installed Mac app, Apple Silicon, with the reference picture hidden:

![Native Apple Silicon stitch preview](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/graphics-native-confirmed/arm-preview.png>)

Actual installed Mac app, Intel, with the reference picture hidden:

![Native Intel stitch preview](<C:/Users/mazin/Downloads/embroidry app/reports/M2/etsy/graphics-native-confirmed/intel-preview.png>)

Next: finish native Mac editing/save/reopen/export on the exact ZIP on both architectures, validate final archive hashes and write the final M2 report. Do not begin M3.
