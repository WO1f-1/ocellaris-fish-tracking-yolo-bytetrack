# 2026-05-17 23:00 提交建议

下面这些文件内容按“2026-05-17 23:00 当时已经可以总结出来”的项目状态整理，适合用于补充 5 月 17 日的真实项目记录提交。

## 建议提交顺序

```bash
git add README_2026-05-17_2300.md
GIT_AUTHOR_DATE="2026-05-17T23:00:00+08:00" GIT_COMMITTER_DATE="2026-05-17T23:00:00+08:00" git commit -m "Add fish tracking project summary"

git add docs/model_iterations_2026-05-17_2300.md
GIT_AUTHOR_DATE="2026-05-17T23:08:00+08:00" GIT_COMMITTER_DATE="2026-05-17T23:08:00+08:00" git commit -m "Document early YOLO model iterations"

git add docs/dataset_protocol_2026-05-17_2300.md
GIT_AUTHOR_DATE="2026-05-17T23:16:00+08:00" GIT_COMMITTER_DATE="2026-05-17T23:16:00+08:00" git commit -m "Document dataset construction protocol"

git add docs/annotation_rules_2026-05-17_2300.md
GIT_AUTHOR_DATE="2026-05-17T23:24:00+08:00" GIT_COMMITTER_DATE="2026-05-17T23:24:00+08:00" git commit -m "Add fish and reflection annotation rules"

git add docs/tracking_protocol_2026-05-17_2300.md
GIT_AUTHOR_DATE="2026-05-17T23:32:00+08:00" GIT_COMMITTER_DATE="2026-05-17T23:32:00+08:00" git commit -m "Document fish tracking evaluation protocol"

git push origin main
```

## 注意

- 确保 git config user.email 是 GitHub 账号已绑定邮箱。
- 确保提交在 main/master 默认分支上。
- GitHub 贡献墙可能不会立刻刷新。
