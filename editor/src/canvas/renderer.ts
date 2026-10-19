import { Application, type ApplicationOptions } from "pixi.js";
import { registerCanvasStitchMeshes } from "./canvasMeshPipe";

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
    gl?.getExtension("WEBGL_lose_context")?.loseContext();
  }
}

export async function createDrawingApplication(options: Partial<ApplicationOptions>): Promise<Application> {
  registerCanvasStitchMeshes();
  const useGPU = hasWorkingWebGL();
  let app = new Application();
  try {
    await app.init({ ...options, preference: [useGPU ? "webgl" : "canvas"] });
  } catch (error) {
    if (!useGPU) throw error;
    // Drivers can lose a context between the capability check and startup.
    // Dispose the failed instance where possible, then use a fresh 2D canvas.
    try { app.destroy({ removeView: true }, { children: true }); } catch { /* partially initialized renderer */ }
    app = new Application();
    await app.init({ ...options, preference: ["canvas"] });
  }
  return app;
}
