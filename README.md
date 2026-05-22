# Ocellaris Fish Tracking with YOLO26s and ByteTrack

YOLO26s-based `fish/reflection` detection and ByteTrack tracking pipeline for ocellaris clownfish behavior analysis.

English | [简体中文](README.zh.md)

## Overview

This project builds a computer-vision pipeline for TOP-view ocellaris clownfish videos.  
The detection task is defined as a two-class problem:

- `fish`: real fish body
- `reflection`: complete fish-like mirror image on the tank wall

Only the `fish` class is used for ByteTrack multi-object tracking. This design reduces the influence of tank-wall reflections on trajectory extraction and downstream behavior analysis.

## Current Status

The project has completed multiple rounds of dataset construction, CVAT annotation correction, YOLO26s model iteration, and ByteTrack tracking evaluation.

The current main working setup is:

| Component | Choice |
|---|---|
| Detector | YOLO26s V6 |
| Tracker | ByteTrack E2 |
| Detection classes | `fish` / `reflection` |
| Tracking class | `fish` only |
| Current role | Main analysis candidate for 2D trajectory extraction |

V6+E2 improves automatic tracking continuity compared with V5+E2, but manual inspection still found ID switches.  
The current bottleneck has shifted from detection completeness to identity consistency during crossing and occlusion events.

## Pipeline

```text
Video input
→ preprocessing
→ fish/reflection detection
→ ByteTrack tracking
→ trajectory CSV export
→ behavior metrics
→ future 3D reconstruction / social behavior modeling
```

## Highlights

- Two-class YOLO26s detection: `fish` and `reflection`
- CVAT-assisted annotation correction through multiple dataset iterations
- ByteTrack-based multi-object tracking for real fish only
- V6 improves detection completeness and track continuity compared with V5+E2
- Current bottleneck: ID switches during crossing, occlusion, and close interactions
- Future direction: `identity_uncertain` labeling, tracklet stitching, and dual-view 3D trajectory reconstruction

## Annotation Rules

| Class ID | Class name | Meaning |
|---:|---|---|
| 0 | `fish` | Real fish body |
| 1 | `reflection` | Complete fish-like reflection on the tank wall |

Rules:

- Real fish bodies are labeled as `fish`.
- Complete fish-like mirror images on the tank wall are labeled as `reflection`.
- Bubbles, light spots, and water texture are not labeled.
- Severely occluded or unclear fish are not labeled.
- Overlapping but separable fish are labeled separately.
- Complete reflections that may be confused with real fish should be labeled as `reflection`.

## Dataset Construction

The dataset was built through frame extraction, YOLO-assisted pre-labeling, and manual correction in CVAT.

Current dataset size:

| Split | Images | Boxes |
|---|---:|---:|
| Train | 1128 | 4432 |
| Val | 233 | 939 |
| Total | 1361 | 5371 |

Major batches:

| Batch | Source | Usage | Description |
|---|---|---|---|
| Initial dataset | `TOP_final.mp4` | train / val | Initial fish/reflection dataset |
| `top2m` | `TOP_test_2min.mp4` | train | About 200 manually labeled images |
| `top5m300` | `TOP_test_5min.mp4` | train | 300 model-prelabeled and manually corrected images |
| `v5tr` | `TOP_final.mp4` 20:00–25:00 | train | 200 V5 training images |
| `v5val` | `TOP_final.mp4` 10:00–15:00 | val | 100 V5 validation images |
| `v6tr` | `TOP_final.mp4` 15:00–20:00 | train | 300 V6 training images |
| `v6val` | `TOP_final.mp4` 05:00–10:00 | val | 100 V6 validation images |

During V6 annotation correction, three main V5 pre-labeling issues were observed:

- bounding boxes were generally slightly too large;
- about 10 images had duplicate labels on a single fish;
- about 5 images had missed fish in simple scenes.

## Model Iteration

| Stage | Main change | Notes |
|---|---|---|
| Baseline | Initial fish/reflection detector | Basic detection worked, but tracking was fragmented |
| V3 | Added manually labeled `TOP_test_2min` frames | Improved detection completeness |
| V4 | Added 300 corrected `TOP_test_5min` samples | Important intermediate model for pre-labeling |
| V5 | Added `train200 + val100` and fine-tuned from V4 | Stable previous main detector |
| V6 | Added `train300 + val100` and fine-tuned from V5 | Better fish localization and tracking continuity |

