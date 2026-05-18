# Ocellaris Fish Tracking with YOLO and ByteTrack

[中文说明](README.zh.md)

YOLO-based fish/reflection detection and ByteTrack tracking pipeline for ocellaris clownfish behavior analysis.

## Highlights

- Two-class object detection: `fish` and `reflection`
- YOLO-based detector trained through multiple iterations
- ByteTrack-based multi-object tracking
- Current best candidate: V5 detector + ByteTrack E2
- V5 outperformed V4 on the same validation set
- V5 + ByteTrack E2 showed about 3 obvious ID switches in a 5-minute test clip

## Pipeline

Video input  
→ preprocessing  
→ fish/reflection detection  
→ ByteTrack tracking  
→ trajectory export  
→ behavior analysis

## Current Best Setup

| Component | Choice |
|---|---|
| Detector | V5_train200_val100 |
| Tracker | ByteTrack E2 |
| Detection classes | fish / reflection |
| Tracking class | fish only |

## Model Comparison

| Model | Validation Set | fish AP | reflection AP | mAP@0.5 |
|---|---:|---:|---:|
| V4 | V5 val | 0.862 | 0.940 | 0.901 |
| V5 | V5 val | 0.903 | 0.952 | 0.927 |

## Tracking Result

Using V5 + ByteTrack E2 on a 5-minute TOP-view test clip, about 3 obvious ID switches were observed.

This indicates that the current pipeline is usable for short-term 2D trajectory extraction, but ID preservation under occlusion and reflection interference is not fully solved.

## Annotation Rules

- Real fish: `fish`
- Complete tank-wall mirror image: `reflection`
- Bubbles, light spots, and water texture: not labeled
- Severely occluded or unclear fish: not labeled
- Overlapping but separable fish: labeled separately

## Dataset Construction

The dataset was built through multiple rounds of frame extraction, model-assisted pre-labeling, and manual correction in CVAT.

| Batch | Source | Usage | Description |
|---|---|---|---|
| Initial dataset | TOP_final.mp4 | train / val | Initial fish/reflection dataset |
| top2m | TOP_test_2min.mp4 | train | About 200 manually labeled images |
| top5m300 | TOP_test_5min.mp4 | train | 300 model-prelabeled and manually corrected images |
| v5tr | TOP_final.mp4 20:00–25:00 | train | 200 additional V5 training images |
| v5val | TOP_final.mp4 10:00–15:00 | val | 100 additional V5 validation images |
| v6tr | TOP_final.mp4 15:00–20:00 | planned train | Planned V6 training samples |

## Current Limitations

- `TOP_test_5min` is not a strict independent test set.
- Severe occlusion, bubbles, and tank-wall reflections can still cause ID switches.
- Some reflection or bubble interference may still be misdetected as fish.
- A fully independent test set is still needed for final evaluation.

## Roadmap

- Add V6 training samples from `TOP_final.mp4` 15:00–20:00
- Build an independent test set
- Compare V5 and V6 on the same test set
- Export stable trajectory CSV files
- Compute speed, acceleration, inter-fish distance, and group behavior features
- Extend to future 3D reconstruction and GCN-based behavior modeling

## License

This project is released under the MIT License.
