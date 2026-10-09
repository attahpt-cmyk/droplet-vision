"""Droplet measurement: threshold -> label blobs -> size filter -> one CSV row per droplet."""

import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from skimage.measure import regionprops

EXTENSIONS = ("*.tif", "*.tiff", "*.png", "*.jpg", "*.jpeg", "*.bmp")


def find_images(folder):
    files = []
    for ext in EXTENSIONS:
        files.extend(folder.glob(ext))
    return sorted(files)


def measure_frame(filepath, threshold=110, min_area=5, max_area=2500, min_circ_area=30):
    img = cv2.imread(str(filepath))
    if img is None:
        raise ValueError(f"Could not read image: {filepath}")

    red = img[:, :, 2]  # OpenCV loads BGR, so red is index 2
    mask = (red < threshold).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n == 1:
        return [], 0

    jet_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    jet_area = int(stats[jet_label, cv2.CC_STAT_AREA])
    dist_to_jet = cv2.distanceTransform(
        (labels != jet_label).astype(np.uint8), cv2.DIST_L2, 5
    )

    rows = []
    for r in regionprops(labels):
        if r.label == jet_label or not (min_area <= r.area <= max_area):
            continue
        circ_ok = r.perimeter > 0 and r.area >= min_circ_area
        rows.append(
            {
                "filename": filepath.name,
                "id": r.label,
                "area_px": r.area,
                "equiv_diameter_px": r.equivalent_diameter_area,
                "centroid_x": r.centroid[1],
                "centroid_y": r.centroid[0],
                "perimeter_px": r.perimeter,
                "circularity": (
                    4 * np.pi * r.area / r.perimeter**2 if circ_ok else np.nan
                ),
                "dist_to_jet_px": float(
                    dist_to_jet[r.coords[:, 0], r.coords[:, 1]].min()
                ),
            }
        )
    return rows, jet_area


def main():
    parser = argparse.ArgumentParser(
        description="Measure droplets in a folder of images."
    )
    parser.add_argument("input_folder", type=Path)
    parser.add_argument("--output", type=Path, default=Path("droplets.csv"))
    parser.add_argument("--threshold", type=int, default=110)
    parser.add_argument("--min-area", type=int, default=5)
    parser.add_argument("--max-area", type=int, default=2500)
    parser.add_argument("--min-circ-area", type=int, default=30)
    args = parser.parse_args()

    files = find_images(args.input_folder)
    if not files:
        raise SystemExit(f"No images found in {args.input_folder}")

    all_rows = []
    for f in files:
        rows, jet_area = measure_frame(
            f, args.threshold, args.min_area, args.max_area, args.min_circ_area
        )
        all_rows.extend(rows)
        print(f"{f.name}: {len(rows)} droplets, jet {jet_area} px")

    pd.DataFrame(all_rows).to_csv(args.output, index=False)
    print(f"Saved {len(all_rows)} droplets from {len(files)} frames to {args.output}")


if __name__ == "__main__":
    main()
