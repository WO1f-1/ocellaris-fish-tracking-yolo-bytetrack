# ocellaris-fish-tracking-yolo-bytetrack
- 基于 YOLO 的鱼类与倒影检测及 ByteTrack 追踪流程用于小丑鱼行为分析
- YOLO-based fish/reflection detection and ByteTrack tracking pipeline for ocellaris clownfish behavior analysis.

# 基于 YOLO 与 ByteTrack 的眼斑双锯鱼跟踪项目

本项目构建了一个计算机视觉流程，用于检测真实鱼体与鱼缸壁反射，并进一步跟踪眼斑双锯鱼个体，为后续鱼类行为分析提供基础数据。

## 项目亮点

- 双类别目标检测：`fish` 与 `reflection`
- 基于 YOLO 的检测模型，已完成多轮迭代训练
- 基于 ByteTrack 的多目标跟踪流程
- 当前最佳候选方案：V5 检测模型 + ByteTrack E2 跟踪配置
- V5 在相同验证集上优于 V4
- V5 + ByteTrack E2 在 5 分钟测试片段中约出现 3 次明显 ID 互换

## 项目流程

视频输入  
→ 视频预处理  
→ fish/reflection 双类别检测  
→ ByteTrack 多目标跟踪  
→ 轨迹导出  
→ 行为分析

## 当前最佳配置

| 模块 | 选择 |
|---|---|
| 检测模型 | V5_train200_val100 |
| 跟踪器 | ByteTrack E2 |
| 检测类别 | fish / reflection |
| 跟踪类别 | 仅 fish |

## 模型对比

| 模型 | 验证集 | fish AP | reflection AP | mAP@0.5 |
|---|---:|---:|---:|---:|
| V4 | V5 val | 0.862 | 0.940 | 0.901 |
| V5 | V5 val | 0.903 | 0.952 | 0.927 |

## 跟踪结果

在一个 5 分钟的顶视角测试片段中，使用 V5 + ByteTrack E2 进行多目标跟踪，观察到约 3 次明显的 ID 互换。

## 标注规则

- 真实鱼体：标注为 `fish`
- 鱼缸壁上的完整鱼形镜像：标注为 `reflection`
- 气泡、光斑、水流纹理：不标注
- 严重遮挡或轮廓不清的鱼：不标注
- 鱼体重叠但仍能区分个体时：分别标注

## 当前限制

- 当前的 `TOP_test_5min` 片段并不是严格独立测试集。
- 严重遮挡、气泡干扰和鱼缸壁反射仍可能导致 ID 互换。
- 后续仍需要建立独立测试集，用于最终模型评估。

## 后续计划

- 从 `TOP_final.mp4` 的 15:00–20:00 时间段新增 V6 训练样本
- 构建独立测试集
- 在同一测试集上比较 V5 与 V6
- 导出稳定的轨迹 CSV 文件
- 计算速度、加速度、个体间距离和群体行为特征
- 后续扩展到三维重建与基于 GCN 的行为建模
