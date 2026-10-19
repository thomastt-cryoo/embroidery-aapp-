import { ExtensionType, extensions, Texture, type CanvasRenderer, type InstructionSet, type Mesh, type MeshGeometry } from "pixi.js";

interface CachedPath {
  geometry: MeshGeometry;
  positions: Float32Array;
  indices: Uint32Array | Uint16Array;
  count: number;
  path: Path2D;
}

/** Canvas counterpart of the existing solid-colour stitch meshes. Geometry,
 * colour, layer order, view transforms and reveal counts come from StitchLayer.
 * This is only a drawing backend; it never generates or changes stitches. */
export class CanvasStitchMeshPipe {
  static extension = { type: ExtensionType.CanvasPipes, name: "mesh" } as const;
  private paths = new WeakMap<Mesh, CachedPath>();

  constructor(private renderer: CanvasRenderer) {}

  validateRenderable(): boolean { return false; }
  updateRenderable(): void {}
  destroyRenderable(mesh: Mesh): void { this.paths.delete(mesh); }

  addRenderable(mesh: Mesh, instructions: InstructionSet): void {
    this.renderer.renderPipes.batch.break(instructions);
    instructions.add(mesh);
  }

  execute(mesh: Mesh): void {
    if (!mesh.isRenderable) return;
    if (mesh.texture !== Texture.WHITE) throw new Error("The stitch canvas expects solid-colour mesh geometry.");
    const geometry = mesh.geometry as MeshGeometry;
    const positions = geometry.positions;
    const indices = geometry.indices;
    const count = geometry.indexCount || indices.length;
    let cached = this.paths.get(mesh);
    if (!cached || cached.geometry !== geometry || cached.positions !== positions || cached.indices !== indices || count < cached.count) {
      cached = { geometry, positions, indices, count: 0, path: new Path2D() };
      this.paths.set(mesh, cached);
    }
    // Playback normally grows one partial chunk. Append only newly revealed
    // triangles; fully visible chunks keep their cached native paths.
    for (let i = cached.count; i < count; i += 3) {
      const a = indices[i] * 2;
      const b = indices[i + 1] * 2;
      const c = indices[i + 2] * 2;
      cached.path.moveTo(positions[a], positions[a + 1]);
      // The mesh's end caps have the opposite winding from its rectangles.
      // Normalize winding so overlapping native path triangles never cancel.
      const cross = (positions[b] - positions[a]) * (positions[c + 1] - positions[a + 1]) - (positions[b + 1] - positions[a + 1]) * (positions[c] - positions[a]);
      const first = cross < 0 ? c : b;
      const second = cross < 0 ? b : c;
      cached.path.lineTo(positions[first], positions[first + 1]);
      cached.path.lineTo(positions[second], positions[second + 1]);
      cached.path.closePath();
    }
    cached.count = count;
    const renderer = this.renderer;
    const global = renderer.globalUniforms.globalUniformData?.worldColor ?? 0xffffffff;
    const group = mesh.groupColorAlpha;
    // Pixi stores group tint as ABGR; Canvas uses RGB.
    const channel = (shift: number) => Math.round(((group >>> shift) & 255) * ((global >>> shift) & 255) / 255);
    const alpha = ((group >>> 24) & 255) / 255 * ((global >>> 24) & 255) / 255;
    if (alpha <= 0) return;
    const system = renderer.canvasContext;
    const context = system.activeContext;
    system.setBlendMode(mesh.groupBlendMode);
    context.save();
    system.setContextTransform(mesh.groupTransform);
    context.globalAlpha = alpha;
    context.fillStyle = `rgb(${channel(0)},${channel(8)},${channel(16)})`;
    context.fill(cached.path);
    context.restore();
  }

  destroy(): void { this.paths = new WeakMap(); }
}

let registered = false;
export function registerCanvasStitchMeshes(): void {
  if (registered) return;
  extensions.add(CanvasStitchMeshPipe);
  registered = true;
}
