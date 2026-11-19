# 虚空 (Akasha / `akasha`) v9.1.0 — 自然对话前台 × 七人严谨工程后台

遵循 [WorkBuddy 开放平台《专家团》官方规范](https://open.workbuddy.cn/docs/expert-team) 构建的 **v9.1 七人全栈研发专家团**：前台像顺手好用的日常 AI 助手一样自然交流，后台全自动执行高标准工程闭环。

## 五大核心能力

1. **前台自然对话 × 后台严谨工程分离（v9.1 重点升级）**
   - 主理人（派蒙）内置 `<USER_COMMUNICATION_PROTOCOL>`：彻底隐藏内部流水号与工程黑话（不再向用户报 `Phase 1A/1.5`、`SSOT`、`FRAS`、`S1 BLOCK`、`Exit Code 0`），废除生硬的四段式表情包汇报模板。
   - 新增 **Workflow 0 日常对话直通通道**：闲聊、咨询、讨论方案时像普通 AI 一样直接自然回复，不强行拉流程、不乱弹框、不硬塞报告。
   - 提问围绕真实体验与取舍用大白话交流，仅在真正需要对比架构大方案时才附精简表格。
2. **专职 AOCI 机器索引测绘官（艾尔海森 `aoci-codebase-cartographer`）**
   - 配套确定性预扫器 `skills/aoci-cognition/scripts/aoci_prescan.py`（SHA-256 增量漂移检测），生成标准 `aoci.txt / aoci.meta.txt / aoci.code.txt`，其余专家直读零盲扫，节省 60%–80% 探索 Token。
3. **6 维灰区温和深度对齐**
   - `纳西妲` 从目标边界、交互流、空态/失败边界、数据契约、存量防退化、验收标准 6 维识别灰区；`派蒙` 翻译成通俗易懂的 1–2 轮递进弹窗选项（带推荐默认值与一键推进）。
4. **确定性门禁 + Diff-Aware 运行时 QA + 单轮终审上限**
   - `可莉` 前置实跑编译/测试/真实端到端 QA 消灭 Bug；`希格雯` 仅做 **最多 1 轮 Diff-Only 高置信度终审**（`<=10` 次调用），杜绝反复审校烧 Token。
5. **任务收尾自动交付专业 Word (`.docx`) 进度报告**
   - 内置 `docx-delivery-reporter` 技能与 `scripts/generate_delivery_docx.py`，每次工程/调研/审查任务结束自动生成排版工整的 `.docx` 报告，聊天窗口只给轻松简洁的结论与文件路径。
