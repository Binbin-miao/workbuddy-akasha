---
name: clean-code-and-commit-guard
description: 确定性门禁左移、Ponytail 六级消肿、五大隐性防呆、单轮差分终审与公私双账本脱敏门禁（v9.0：用自动化测试与运行时 QA 抓 Bug，严禁多轮 LLM 空转审核）。
---

# Deterministic-First Clean Code & Sanitization Guard (v9.0)

## 1. SHIFT-LEFT BUG PREVENTION (WHY REVIEW LOOPS FAIL)
LLM review loops burn tokens and still miss runtime bugs. Catch defects deterministically BEFORE review:
1. **Static Gate**: Compiler (`cargo check`/`tsc --noEmit`), strict linter (`clippy`/`eslint`/`ruff`), zero warnings on touched files.
2. **Test Gate**: Unit + integration regression tests wired into root test runner (`N_after > N_before`).
3. **Diff-Aware Runtime QA**: Execute the real modified code path (CLI run, API call, or headless browser check for UI) covering happy path + empty/error boundary.

## 2. CODE AESTHETICS, PONYTAIL L1-L6 & 5 SAFETY GUARDS
- **Structure**: Flat early-return guards (`<=3` nesting), declarative lookup tables, `Parse, Don't Validate` at boundaries.
- **Ponytail L1-L6**:
  - `L1` Delete dead code, zero-caller helpers, and comments contradicting defaults.
  - `L2` Prefer standard library / Modern Web Baseline primitives.
  - `L3` Deduplicate logic & unify shared constants.
  - `L4` Flatten deep conditionals.
  - `L5` Inline shallow pass-through wrappers failing Ousterhout's Deletion Test.
  - `L6` Kill `O(N^2)` hot loops, loop log spam, and random video `set(POS_FRAMES)` seeks.
- **Five Safety Guards (`G1-G5`)**:
  - `G1` RAII / `finally` lock release + fail-closed outside-click capture cancel.
  - `G2` Pure read paths (zero disk write side effects) + UI `request_repaint` waker.
  - `G3` Atomic persistence: `backup -> .tmp -> fsync -> atomic rename -> rollback`.
  - `G4` Async unmount guard (`disposed` / `AbortController`).
  - `G5` Zero-value predicate (`count == 0` never deadlocks Save) + visible startup conflict UI event.

## 3. SINGLE-PASS COMMIT & SANITIZATION GATE (`[S1 BLOCK]`)
- **Single-Pass Rule**: Audit `git diff` + impacted AOCI `R/S` + deterministic QA proof ONCE (`Confidence >= 85%` only; ZERO style nitpicks).
- **Git Integrity**:
  - `.git/info/exclude` hides `.scratch/`, `.learnings/`, `.aoci/`, `.mcp.json`, `*.bak*`, `*.tmp*` (plus root `aoci*.txt` in `external_pr`).
  - NEVER run `git add .` / `git add -A`. ZERO `MM` (partially staged) files. Every commit compiles & passes tests independently.
- **Public-Private Ledger Sanitization**:
  - Zero local machine paths (`C:\Users\...`, `/Users/...`), internal IPs/hostnames, real secrets, or personal debugging stories (`"本地测了三把"`, `"修上一轮改坏的"`) in code, tests, commits, or PRs.
