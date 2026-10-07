import type { PestDetectionItem } from '../types/predict';
import type { BoundingBox } from '../types/crop';

/** Convert YOLO pixel boxes to percentage overlay (assumes ~640 inference size). */
export function pestsToOverlayBoxes(
  pests: PestDetectionItem[],
  refWidth = 640,
  refHeight = 640
): BoundingBox[] {
  return pests.map((p, i) => {
    const [x1, y1, x2, y2] = p.bounding_box;
    return {
      id: `pest-${i}-${p.pest}`,
      label: p.pest,
      confidence: Math.round(p.confidence * 1000) / 10,
      x: (x1 / refWidth) * 100,
      y: (y1 / refHeight) * 100,
      width: ((x2 - x1) / refWidth) * 100,
      height: ((y2 - y1) / refHeight) * 100,
      type: 'pest' as const,
    };
  });
}
