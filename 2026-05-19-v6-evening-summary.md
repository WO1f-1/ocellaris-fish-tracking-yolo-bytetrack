# 2026-05-19 晚间进展记录：V6 数据扩充、训练与 V5/V6 对比

> 项目：眼斑双锯鱼 fish/reflection 双类别检测与 ByteTrack 跟踪  
> 记录时间：2026-05-19 23:24  
> 当前阶段：V5 + E2 稳定方案基础上，推进 V6 候选模型验证  
> 记录目的：补充项目进展、同步 GitHub、保留 2026-05-19 的开发贡献记录

---

## 1. 今晚工作目标

今晚的工作不是重新规划项目，而是在既有 **V5 检测模型 + ByteTrack E2 跟踪配置** 的基础上继续推进。

主要目标如下：

1. 完成 `V6 train300` 数据闭环；
2. 新增 `V6 val100` 验证集；
3. 基于 V5 权重继续微调训练 V6；
4. 在同一 current val 上公平比较 V5 与 V6；
5. 判断 V6 是否具备替代 V5 成为新主模型的可能；
6. 为后续 V6 + E2 tracking 验证做准备。

---

## 2. 当前项目背景

本项目围绕眼斑双锯鱼顶视角视频，构建鱼类群体行为分析的视觉基础流程：

```text
视频输入
→ fish/reflection 双类别检测
→ ByteTrack 多目标跟踪
→ ID 轨迹导出
→ 行为学指标计算
→ 后续三维重建与 GCN 建模
```

当前检测类别为：

```text
0 = fish
1 = reflection
```

当前已知稳定方案为：

```text
检测模型：V5_train200_val100
跟踪器：ByteTrack E2
```

V5 的主要权重路径：

```text
/mnt/e/pilot exp/fish_best_v5_train200_val100.pt
```

E2 跟踪配置路径：

```text
/mnt/e/pilot exp/bytetrack_fish_final_E2.yaml
```

---

## 3. V6 train300 数据来源

V6 train300 来自 `TOP_final.mp4` 的 15:00–20:00 片段：

```text
video = /mnt/e/pilot exp/TOP_final.mp4
time range = 15:00–20:00
start_sec = 900
duration_sec = 300
num_frames = 300
```

该时间段的选择理由是避开已有 V5 数据分区：

```text
10:00–15:00：v5val_
15:00–20:00：v6tr_
20:00–25:00：v5tr_
```

已生成：

```text
fish_dataset/v6_train300_frames
fish_dataset/v6_train300_frames.zip
```

经检查，图片数量为 300 张。

---

## 4. V5 预标与 CVAT 导入

V6 train300 使用当前 V5 模型进行预标：

```text
model = fish_best_v5_train200_val100.pt
classes = [0, 1]
conf = 0.35
imgsz = 1024
```

预标目标：

```text
0 = fish
1 = reflection
```

CVAT 导入时采用 `YOLO / YOLO 1.1` 格式。

导入过程中遇到两个格式问题：

### 4.1 缺少 obj.data

初始 zip 中只有 `.txt` 标注文件和 `obj.names`，CVAT 报错：

```text
cvat.apps.dataset_manager.bindings.CvatDatasetNotFoundError:
Dataset must contain a file: "obj.data"
```

原因是 CVAT 的 YOLO 1.1 导入要求压缩包中必须包含 `obj.data`。

### 4.2 train.txt 路径与任务图片名不匹配

补充 `obj.data` 后，又出现图片路径匹配错误：

```text
Can't find image info for '/home/django/data/tmp/.../obj_train_data/frame_000001.jpg'
```

原因是 `train.txt` 中写入了：

```text
obj_train_data/frame_000001.jpg
```

但 CVAT 任务中已上传图片名是：

```text
frame_000001.jpg
```

最终解决方法是在 `train.txt` 中只写图片文件名：

```text
frame_000001.jpg
frame_000002.jpg
...
```

这样 CVAT 成功识别任务图片并导入预标框。

---

## 5. V6 train300 人工修正观察

V6 train300 在 CVAT 中完成 300 张人工修正。

修正过程中发现 V5 预标存在以下系统性问题：

```text
1. 预标注框普遍略偏大；
2. 300 张中约 10 张存在单条鱼重复标记；
3. 约 5 张在明显非复杂环境下存在真实鱼漏检。
```

这些问题说明 V5 的主要短板并不是完全无法识别目标，而是集中在：

```text
边界框贴合度
重复检测抑制
简单场景下少量漏检
```

因此，V6 train300 的主要价值是：

