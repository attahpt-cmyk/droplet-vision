"""Droplet detection: threshold -> label blobs -> size filter -> CSV."""

import argparse
from pathlib import Path

import matplotlib.image as mpimg
import pandas as pd
from scipy import ndimage as ndi

EXTENSIONS = ("*.tif", "*.tiff", "*.png", "*.jpg", "*.jpeg", "*.bmp")


def find_images(folder):
    files = []
    for ext in EXTENSIONS:
        files.extend(folder.glob(ext))
    return sorted(files)


def process_frame(filepath, threshold=110, min_area=5, max_area=2500):
    img = mpimg.imread(filepath)
    red = img[:, :, 0] if img.ndim == 3 else img
    if red.dtype.kind == "f":
        red = (red * 255).astype("uint8")

    binary = red < threshold
    labeled, num = ndi.label(binary)
    sizes = ndi.sum(binary, labeled, range(1, num + 1))
    valid = [s for s in sizes if min_area <= s <= max_area]

    return {
        "filename": filepath.name,
        "num_droplets": len(valid),
        "total_area": float(sum(valid)),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect droplets in a folder of images."
    )
    parser.add_argument("input_folder", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results.csv"))
    parser.add_argument("--threshold", type=int, default=110)
    parser.add_argument("--min-area", type=int, default=5)
    parser.add_argument("--max-area", type=int, default=2500)
    args = parser.parse_args()

    files = find_images(args.input_folder)
    if not files:
        raise SystemExit(f"No images found in {args.input_folder}")

    results = []
    for f in files:
        r = process_frame(f, args.threshold, args.min_area, args.max_area)
        results.append(r)
        print(f"{r['filename']}: {r['num_droplets']} droplets")

    pd.DataFrame(results).to_csv(args.output, index=False)
    print(f"Saved {len(results)} rows to {args.output}")


if __name__ == "__main__":
    main()
