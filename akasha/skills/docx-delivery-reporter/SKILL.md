---
name: docx-delivery-reporter
description: 自动 Word (.docx) 交付与进度报告协议：每次任务收尾由脚本确定性生成排版规范的 Word 说明文档，报告执行摘要、阶段进度、需求决策、变更清单、门禁实证与风险建议，零 LLM 样板 Token 消耗。
---

# Automatic Word (.docx) Delivery Report Protocol (v9.0)

## 1. MANDATORY DELIVERY RULE
- **EVERY completed task** (Workflow A Feature/Refactor, Workflow B Bugfix, Workflow C Review/Commit, or standalone Research/Indexing) MUST produce a polished **Word document (`.docx`)** before the final summary is sent to the user.
- **Default Output Path**:
  - `.scratch/<feature>/deliverables/<YYYYMMDD>-<feature>-delivery-report.docx` (or the user's explicitly requested path).
  - Ensure `.scratch/` is listed in `.git/info/exclude` so internal reports never pollute external PRs.

## 2. ZERO-TOKEN-WASTE SCRIPT WORKFLOW (2 STEPS)
NEVER write ad-hoc `python-docx` layout code from scratch. Use the bundled deterministic generator:
1. Write a compact JSON manifest at `.scratch/<feature>/delivery_report.json`:
   ```json
   {
     "title": "任务交付与进度说明报告：<任务名>",
     "project": "<仓库名>",
     "feature": "<feature-slug>",
     "date": "YYYY-MM-DD HH:MM",
     "status": "已完成 / 已通过门禁",
     "git_ref": "<branch @ short-sha>",
     "aoci_status": "已对齐 (N files, 0 drift)",
     "test_delta": "N_before -> N_after (0 failed)",
     "executive_summary": "<2-4句高密度成果总结>",
     "deliverables": ["核心产出1", "核心产出2"],
     "progress": [
       {"phase": "Phase 0.5 AOCI测绘", "owner": "艾尔海森", "status": "完成", "note": "增量更新 X 条 FRAS 索引"},
       {"phase": "Phase 1 深度审讯与Spec", "owner": "纳西妲", "status": "完成", "note": "对齐 X 项边界并落盘 spec.md"},
       {"phase": "Phase 2 TDD与运行时QA", "owner": "可莉", "status": "完成", "note": "实现并实跑门禁 Exit Code 0"},
       {"phase": "Phase 3 单轮终审与脱敏", "owner": "希格雯", "status": "PASS", "note": "单轮 Diff 终审零 S1 缺陷"}
     ],
     "decisions": [
       {"topic": "<决策维度>", "choice": "<用户拍板方案>", "rationale": "<边界与依据>"}
     ],
     "changes": [
       {"path": "<file>", "action": "修改/新增/删除", "summary": "<精炼变更说明>"}
     ],
     "verification": [
       {"command": "<真实执行命令或QA步骤>", "exit_code": "0", "result": "<实测输出摘要>"}
     ],
     "risks_and_next": ["剩余低风险项或下一步建议"]
   }
   ```
2. Run the bundled generator script (locate via installed skill path `~/.workbuddy/skills/docx-delivery-reporter/scripts/generate_delivery_docx.py` or plugin path):
   ```bash
   python "<script_path>" --input ".scratch/<feature>/delivery_report.json" --output ".scratch/<feature>/deliverables/<YYYYMMDD>-<feature>-delivery-report.docx"
   ```
3. Verify the JSON output reports `"status": "ok"` and return the exact `.docx` absolute/relative file path in the final 4-line user response. (If `python-docx` is missing, install once via `pip install python-docx` if permitted, or report the fallback `.md` path + 1-line install command.)
