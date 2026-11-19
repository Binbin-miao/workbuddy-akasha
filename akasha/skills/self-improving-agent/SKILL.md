---
name: self-improving-agent
description: 双层作用域隔离记忆与自进化协议（v9.1）：跨会话沉淀用户偏好（含自然人话前台交流、AOCI 直读、深度对齐、单轮终审与自动 Word 交付），强制限容、去重覆盖与零 PII 脱敏。
---

# Self-Improving Agent Memory Protocol (v9.1)

## 1. TWO-TIER SCOPED STORAGE
1. **Project Ledger (`.learnings/USER_RULES.md` & `.learnings/SESSION_JOURNAL.md`)**:
   - Stores repository-specific AOCI invariants, exact build/test/QA commands, UI tab rules, and retro lessons (hidden via `.git/info/exclude`).
2. **Global Profile (`~/.workbuddy/memory/user-coding-profile.md`)**:
   - Stores ONLY universal cross-project preferences:
     * **Natural Frontstage Chat**: Lead communicates like a normal, warm, clear AI collaborator—zero internal phase codes, zero SOP jargon, zero robotic emoji templates, and zero unnecessary walls of text.
     * Dedicated AOCI Cartographer (`艾尔海森`) updates machine-readable `aoci.code.txt` first; all other agents read it directly instead of blind repo scans.
     * Thorough yet conversational 6-dimension `AskUserQuestion` alignment before coding (plain language, recommended defaults, fast-pass option).
     * Deterministic gate + Diff-Aware Runtime QA first; single-pass diff-only audit (MAX 1 review wave, zero token-wasting review ping-pong).
     * Automatic polished Word (`.docx`) delivery & progress report on every completed task via `generate_delivery_docx.py`.
     * Zero solo coding by Lead; out-of-the-box auto-scaling defaults; master switch on top; `<=12` config tabs; zero flashing outer borders; flat guard clauses (`<=3` levels); RAII/atomic persistence/public-ledger sanitization.
   - **NEVER write project-specific paths, secrets, or local IPs into global profile.**

## 2. READ/WRITE TRIGGERS & BOUNDED CAPACITY
- **Phase 0 Read**: Read global profile + `.learnings/USER_RULES.md` + `.learnings/SESSION_JOURNAL.md` (project rules override global on conflict).
- **Write-On-Feedback**: Update immediately after user `AskUserQuestion` decisions, user corrections, or `retro`.
- **Capacity**: Max `<=80` rules (`<=200` lines) per file; replace superseded rules in-place.
```markdown
### [RULE-00X] <Imperative Rule Title> (Updated: YYYY-MM-DD | Scope: project|global)
- **Trigger**: <When> | **Action**: <Required behavior> | **Ban**: <Anti-pattern>
```
