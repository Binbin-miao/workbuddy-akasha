# 虚空 (Akasha) v9.1.0 — WorkBuddy 七人研发专家团

前台像日常 AI 助手一样自然对话，后台自动跑完整工程闭环：需求对齐、Spec 落盘、TDD 实现、独立终审、Word 交付报告。

面向 **WorkBuddy / CodeBuddy** 的专家团队插件，共 **7 位角色 + 8 项内置技能**。

## 阵容

| 角色 | Agent ID | 职责 |
| --- | --- | --- |
| 派蒙 | `akasha-team-lead` | 主理人：需求对齐、任务调度、收尾汇总 |
| 艾尔海森 | `aoci-codebase-cartographer` | 代码库测绘：生成标准机器索引，其余成员直读免盲扫 |
| 纳西妲 | `domain-grilling-architect` | 架构分析、Spec 与工单建模、并发不变量 |
| 可莉 | `deep-module-tdd-engineer` | TDD 实现、编译与端到端门禁实跑 |
| 心海 | `impeccable-design-director` | 界面审美、交互状态完备性、多视口走查 |
| 希格雯 | `ponytail-simplicity-gatekeeper` | 代码精简、单轮 Diff 终审、本地事件泄漏拦截 |
| 早柚 | `scrapling-web-intelligence` | 开源先例检索、反爬网页情报 |

## 内置技能 (8)

`aoci-cognition` · `docx-delivery-reporter` · `trellis-workflow` · `matt-2026-suite` · `prompt-optimizer-dispatch` · `self-improving-agent` · `clean-code-and-commit-guard` · `modern-web-guidance`

其中 `aoci-cognition` 与 `docx-delivery-reporter` 自带 Python 脚本（代码库预扫、Word 报告生成）。

## 安装

### 方式一：交给 AI 装

把本仓库克隆或下载为压缩包后发给 WorkBuddy 的 AI，说一句：

> 帮我装这个专家团

AI 会放到专家目录、补齐校验并完成注册。

### 方式二：手动装

1. 把 `akasha/` 整个文件夹放进：
   - Windows：`%USERPROFILE%\.workbuddy\plugins\marketplaces\my-experts\plugins\`
   - macOS / Linux：`~/.workbuddy/plugins/marketplaces/my-experts/plugins/`
2. 重启 WorkBuddy，在「专家中心 → 我的专家」中即可看到。

### 可选：同步内置技能到全局

内置技能可以只在插件内生效，也可以复制到全局技能库供其他会话使用：

```bash
python akasha/sync_v9_skills_safe.py
```

该脚本采用白名单，只处理上列 8 个技能，不会改动你本机其他技能。

## 依赖

`docx-delivery-reporter` 生成 Word 报告需要 `python-docx`：

```bash
python -m pip install python-docx
```

不装也不影响其他功能，只是收尾时无法输出 `.docx`。

## 目录结构

```
akasha/
├── .codebuddy-plugin/plugin.json   # 插件元信息
├── agents/                         # 7 位角色定义
├── avatars/                        # 8 张头像
├── skills/                         # 8 项内置技能
├── settings.json                   # 主理人指定
└── sync_v9_skills_safe.py          # 技能同步脚本（可选）
```

## 版权

Copyright (c) 2026 Binbin-miao. 保留所有权利。

本仓库内容公开发布供学习与个人使用，未附加开源许可协议；未经作者书面许可，不得用于商业用途、不得二次分发或发布衍生版本。
