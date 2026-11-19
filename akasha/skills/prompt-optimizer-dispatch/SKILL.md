---
name: prompt-optimizer-dispatch
description: 低 Token 增量派单编译器（融合 Prompt Optimizer + context-mode + caveman 通信压缩）：7位专家精准双参数映射、AOCI 指针注入、工具日志裁剪与 429 自动无损续派。
---

# Token-Optimal Subagent Dispatch & Recovery Protocol (v9.0)

## 1. MANDATORY `Agent` PARAMETER MAPPING (7 SPECIALISTS)
Every `Agent` call MUST pass BOTH exact `subagent_type` and exact Chinese `name`:
| Role | `subagent_type` (Exact String) | `name` (`akasha` 虚空) | `name` (`yuan` 源) |
|---|---|---|---|
| AOCI Cartographer | `"aoci-codebase-cartographer"` | `"艾尔海森"` | `"天衡"` |
| Grilling & Spec Architect | `"domain-grilling-architect"` | `"纳西妲"` | `"璇玑"` |
| TDD, Runtime QA & Docx | `"deep-module-tdd-engineer"` | `"可莉"` | `"巧夺"` |
| UI & Modern Web Director | `"impeccable-design-director"` | `"心海"` | `"玲珑"` |
| Single-Pass Diff Auditor | `"ponytail-simplicity-gatekeeper"` | `"希格雯"` | `"澄澈"` |
| Web & Benchmark Recon | `"scrapling-web-intelligence"` | `"早柚"` | `"浮光"` |

## 2. ULTRA-COMPACT 6-SECTION DISPATCH TEMPLATE (TOKEN-SAVING)
Pass ONLY file pointers + delta constraints (NEVER paste full files, long chat logs, or boilerplate rules):
```markdown
# 1. [Role|Phase] {{ZH_Name}} (`{{ID}}`) | Phase: {{Phase}}
# 2. [Pointer Context] Repo: `{{own_repo|external_pr}}` | AOCI: `{{aoci_code_path}}` | Context: `.scratch/{{feature}}/CONTEXT.md` | Spec: `.scratch/{{feature}}/spec.md`
# 3. [Delta Rules] {{Only_Relevant_USER_RULES_1_to_3_Bullets}}
# 4. [Goal & Lock] Deliverable: {{Imperative_Goal}} | WriteLock: `{{Whitelist_Or_READ_ONLY}}` | CompileOwner: `{{true|false}}`
# 5. [Bounds] MaxCalls: `<= {{Budget}}` | SinglePassReviewCap: `1` | BreakLoop: `2 fails` | Read AOCI first (no blind repo scan).
# 6. [Gate & Return] Run: `{{Exact_Verify_Cmd}}` -> Dual-return (`SendMessage` to `akasha-team-lead` + final output) in `<=30` dense machine-terse lines (strip verbose stdout; report exit code + delta + exact `File:Line` only).
```

## 3. INTER-AGENT COMPRESSION (`context-mode` + `caveman` Principles)
- **Clip Noisy Logs**: Never paste >20 lines of raw build/test stdout into `SendMessage`. Report `CMD | EXIT=0 | TESTS=X->Y | FAIL=0` plus only failing assertion lines.
- **Zero Prose Padding**: Inter-agent handoffs use terse key-value bullets (`File:Line`, `Delta`, `Blocker`, `Proof`). Save fluent prose strictly for the final Word `.docx` report.

## 4. SUBAGENT `429` / SESSION FAILURE AUTO-RECOVERY
If any subagent fails with `429`, rate limit, timeout, or `Ambiguous durable subagent session`:
1. NEVER halt to show the 429 error to the user, NEVER code manually as Lead, NEVER pass `resume`.
2. Run `git status --short && git diff --stat` to capture partial worktree progress.
3. Immediately spawn a fresh `Agent(subagent_type=..., name=...)` without `resume`, injecting the verified partial state + remaining items.
