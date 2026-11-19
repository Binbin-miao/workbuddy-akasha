# 虚空 (Akasha / `akasha`) v9.2.0 — 自然对话前台 × Codex 风格 Worktree 隔离 × 七人工程后台

遵循 [WorkBuddy 开放平台《专家团》官方规范](https://open.workbuddy.cn/docs/expert-team) 构建的 **v9.2 七人全栈研发专家团**：在 v9.1 自然对话、专职 AOCI 机器索引、深度审讯、单轮终审与自动 Word 交付的基础上，为 WorkBuddy 原生补齐 **Codex 风格 Git Worktree 隔离研发工作流**。

## 六大核心能力

1. **Codex 风格 Git Worktree 隔离工作流（v9.2 新增）**
   - 新增 `git-worktree-isolation` 技能与零依赖 CLI `scripts/worktree_manager.py`。
   - 动码前自动在仓库同级隐藏目录 `<parent>/.akasha-worktrees/<repo>/<slug>` 创建独立分支 `akasha/<slug>`，**主工作区 100% 零污染**（就算主目录有未提交改动也能无缝隔离，还支持无损 `--include-dirty` 快照带入）。
   - 子代理强制执行 `WORKTREE_BOUNDARY_LOCK`（源码编辑、编译、测试、运行时 QA 与单轮终审全部限定在独立副本内完成），且自动复用主仓 `.scratch/` 单一权威文档，杜绝脑裂。
   - 收尾提供与 Codex 对齐的 4 种落地方式：**合并回当前分支（`squash-merge` / `merge`）**、**像 Codex "Apply" 一样直接打成补丁放到本地工作区（`apply-patch`）**、**保留独立分支供审阅/提 PR（`keep`）** 或 **一键安全清理（`cleanup`，Windows/POSIX 依赖链接防误删保护）**。
2. **前台自然对话 × 后台严谨工程分离**
   - 派蒙前台说顺手人话，藏起全部内部编号与黑话；闲聊/咨询走 Workflow 0 直通通道，不乱拉流程。
3. **专职 AOCI 机器索引测绘官（艾尔海森 + `aoci_prescan.py`）**
   - SHA-256 增量漂移检测 + 标准 `aoci.txt / aoci.meta.txt / aoci.code.txt`，其余成员直读零盲扫，省 60%–80% Token。
4. **6 维灰区温和深度对齐**
   - 1–2 轮递进弹窗覆盖全部边界（带默认推荐与一键跳过），锁定 `CONTEXT.md` 与 `spec.md`。
5. **确定性门禁 + Diff-Aware 运行时 QA + 单轮终审上限**
   - `可莉` 实跑静态门禁 + 真实运行时 QA 提前消 Bug；`希格雯` 强制最多 1 轮 Diff-Only 终审，绝不空转烧 Token。
6. **任务收尾自动交付 Word (`.docx`) 进度说明报告**
   - 内置 `generate_delivery_docx.py`，详细表格、变更清单、落地方式与实测证据全部归档进 `.docx`。
