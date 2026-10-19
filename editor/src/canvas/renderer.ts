import { Application, DOMAdapter, type ApplicationOptions } from "pixi.js";
import { registerCanvasStitchMeshes } from "./canvasMeshPipe";

let softwareAdapterInstalled = false;
function useSoftwareCanvasAdapter(): void {
  if (softwareAdapterInstalled) return;
  const adapter = DOMAdapter.get();
  DOMAdapter.set({
    ...adapter,
    createCanvas(width, height) {
      const canvas = adapter.createCanvas(width, height);
      const getContext = canvas.getContext.bind(canvas);
      // Pixi's shared batch shader probes WebGL even for its Canvas renderer.
      // A lost-but-non-null WebKit context crashes that precision query. Keep
      // software rendering independent of GPU probes on Pixi-owned canvases;
      // the browser and the embroidery engine's image canvases are untouched.
      canvas.getContext = ((kind: Parameters<typeof canvas.getContext>[0], options?: Parameters<typeof canvas.getContext>[1]) => {
        if (["webgl", "webgl2", "experimental-webgl"].includes(kind)) return null;
        return getContext(kind, options);
      }) as typeof canvas.getContext;
      return canvas;
    },
  });
  softwareAdapterInstalled = true;
}

/** A context object can exist even when the Mac VM has immediately lost it.
 * Check the same precision query used by Pixi rather than accepting a truthy
 * getContext result. A broken GPU must not prevent the editor from drawing. */
export function hasWorkingWebGL(): boolean {
  let gl: WebGLRenderingContext | null = null;
  try {
    gl = document.createElement("canvas").getContext("webgl");
    return !!gl && !gl.isContextLost() && !!gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_FLOAT);
  } catch {
    return false;
  } finally {
    try { gl?.getExtension("WEBGL_lose_context")?.loseContext(); } catch { /* lost driver context */ }
  }
}

export async function createDrawingApplication(options: Partial<ApplicationOptions>): Promise<Application> {
  registerCanvasStitchMeshes();
  const useGPU = !softwareAdapterInstalled && hasWorkingWebGL();
  if (!useGPU) useSoftwareCanvasAdapter();
  let app = new Application();
  try {
    await app.init({ ...options, preference: [useGPU ? "webgl" : "canvas"] });
  } catch (error) {
    if (!useGPU) throw error;
    // Drivers can lose a context between the capability check and startup.
    // Dispose the failed instance where possible, then use a fresh 2D canvas.
    try { app.destroy({ removeView: true }, { children: true }); } catch { /* partially initialized renderer */ }
    useSoftwareCanvasAdapter();
    app = new Application();
    await app.init({ ...options, preference: ["canvas"] });
  }
  return app;
}
