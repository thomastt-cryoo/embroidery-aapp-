import iconUrl from "../assets/brand/embrova-logo.png";

/** The owner's complete supplied flower and wordmark, fitted without cropping. */
export function BrandMark({ size = 24 }: { size?: number }) {
  return <img className="brand-mark" src={iconUrl} width={size} height={size} alt="" draggable={false} />;
}