1. 改善 fish 类边界框定位质量；
2. 减少单鱼重复检测；
3. 修正简单场景下的漏检；
4. 提升后续 ByteTrack 输入框质量。

---

## 6. V6 train300 导出与合并

CVAT 修正完成后导出：

```text
fish_dataset/v6_train300_manual_fixed.zip
```

导出包结构包含：

```text
train.txt
data.yaml
labels/train/v6_train300_frames/*.txt
```

随后将该批数据合并进 YOLO 数据集 train 集，统一前缀：

```text
v6tr_
```

合并目标目录：

```text
fish_dataset/yolo_fish_reflection/images/train/
fish_dataset/yolo_fish_reflection/labels/train/
```

合并后的 V6 train300 统计：

```text
v6tr_ images = 300
v6tr_ labels = 300
v6tr_ boxes = 1269
  fish = 902
  reflection = 367
```

标签格式检查：

```text
bad_line_count = 0
```

---

## 7. V6 val100 验证集

为了配合 V6 评估，新增 V6 val100。

数据来源：

```text
TOP_final.mp4 05:00–10:00
start_sec = 300
duration_sec = 300
num_frames = 100
```

该批数据只进入 val，不进入 train。

CVAT 任务：

```text
v6_val100_manual_fix
```

导出文件：

```text
fish_dataset/v6_val100_manual_fixed.zip
```

合并进 YOLO 数据集 val 集，统一前缀：

```text
v6val_
```

合并目标目录：

```text
fish_dataset/yolo_fish_reflection/images/val/
fish_dataset/yolo_fish_reflection/labels/val/
```

合并后的 V6 val100 统计：

```text
v6val_ images = 100
v6val_ labels = 100
v6val_ boxes = 422
  fish = 280
  reflection = 142
```

---

## 8. 当前数据集统计

合并 V6 train300 与 V6 val100 后，当前 YOLO 数据集统计如下：

```text
train images total = 1128
train labels total = 1128
val images total = 233
val labels total = 233
```

分批次统计：

```text
v5tr_ images = 200
v5tr_ labels = 200

v6tr_ images = 300
v6tr_ labels = 300

v5val_ images = 100
v5val_ labels = 100

v6val_ images = 100
v6val_ labels = 100
```

总体标注框统计：

```text
train boxes total = 4432
  fish = 3137
  reflection = 1295

val boxes total = 939
  fish = 618
  reflection = 321
```

标签检查结果：

```text
bad_line_count = 0
```

说明当前数据集格式正常，V6 train/val 合并过程没有发现明显标签损坏。

---

## 9. V6 模型训练

V6 基于 V5 权重继续微调，而不是从预训练模型重新训练。

基础模型：

```text
fish_best_v5_train200_val100.pt
```

训练运行名称：

```text
fish_reflection_yolo26s_v6_train300_val100
```

训练参数：

```text
epochs = 60
imgsz = 768
batch = 8
device = 0
workers = 4
optimizer = auto
patience = 15
amp = False
plots = True
```

训练结果：

```text
Early stopping at epoch 27
Best epoch = 12
Training time = 0.334 hours
```

最佳权重路径：

```text
fish_runs/fish_reflection_yolo26s_v6_train300_val100/weights/best.pt
fish_best_v6_train300_val100.pt
```

V6 在 current val 上的验证结果：

```text
all:
P = 0.939
R = 0.888
mAP50 = 0.944
mAP50-95 = 0.657

fish:
P = 0.948
R = 0.848
mAP50 = 0.934
mAP50-95 = 0.622

reflection:
P = 0.931
R = 0.928
mAP50 = 0.953
mAP50-95 = 0.692
```

---

## 10. V5 与 V6 同一 current val 公平比较

为避免验证集变化造成误判，今晚重新在同一 current val 上分别评估 V5 与 V6。

### 10.1 总体指标

| Metric | V5 | V6 | V6 - V5 |
|---|---:|---:|---:|
| Precision | 0.954238 | 0.939275 | -0.014963 |
| Recall | 0.885493 | 0.887933 | +0.002440 |
| mAP50 | 0.941918 | 0.943662 | +0.001744 |
| mAP50-95 | 0.654955 | 0.657031 | +0.002076 |

### 10.2 分类别 mAP50-95

| Class | V5 | V6 | V6 - V5 |
|---|---:|---:|---:|
| fish | 0.602350 | 0.622142 | +0.019792 |
| reflection | 0.707560 | 0.691919 | -0.015640 |

### 10.3 分类别 AP50

