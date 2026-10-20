# M2 checkpoint 4 — native Mac graphics diagnosis

**Historical diagnosis.** Checkpoint 5 implements and validates a Canvas 2D startup fallback for these lost WebGL contexts. The original diagnostic findings below are retained.

## Completed

Investigated the native canvas error found after dismissing the welcome on the Intel Mac runner. The renderer's startup shader query returned null, while conversion still produced the correct **1,374 stitches** and six objects. Native hoop selection also worked. The embroidery engine, M1 interface and graphics initialization code remain unchanged.

Built and ran a **separate native WKWebView diagnostic**, outside the application. It loads no embroidery JavaScript, assets, Tauri shell or engine. It uses Apple's default public WebKit configuration and reads the available Metal device without changing settings.

## Tests and results

Actual runner: **macOS 15.7.9, Intel**, exposing **Apple Paravirtual device** through Metal.

| Independent WebKit test | Result |
|---|---|
| WebGL 1, antialiasing off | Context immediately lost; shader precision null; green-pixel readback failed |
| WebGL 1, antialiasing on | Same failure |
| WebGL 2, antialiasing off | Same failure |
| WebGL 2, antialiasing on | Same failure |

Every context reported `isContextLost() = true` and the initial error **37442 (`CONTEXT_LOST_WEBGL`)**. The attempted green pixel read returned `[0,0,0,0]`. This reproduces a native graphics failure without the embroidery application. It supports an environment-level diagnosis for the observed runner failure; it does not prove the application works on physical Mac hardware.

Evidence: [raw JSON](graphics-probe/native-webkit-graphics.json), [private diagnostic run](https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39322724108). Its downloaded evidence archive matched GitHub's SHA-256 `ee862c5a0081e7ba1368a3f58e48463bc69efddfc41d23d8dc46b91fd23de126`.

## Limitations and next

**Native Mac preview approval remains blocked.** Browser tests passed separately using software rendering, but they do not verify native WebKit drawing. Changing stitch processing, removing preview, or merely suppressing the null-query error would not resolve the lost graphics context.

Test the exact ZIP on a physical Mac or a Mac runner with working native graphics. Confirm visible stitches, zoom/pan, realistic preview, simulation, saving/reopening and exports. If the application fails while a standalone native WebView works on that same graphics-capable Mac, investigate the Tauri window and renderer compatibility and make a targeted fix there. Keep the embroidery engine and approved interface intact.

The current free-minute runner environment has been used for the checks it can support. No paid larger runner, new account or billing setting was enabled. No consumer Mac is connected to this Windows workspace, so a physical-Mac preview pass cannot be honestly claimed here. M3 has not started.
