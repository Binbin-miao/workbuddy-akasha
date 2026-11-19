---
name: git-worktree-isolation
description: Codex 风格 Git Worktree 隔离研发工作流（v9.2）：为 WorkBuddy 补齐原生级隔离副本能力，主工作区零污染、支持多任务/多分片真正并行、提供补丁应用/合并/保留/清理四种落地方式与 Windows/POSIX 安全依赖处理。
---

# Codex-Style Git Worktree Isolation Protocol (v9.2)

## 1. ARCHITECTURE: WHY SIBLING WORKTREES + SHARED MAIN SSOT
WorkBuddy does not natively spin up Codex-style worktrees. This skill provides deterministic, zero-pollution isolation via `scripts/worktree_manager.py`:
- **Isolated Code Sandbox (`WORKTREE_PATH`)**: Created OUTSIDE the repository root at `<repo_parent>/.akasha-worktrees/<repo_name>/<slug>` on branch `akasha/<slug>`. Never creates nested `.worktrees/` inside the repo (prevents Vite/Cargo/ESLint/AOCI scanner pollution and Windows `MAX_PATH` bugs).
- **Shared Planning SSOT (`MAIN_REPO_ROOT`)**: `.scratch/aoci/`, `.scratch/<feature>/spec.md`, `.learnings/` stay anchored in `MAIN_REPO_ROOT` so all agents read one single source of truth with zero split-brain.
- **Zero Main-Workspace Pollution**: Even if the user has uncommitted edits in `MAIN_REPO_ROOT`, `worktree_manager.py create` spins up a clean branch from `HEAD` (or safely clones dirty edits via `--include-dirty` using non-destructive `git stash create`) without touching the user's open files.
- **Graceful Fallback**: If the folder is not a Git repository or has 0 commits yet, `probe` / `create` returns `"status": "fallback_in_place"` so tasks proceed seamlessly without failing.

## 2. DETERMINISTIC LIFECYCLE (`scripts/worktree_manager.py`)
Locate script at `~/.workbuddy/skills/git-worktree-isolation/scripts/worktree_manager.py` (or plugin path):
1. **Create Before Coding**:
   ```bash
   python "<wt_script>" create --repo "<main_repo>" --slug "<feature-slug>"
   ```
   *(Add `--include-dirty` ONLY if the user explicitly wants their current uncommitted changes included as the starting point; add `--link-node-modules` ONLY if the repo uses Node and `package-lock.json` will not be modified.)*
2. **Enforce `WORKTREE_BOUNDARY_LOCK` During Implementation & Audit**:
   - `可莉` MUST edit source files and run build/test/Runtime QA commands strictly inside `WORKTREE_PATH` (use absolute paths inside `WORKTREE_PATH` or `cd "<WORKTREE_PATH>" && ...`).
   - For Rust repos, set `CARGO_TARGET_DIR="<main_repo>/target"` when `compile_gate_owner=true` to reuse compiled crate cache cleanly.
   - `希格雯` audits strictly via `git -C "<WORKTREE_PATH>" status --short` and `python "<wt_script>" diff --repo "<main_repo>" --slug "<slug>"`, confirming `MAIN_REPO_ROOT` remained untouched.
3. **Codex-Style Landing Choice (User Decides How to Land)**:
   After single-pass audit passes, ask the user naturally (via `AskUserQuestion`) how to land the tested changes:
   - **`apply-patch` (Codex "Apply to local")**: `python "<wt_script>" land --repo "<main_repo>" --slug "<slug>" --mode apply-patch` -> applies clean working-tree diff onto `MAIN_REPO_ROOT` without creating a merge commit!
   - **`squash-merge`**: `python "<wt_script>" land --repo "<main_repo>" --slug "<slug>" --mode squash-merge --commit-message "<msg>"` -> lands as 1 clean sanitized commit on current branch.
   - **`merge`**: Preserves branch commits via `--no-ff`.
   - **`keep`**: Leaves `akasha/<slug>` branch & folder intact for manual inspection or `git push` PR.
4. **Safe Cleanup**:
   ```bash
   python "<wt_script>" cleanup --repo "<main_repo>" --slug "<slug>" --delete-branch --force
   ```
   *(Automatically unlinks any junctions/symlinks safely before removing the worktree directory—NEVER deletes `MAIN_REPO_ROOT/node_modules`.)*
