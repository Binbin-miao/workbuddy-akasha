---
name: trellis-workflow
description: Trellis v9.0 低 Token 高质量工作流：集成专职 AOCI 测绘（Phase 0.5）、GSD 干净上下文分片、确定性门禁+运行时 QA、单轮审校硬上限（杜绝反复审校烧 Token）与自动 Word 交付收口。
---

# Trellis v9.0 Token-Efficient Structured Workflow

## 1. SINGLE SSOT ARTIFACT TREE
- `.scratch/aoci/{aoci.txt, aoci.meta.txt, aoci.code.txt, baseline.json}`: Machine-readable AOCI CognitionSet (owned exclusively by `艾尔海森`).
- `.scratch/codebase-architecture.md` & `GLOSSARY.md`: High-level architecture & Legacy Parity baseline.
- `.scratch/<feature>/CONTEXT.md`: Locked user preferences from Deep Grilling (`AskUserQuestion`).
- `.scratch/<feature>/spec.md`: Single authoritative engineering specification & Acceptance Criteria.
- `.scratch/<feature>/implement.jsonl` & `check.jsonl`: Machine coordinates (`exclusive_file_lock`, `compile_gate_owner`, deterministic checks).
- `.scratch/<feature>/deliverables/<YYYYMMDD>-<feature>-delivery-report.docx`: Mandatory Word progress & delivery report.
- `.learnings/USER_RULES.md` & `.learnings/SESSION_JOURNAL.md`: Project memory ledger.

## 2. FIVE ORTHOGONAL PHASES (WITH HARD ANTI-LOOP CIRCUIT BREAKERS)
1. **Phase 0.5 (Dedicated AOCI Cartography — `艾尔海森`)**:
   - Run `aoci_prescan.py` -> if 0 drift, return cache hit in 1 turn; otherwise update ONLY drifted `F|R|A|S` entries in `aoci.code.txt`.
2. **Phase 1A & 1.5 (Deep Grilling & Gray-Area Lock — `纳西妲` + `派蒙`)**:
   - `纳西妲` reads `aoci.code.txt` (NO blind repo sweep!), identifies all gray areas across Scope, User Flow/Edge Cases, Data/API/Legacy Parity, and UI/UX/Acceptance.
   - `派蒙` executes **Structured Deep Grilling** via `AskUserQuestion` (up to 2 progressive waves; always includes recommended defaults + fast-pass option).
   - `纳西妲` writes `CONTEXT.md`, `spec.md`, `implement.jsonl`, `check.jsonl` (Phase 1B, `<=6` calls).
3. **Phase 2 (Fresh-Context TDD + Deterministic Gate + Diff-Aware Runtime QA — `可莉`)**:
   - Reads `aoci.code.txt` + `CONTEXT.md` + `spec.md` in a clean context window.
   - Writes failing tests first -> minimal deep-module implementation -> runs **Deterministic Gate** (compile/typecheck/lint/unit/integration) + **Diff-Aware Runtime QA** (actually execute changed CLI/API/UI paths and verify real behavior!).
   - **`trellis-break-loop`**: Same error fails 2 consecutive times -> STOP guessing, inspect runtime trace & AOCI `S` invariants.
4. **Phase 3 (SINGLE-PASS Diff-Only Audit — `希格雯`, HARD CAP = 1 WAVE)**:
   - Runs ONLY AFTER `可莉` achieves real `Exit Code 0` + Runtime QA pass.
   - Reads ONLY `aoci.code.txt` impacted `R/S` + `git diff` + test/QA evidence (`<=10` tool calls).
   - **ZERO PING-PONG RULE**: Max **1** audit wave! If `[S1 BLOCK]` is raised, allow at most **1** targeted fix by `可莉` + deterministic re-verify. NEVER enter a 2nd/3rd LLM review loop; escalate unresolved S1 directly to the user with evidence.
5. **Phase 4 (AOCI Delta Sync + Mandatory Word `.docx` Report)**:
   - `艾尔海森` refreshes changed `F|R|A|S` lines; `可莉` (or `派蒙` via script) runs `generate_delivery_docx.py` to deliver the `.docx` progress report; update `SESSION_JOURNAL.md` & `USER_RULES.md`.