| Class | V5 AP50 | V6 AP50 | 变化 |
|---|---:|---:|---:|
| fish | 0.920082 | 0.934076 | +0.013994 |
| reflection | 0.963755 | 0.953248 | -0.010507 |

### 10.4 分类别 Recall

| Class | V5 Recall | V6 Recall | 变化 |
|---|---:|---:|---:|
| fish | 0.839521 | 0.847517 | +0.007996 |
| reflection | 0.931464 | 0.928349 | -0.003115 |

---

## 11. 阶段性分析

V6 并不是压倒性超过 V5，而是呈现出明确取舍。

### 11.1 V6 的优势

```text
1. fish 类 mAP50-95 明显提升；
2. fish recall 小幅提升；
3. fish AP50 提升；
4. 总体 mAP50 和 mAP50-95 小幅提升；
5. 对 V5 阶段框偏大的问题可能有改善。
```

其中最有价值的是 fish 类 mAP50-95：

```text
V5 fish mAP50-95 = 0.602350
V6 fish mAP50-95 = 0.622142
delta = +0.019792
```

这说明 V6 对真实鱼体的框定位质量有所改善，符合 V6 train300 修标时对“框偏大”的修正方向。

### 11.2 V6 的代价

```text
1. overall precision 下降；
2. reflection 类 mAP50-95 下降；
3. reflection AP50 小幅下降；
4. 是否改善实际 ByteTrack 跟踪仍需视频验证。
```

其中 precision 的下降需要特别注意：

```text
V5 precision = 0.954238
V6 precision = 0.939275
delta = -0.014963
```

如果 V6 在 tracking 中带来更多误检框，可能会增加假 ID 或短碎片 ID。

---

## 12. 当前模型定位

当前不应直接写成：

```text
V6 已全面优于 V5
```

更严谨的定位是：

```text
V5 + E2：当前稳定主方案
V6 + E2：候选增强方案，fish 检测更好，但需 tracking 验证
```

推荐汇报表述：

```text
在当前综合验证集上，V6 相比 V5 的总体 mAP50 和 mAP50-95 略有提升，其中 fish 类 mAP50-95 提升较明显，但 reflection 类性能略有下降。因此，V6 更偏向改善真实鱼体检测与框定位质量，是否替代 V5 仍需结合 ByteTrack 跟踪稳定性评估。
```

---

## 13. 下一步计划

下一步不应继续盲目训练 V7，而应进入跟踪层面的验证。

计划如下：

```text
1. 使用 V6 + ByteTrack E2 跑 TOP_test_5min；
2. 与已有 V5 + E2 结果进行对比；
3. 比较每帧 fish 数量、总 ID 数、短碎片 ID、明显 ID switch；
4. 检查 V6 是否减少简单漏检和重复框；
5. 若 V6 tracking 不劣于 V5，并且 fish 检测更稳定，则可将主方案升级为 V6 + E2。
```

跟踪比较重点：

```text
mean detections per frame
median detections per frame
total IDs
short fragment IDs
manual ID switch count
duplicate fish boxes
false fish detections near reflection
```

此外，还应建立真正独立的 temporal test，例如：

```text
TOP_final.mp4 00:00–05:00
```

该片段应只用于最终测试，不进入 train 或 val。

---

## 14. 今日结论

2026-05-19 晚间完成了 V6 train300 和 V6 val100 的数据闭环、V6 模型训练，以及 V5/V6 在同一 current val 上的公平比较。

V6 在 fish 类检测和定位方面取得了实质性改善，尤其是 fish mAP50-95 从 0.602350 提升至 0.622142。但整体优势较小，并伴随 precision 与 reflection 类指标轻微下降。

因此，当前结论是：

```text
V6 是候选新主模型；
V5 仍是稳定主方案；
是否正式切换到 V6 + E2，需要下一步 tracking 验证。
```

今晚的工作为后续判断 V6 是否真正改善鱼类跟踪稳定性提供了完整的数据和模型基础。

---

## 15. Git 提交建议

建议将本文件提交到仓库：

```text
docs/progress/2026-05-19-v6-evening-summary.md
```

建议提交信息：

```text
docs: summarize V6 training and validation progress
```

建议提交时间：

```text
2026-05-19T23:24:00+08:00
```

对应命令：

```bash
git add docs/progress/2026-05-19-v6-evening-summary.md

GIT_AUTHOR_DATE="2026-05-19T23:24:00+08:00" \
GIT_COMMITTER_DATE="2026-05-19T23:24:00+08:00" \
git commit -m "docs: summarize V6 training and validation progress"

git push origin main
```
