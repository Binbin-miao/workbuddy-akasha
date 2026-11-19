---
name: matt-2026-suite
description: Matt Pocock + gstack + GSD 融合工程套件（v9.1）：以自然易懂的人话进行 6 维深度需求对齐、Ousterhout 删除测试、Diff-Aware 运行时 QA、TDD 实测否决权与三段式 PR/Retro。
---

# Deep-Grilling, Spec & Verification Suite (v9.1)

## 1. DEEP GRILLING MATRIX (THOROUGH BACKSTAGE, COMFORTABLE FRONTSTAGE)
Before writing `spec.md`, interrogate all 6 dimensions internally (skip any genuinely N/A):
1. **Goal, Scope & Non-Goals**: Must-Have v1 vs explicitly Out-of-Scope.
2. **Concrete User Flows & Interaction Details**: Triggers, hotkeys, layout density, visual states, feedback messages.
3. **Edge Cases, Zero-Value & Failure Modes**: `count == 0`, empty input, duplicate click/trigger, timeout, permission failure, cancel/rollback.
4. **Architecture, Data & Contracts**: Input/output schema, persistence, sync vs async, OS/browser runtime target.
5. **Legacy Parity & Compatibility**: Existing defaults/auto-scaling/features that MUST NOT regress or degrade into manual steps.
6. **Acceptance Criteria & Word Report Focus**: Exact runtime check proving it works + what the user wants highlighted in the `.docx` report.

### Conversational Grilling Rules (Comfortable UX)
- **Verify Code First**: Read `aoci.code.txt` before asking. Never ask facts already visible in code.
- **Speak Plain User Language**: Frame options in terms of real user experience and behavior, NOT internal jargon (`G5`, `SSOT`, `FRAS`, `Phase 1.5`).
- **Table Only When Worth It**: Only show a compact comparison table when contrasting 2–3 genuinely distinct architectural approaches. For straightforward choices, a crisp 1-sentence explanation + `AskUserQuestion` is much more comfortable.
- **Progressive 1–2 Waves + Respect User Pace**:
  - *Wave 1 (Core Scope & Experience)*: 3–4 clear questions with `（推荐）` defaults.
  - *Wave 2 (Remaining Edge Cases & Acceptance)*: 2–4 questions ONLY for unresolved gray areas, with `"其余细节按推荐方案来就行，直接开做（推荐）"`.
  - If the user says *"你决定就行"*, accept the recommended defaults smoothly and persist to `.scratch/<feature>/CONTEXT.md`.

## 2. DEEP MODULE DESIGN & DIFF-AWARE RUNTIME QA
- **Ousterhout Deletion Test**: Remove shallow pass-through wrappers; expose narrow, deep module interfaces.
- **Diff-Aware Runtime QA**: After unit tests pass, execute the actual changed user flow (CLI run, API call, or headless browser check for Web UI) and record observable evidence.
- **Empirical Veto Right**: Existing passing tests are invariant. Never delete or weaken passing tests to fit a speculative spec constant; return calculation proof and update `spec.md`.
- **PR & Retro**: Format PRs strictly as `## Summary / ## Evidence / ## Merge Danger` (zero private paths/narratives). Distill 1–3 rules into `.learnings/USER_RULES.md` and AOCI `S`.
