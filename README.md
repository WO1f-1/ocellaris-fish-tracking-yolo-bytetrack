# ocellaris-fish-tracking-yolo-bytetrack
基于 YOLO 的鱼类与倒影检测及 ByteTrack 追踪流程用于小丑鱼行为分析。
YOLO-based fish/reflection detection and ByteTrack tracking pipeline for ocellaris clownfish behavior analysis.

# Ocellaris Fish Tracking with YOLO and ByteTrack

A computer vision pipeline for detecting real fish and tank-wall reflections, then tracking individual ocellaris clownfish for behavior analysis.

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
|---|---:|---:|---:|---:|
| V4 | V5 val | 0.862 | 0.940 | 0.901 |
| V5 | V5 val | 0.903 | 0.952 | 0.927 |

## Tracking Result

Using V5 + ByteTrack E2 on a 5-minute TOP-view test clip, about 3 obvious ID switches were observed.

## Annotation Rules

- Real fish: `fish`
- Complete tank-wall mirror image: `reflection`
- Bubbles, light spots, water texture: not labeled
- Severely occluded or unclear fish: not labeled
- Overlapping but separable fish: labeled separately

## Limitations

- The current TOP_test_5min clip is not a strict independent test set.
- Severe occlusion, bubbles, and reflections can still cause ID switches.
- An independent test set is still needed for final evaluation.

## Roadmap

- Add V6 training samples from TOP_final.mp4 15:00–20:00
- Build an independent test set
- Compare V5 and V6 on the same test set
- Export stable trajectory CSV files
- Compute speed, acceleration, inter-fish distance, and group behavior features
- Extend to future 3D reconstruction and GCN-based modeling
