import { useHoop } from "../hoops/autoPick";
import { fmtSize } from "../hoops/format";
import { DesignSection, HoopSelect } from "../panels/DesignSection";

/** Hoop access stays here even while shapes, lettering or click-to-stitch are selected. */
export function WorkspaceCard() {
  const hoop = useHoop();
  return (
    <section className="workspace-card" aria-label="Hoop and workspace">
      <h2>Hoop & size</h2>
      <HoopSelect compact />
      <span className="hoop-size-label">{fmtSize(hoop)} sewing area</span>
      <details>
        <summary>Hoop tools & drawing colour</summary>
        <DesignSection />
      </details>
    </section>
  );
}
