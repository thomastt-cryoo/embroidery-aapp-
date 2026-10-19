import iconUrl from "../assets/brand/studio-icon.svg";

/** Temporary Embroidery Studio hoop-and-stitch identity. */
export function BrandMark({ size = 24 }: { size?: number }) {
  return <img className="brand-mark" src={iconUrl} width={size} height={size} alt="" draggable={false} />;
}
