# Droplet Vision

## Computer Vision and Data Analysis for Automated Droplet Detection and Measurement

**Droplet Vision** is an ongoing research and development project focused on developing computational methods for the analysis of high-speed imaging data of liquid jets, droplets, and breakup processes.

The project combines **Python programming, data processing, computer vision, image analysis, machine learning, and deep learning** to develop an automated and scalable approach for extracting meaningful quantitative information from experimental imaging data.

## Project Scope

The project explores different stages of an automated data-analysis pipeline:

- Python programming and scientific computing
- Data organization, processing, and analysis
- File and dataset management
- Image preprocessing and enhancement
- Computer vision and image analysis
- Image segmentation and object detection
- Droplet size and shape measurement
- Droplet position and velocity estimation
- Object tracking across consecutive frames
- Analysis of liquid jet breakup and droplet formation
- Statistical analysis and visualization
- Processing of large experimental datasets
- Machine learning and deep learning
- Model training, evaluation, and validation
- Automation and reproducible computational workflows

## Planned Approach

The project is being developed progressively, starting with fundamental programming and data-processing techniques and advancing toward more sophisticated computer vision and AI-based approaches.

The initial development includes:

- Python programming
- NumPy and Pandas for numerical and experimental data analysis
- File and dataset management
- Data visualization
- Image preprocessing
- Classical computer vision techniques
- Object detection and segmentation
- Feature extraction and measurement

Future stages will investigate **machine-learning and deep-learning methods** for challenging imaging conditions, including small, overlapping, blurred, rapidly moving, and partially fragmented droplets.

## Research Context

The project is motivated by experimental research on **liquid jet breakup and droplet formation in a gaseous environment**.

High-speed imaging produces large amounts of visual data containing information about the evolution of liquid structures over time. The objective is to develop computational methods that can convert these images into quantitative measurements for the analysis of:

- Breakup dynamics
- Droplet characteristics
- Spray behavior
- Droplet size distributions
- Droplet trajectories and velocities
- Temporal evolution of liquid structures

## Development Direction

The long-term goal is to develop a general **computer vision and AI-based pipeline** capable of processing experimental imaging datasets with minimal manual intervention.

Potential future developments include:

- Automated dataset generation and labeling
- Advanced image segmentation
- Object detection
- Multi-frame object tracking
- Machine learning
- Deep learning
- Feature extraction
- Model training and evaluation
- Performance optimization
- Automated visualization and reporting
- Integration of different computational tools

## Current Status

🚧 **In Development**

The current stage focuses on building the foundations of the computational workflow, including **Python programming, data handling, file management, numerical analysis, and the development of computer vision techniques**.

The project will progressively expand toward advanced computer vision, machine learning, and deep learning methods while evaluating their performance on experimental high-speed imaging data.

## Usage

Requires Python 3.10+.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src\droplet_detect.py "path\to\image\folder" --output data\results.csv
```

Optional settings: `--threshold` (default 110), `--min-area` (default 5), `--max-area` (default 2500).

## Output

One row per frame in a CSV file: `filename`, `num_droplets`, `total_area` (in pixels).

## Current Method

1. Take the red channel of each frame
2. Threshold: pixels darker than the threshold count as liquid
3. Label connected regions
4. Keep regions between `min-area` and `max-area` as droplet candidates

## Known Limitations

- Pixel-exact connectivity means some bumps on the jet's edge are counted as separate droplets, so counts are an upper estimate rather than ground truth.
- Morphological closing/opening and a Sobel sharpness filter were tested on one frame and did not remove these false detections (details in `notes.md`).
- Areas are in pixels; no spatial calibration has been applied yet.
- The jet/droplet distinction currently relies on the area limits only.