## Detection Results

### V4 vs V5 on the same V5 validation set

| Model | Validation set | fish AP | reflection AP | mAP@0.5 |
|---|---|---:|---:|---:|
| V4 | V5 val | 0.862 | 0.940 | 0.901 |
| V5 | V5 val | 0.903 | 0.952 | 0.927 |

### V5 vs V6 on the same current validation set

| Metric | V5 | V6 | V6 - V5 |
|---|---:|---:|---:|
| Precision | 0.954238 | 0.939275 | -0.014963 |
| Recall | 0.885493 | 0.887933 | +0.002440 |
| mAP@0.5 | 0.941918 | 0.943662 | +0.001744 |
| mAP@0.5:0.95 | 0.654955 | 0.657031 | +0.002076 |

Per-class mAP@0.5:0.95:

| Class | V5 | V6 | V6 - V5 |
|---|---:|---:|---:|
| fish | 0.602350 | 0.622142 | +0.019792 |
| reflection | 0.707560 | 0.691919 | -0.015640 |

Interpretation: V6 mainly improves real-fish localization, while precision and reflection performance are slightly lower.

## Tracking Comparison

Test video:

```text
TOP_test_5min.mp4
```

Tracking configuration:

```text
ByteTrack E2
```

| Metric | V5+E2 | V6+E2 | Change |
|---|---:|---:|---:|
| Mean boxes/frame | 2.8822 | 2.9335 | +0.0513 |
| Median boxes/frame | 3.0 | 3.0 | 0 |
| Total IDs | 32 | 18 | -14 |
| Short IDs < 90 frames | 16 | 4 | -12 |
| Mean ID life | 1622.8 | 2938.2 | +1315.3 |
| Median ID life | 65.0 | 753.5 | +688.5 |
| Manual ID switches | 3 | 4 | +1 |

V6+E2 processed 18030 frames. Frame-level fish count:

| Fish count condition | Frames |
|---|---:|
| fish count = 3 | 16854 |
| fish count < 3 | 1158 |
| fish count > 3 | 18 |

Conclusion:

- V6+E2 improves detection completeness and track continuity.
- V6+E2 greatly reduces fragmented IDs and short-lived IDs.
- Manual inspection still found 4 ID switches.
- Therefore, V6+E2 is a better next-stage analysis candidate, but identity preservation is not fully solved.

## Current Bottleneck

The current bottleneck is no longer only detection mAP.  
The main issue is identity consistency when visually similar fish cross, overlap, or occlude each other.

Because the three ocellaris clownfish have highly similar appearances, appearance-based ReID is not used as the main identity-preservation strategy. The future direction is based on:

- motion continuity;
- `identity_uncertain` labeling;
- tracklet stitching;
- dual-view 3D reconstruction;
- social-status inference from body size, trajectory, and interaction direction.

## Current Limitations

- `TOP_test_5min` is not a strict independent test set because some related frames have been used during model development.
- V6+E2 still has manual ID switches.
- Severe occlusion, close interactions, bubbles, and tank-wall reflections remain challenging.
- Current results are suitable for short-term 2D trajectory extraction and method validation.
- A strict independent temporal test set is still needed for final evaluation.

## Roadmap

- [x] Build a `fish/reflection` two-class detection dataset
- [x] Train and validate V5 / V6 YOLO26s models
- [x] Compare V5+E2 and V6+E2 tracking performance
- [ ] Record ID switch segments and build an error bank
- [ ] Add `identity_uncertain` labels for crossing and occlusion events
- [ ] Export standardized trajectory CSV files
- [ ] Compute 2D behavior metrics such as speed, inter-individual distance, group center, and MND
- [ ] Build V7 hard-sample training data from failure cases
- [ ] Explore dual-view 3D trajectory reconstruction
- [ ] Build social behavior metrics and graph-based group analysis

## Acknowledgements

Thanks to [fzz872](https://github.com/fzz872) for project discussion and documentation support.

## License

This project is released under the MIT License.
