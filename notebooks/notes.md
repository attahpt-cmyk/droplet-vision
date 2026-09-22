# Porting Notes: MATLAB → Python (jet_conversion_diagnostics.m)

Notes from reading through the existing MATLAB pipeline before porting it to Python.
Goal: preserve the actual scientific logic exactly; don't blindly translate MATLAB-specific
syntax that has no Python equivalent (or a much simpler one).

## Inputs & Outputs

- **Input:** folder of high-speed frame images (.tif/.tiff/.png/.jpg/.jpeg/.bmp)
- **Output:** 3 subfolders — binary masks (`Generated_Binary`), annotated snapshots
  (`processed_snapshots`), and reports (`Reports`)
- **Output schema (per detected object):** Filename, ID, Type, Area_Pixels, Circularity, In_Focus
  — Type is one of: "Main Jet Structure", "Droplet" (in-focus), or discarded (out-of-focus)

## Core scientific logic (must preserve exactly, not just syntax-translate)

1. **Grayscale extraction:** takes only the first (Red) channel of color images, not a proper
   weighted grayscale conversion. Confirm this is intentional (camera-specific contrast) before
   porting — may want `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)` instead, or replicate as-is.

2. **8-bit normalization is required.** MATLAB and Python/OpenCV can represent pixel intensities
   differently depending on source format — must force both to 0–255 uint8 explicitly to keep
   thresholding consistent. (Flagged in original code as a real bug already fixed once.)

3. **Thresholding:** simple dark-pixel threshold — `pixel < threshold_value` = foreground.
   Default value: 110. Straightforward to port (`cv2.threshold` or plain NumPy comparison).

4. **Morphological cleanup:** cross-shaped 3×3 kernel (`[0 1 0; 1 1 1; 0 1 0]`), used with
   "closing" to fill small gaps in binary blobs before measuring.
   → `cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))`

5. **Sobel edge/sharpness filter:** standard 3×3 Sobel kernels for gradient magnitude
   (`sqrt(Gx² + Gy²)`), sampled specifically along each blob's *boundary* pixels and averaged.
   Used to reject blurry/out-of-focus detections. → `cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)`
   (and dy=1 for the other direction)

6. **Three-way classification per detected blob:**
   - Area < `minArea` (default 5) → discarded as noise
   - Area > `maxArea` (default 2500) **OR** width > 40% of frame width → classified as
     "Main Jet Structure" (not an individual droplet)
   - Otherwise → check mean Sobel gradient along boundary vs. `sharpLimit` (default 15):
     - Above limit → in-focus droplet (kept)
     - Below limit → out-of-focus (discarded)

7. **Circularity formula:** `4π × Area / Perimeter²`
   - ~1.0 = near-perfect circle (ideal droplet)
   - Lower = irregular/elongated shape
   - Guard against divide-by-zero on degenerate (near-zero-perimeter) blobs → default to 0
   - Only computed for actual droplets, not jet structures (jet rows get "N/A")

## Default parameter values (already validated, use as Python starting point)

- `threshold = 110`
- `min_area = 5`
- `max_area = 2500`
- `sharp_limit = 15`
- jet width cutoff = 40% of frame width

## MATLAB-specific things to NOT port literally

- **Pre-allocated struct array sized for worst case** (`numFiles * 25` estimated objects) —
  this exists purely because growing arrays is slow in MATLAB. In Python, just use a growing
  list of dicts or dataclass instances (e.g. reuse the `DropletData` dataclass pattern from
  the OOP notebook) — no pre-allocation needed.
- **Interactive slider-based tuning UI** (sliders for threshold/sharpness/min/max area, with
  execution pausing via `uiwait` until the user clicks "LOCK & START BATCH"). Decide whether to
  replicate this in Python (e.g. `matplotlib` widgets or `cv2.createTrackbar`) or simplify to a
  config file / CLI arguments, at least for the first version.
- **1-indexing vs 0-indexing** — MATLAB arrays start at 1, Python/NumPy at 0. Will affect any
  loop bounds or index math carried over.
- **Manual array row-stacking** (`[a; b]` syntax) — replace with `list.append()`/`.extend()`
  in Python, much simpler.

## Open questions to resolve before/during porting

- Is single-channel (Red-only) grayscale extraction intentional, or should it become a proper
  weighted grayscale conversion?
- Keep the interactive tuning step, or move straight to a config-file-driven approach for v1?
- Confirm actual filenames are zero-padded (frame001, frame002...) — alphabetical sort will
  order frames incorrectly otherwise (frame1, frame10, frame2...).