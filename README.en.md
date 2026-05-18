# Ocellaris Fish Tracking with YOLO and ByteTrack

[中文说明](README.zh.md)

This repository documents a computer vision workflow for detecting real fish and tank-wall reflections, then tracking individual ocellaris clownfish for behavior analysis.

The project is currently in a pilot and workflow-validation stage. The main goal is to build a reproducible pipeline for fish/reflection detection, multi-object tracking, trajectory export, and future behavioral analysis.

## Project Overview

The workflow is designed for top-view aquarium videos of ocellaris clownfish. The visual task is challenging because real fish, tank-wall reflections, bubbles, occlusion, and overlapping fish can easily interfere with both detection and tracking.

The overall pipeline is:

```text
Video input
→ preprocessing
→ fish/reflection detection
→ ByteTrack multi-object tracking
→ trajectory export
→ behavior analysis
```

## Main Objectives

This project aims to:

- distinguish real fish from tank-wall reflections;
- reduce false detections caused by reflections, bubbles, and water texture;
- improve stable detection of multiple fish in top-view videos;
- generate individual fish trajectories using ByteTrack;
- prepare trajectory data for behavioral metrics such as speed, acceleration, and inter-fish distance;
- support future 3D reconstruction and graph-based behavior modeling.

## Detection Classes

The current detection task uses two classes:

| Class ID | Class Name | Meaning |
|---:|---|---|
| 0 | fish | Real fish body |
| 1 | reflection | Complete fish-like reflection on the tank wall |

## Annotation Rules

The annotation rules are:

- real fish bodies are labeled as `fish`;
- complete fish-shaped mirror images on the tank wall are labeled as `reflection`;
- bubbles, light spots, and water texture are not labeled;
- severely occluded or unclear fish are not labeled;
- overlapping but separable fish are labeled separately;
- complete reflections that may be misdetected as real fish are labeled as `reflection`.

## Current Best Setup

The current best candidate setup is:

| Component | Choice |
|---|---|
| Detector | V5_train200_val100 |
| Tracker | ByteTrack E2 |
| Detection classes | fish / reflection |
| Tracking class | fish only |

During tracking, only the `fish` class is used. The `reflection` class is used during detection training to help the model distinguish real fish from tank-wall reflections.

## Model Development

The model was developed through several iterations:

| Stage | Main Change | Result |
|---|---|---|
| COCO baseline | Tested a general YOLO model | Not suitable; fish were often misclassified as COCO objects |
| Early fish/reflection baseline | Built the first two-class detector | Usable, but had missed detections and fragmented IDs |
| V2 | Increased training epochs | More epochs alone did not solve difficult cases |
| V3 | Added TOP_test_2min samples | Improved detection completeness and tracking stability |
| V4 | Added 300 manually corrected difficult samples | Became an important intermediate model and pre-labeling tool |
| V5 | Added train200 + val100 and fine-tuned from V4 | Current best candidate model |

## V4 vs V5 Comparison

V4 and V5 were compared on the same V5 validation set.

| Model | Validation Set | fish AP | reflection AP | mAP@0.5 |
|---|---|---:|---:|---:|
| V4 | V5 val | 0.862 | 0.940 | 0.901 |
| V5 | V5 val | 0.903 | 0.952 | 0.927 |

The results show that V5 outperformed V4 on both `fish` and `reflection` classes under the same validation setting.

## Tracking Result

Using the V5 detector with ByteTrack E2 on a 5-minute top-view test clip, about 3 obvious ID switches were observed.

This result suggests that the current pipeline is usable for short-term 2D trajectory extraction, but it has not fully solved identity preservation under severe occlusion, overlap, and reflection interference.

## Dataset Construction

The dataset was built through multiple rounds of frame extraction, model pre-labeling, and manual correction.

| Batch | Source | Usage | Description |
|---|---|---|---|
| Initial dataset | TOP_final.mp4 | train / val | Initial fish/reflection dataset |
| top2m | TOP_test_2min.mp4 | train | About 200 manually labeled images |
| top5m300 | TOP_test_5min.mp4 | train | 300 pre-labeled and manually corrected difficult samples |
| v5tr | TOP_final.mp4 20:00–25:00 | train | 200 additional V5 training images |
| v5val | TOP_final.mp4 10:00–15:00 | val | 100 additional V5 validation images |
| v6tr | TOP_final.mp4 15:00–20:00 | planned train | Planned V6 training samples |

Note: `TOP_test_5min` is not a strict independent test set because some frames from this clip have already been used for training. A fully independent test set is still required for final evaluation.

## Current Limitations

The current version has several limitations:

- the current `TOP_test_5min` clip is not a strict independent test set;
- severe occlusion, bubbles, and tank-wall reflections can still cause ID switches;
- reflections or bubbles may occasionally be misdetected as real fish;
- long-term tracking still requires trajectory post-processing and manual review;
- an independent test set is needed for more rigorous model evaluation.

## Roadmap

Planned next steps:

- add V6 training samples from `TOP_final.mp4` 15:00–20:00;
- use the current V5 model for pre-labeling;
- manually correct labels in CVAT;
- train a V6 detector;
- build an independent test set;
- compare V5 and V6 on the same test set;
- export stable trajectory CSV files;
- compute behavioral metrics such as speed, acceleration, and inter-fish distance;
- extend the workflow to 3D reconstruction and GCN-based behavior modeling.

## Repository Status

This repository currently serves as a public project showcase and documentation archive. Training scripts, tracking scripts, configuration files, example outputs, and independent test results will be added gradually as the workflow is cleaned and organized.

## License

This project is released under the MIT License.
