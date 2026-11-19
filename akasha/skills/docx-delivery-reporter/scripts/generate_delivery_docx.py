#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Akasha v9.0 Automatic Delivery Report Generator (.docx)
Generates a clean, executive-ready Word document from a compact JSON manifest
so agents spend ~40 tokens writing structured data instead of 3,000 tokens
re-writing python-docx code on every task.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def render_markdown_fallback(data: dict, out_path: Path) -> Path:
    md_path = out_path.with_suffix(".md")
    lines = [
        f"# {data.get('title', '任务交付与进度说明报告')}",
        "",
        f"- **项目名称**: {data.get('project', '-')}",
        f"- **任务/特性**: {data.get('feature', '-')}",
        f"- **交付日期**: {data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M'))}",
        f"- **总体状态**: {data.get('status', '已完成')}",
        f"- **分支 / Commit**: {data.get('git_ref', '-')}",
        "",
        "## 一、执行摘要",
        data.get("executive_summary", "（未填写）"),
        "",
        "## 二、阶段工作进度",
        "| 阶段 | 负责专家 | 状态 | 核心产物 / 说明 |",
        "|---|---|---|---|",
    ]
    for p in data.get("progress", []):
        lines.append(f"| {p.get('phase','')} | {p.get('owner','')} | {p.get('status','')} | {p.get('note','')} |")
    lines += ["", "## 三、需求对齐与关键决策"]
    for d in data.get("decisions", []):
        lines.append(f"- **{d.get('topic','')}**：{d.get('choice','')}（依据：{d.get('rationale','')}）")
    lines += ["", "## 四、代码与架构变更清单", "| 文件路径 | 变更类型 | 说明 |", "|---|---|---|"]
    for c in data.get("changes", []):
        lines.append(f"| `{c.get('path','')}` | {c.get('action','')} | {c.get('summary','')} |")
    lines += ["", "## 五、自动化门禁与运行时 QA 实证", "| 验证项 / 命令 | 退出码 | 结果详情 |", "|---|---|---|"]
    for v in data.get("verification", []):
        lines.append(f"| `{v.get('command','')}` | {v.get('exit_code','0')} | {v.get('result','')} |")
    lines += ["", "## 六、风险、遗留与下一步建议"]
    for r in data.get("risks_and_next", []):
        lines.append(f"- {r}")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path


def set_cell_shading(cell, fill_hex: str):
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="D0D7DE"):
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/><w:right w:val="none"/><w:insideV w:val="none"/>'
        f"</w:tblBorders>"
    )
    table._tbl.tblPr.append(borders)


def add_heading_styled(doc, text: str):
    from docx.shared import Pt, RGBColor
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(13)
    run.font.color.rgb = RGBColor(0x1B, 0x3B, 0x5C)
    return p


def add_styled_table(doc, headers, rows, col_widths=None):
    from docx.shared import Inches, Pt, RGBColor
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.autofit = False
    set_table_borders(table)

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_shading(hdr_cells[i], "1B3B5C")
        set_cell_margins(hdr_cells[i], 90, 90, 120, 120)
        p = hdr_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(str(h))
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        if col_widths and i < len(col_widths):
            hdr_cells[i].width = Inches(col_widths[i])

    for r_idx, row_vals in enumerate(rows):
        cells = table.rows[r_idx + 1].cells
        bg = "F6F8FA" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_vals):
            set_cell_shading(cells[c_idx], bg)
            set_cell_margins(cells[c_idx], 70, 70, 120, 120)
            p = cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            text = str(val)
            r = p.add_run(text)
            r.font.size = Pt(9)
            if "PASS" in text or "完成" in text or text == "0":
                r.font.color.rgb = RGBColor(0x1A, 0x7F, 0x37)
            elif "FAIL" in text or "阻塞" in text or "风险" in text:
                r.font.color.rgb = RGBColor(0xCF, 0x22, 0x2E)
            else:
                r.font.color.rgb = RGBColor(0x24, 0x29, 0x2F)
            if col_widths and c_idx < len(col_widths):
                cells[c_idx].width = Inches(col_widths[c_idx])
    return table


def build_docx(data: dict, out_path: Path):
    from docx import Document
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    normal = doc.styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(0x24, 0x29, 0x2F)

    # Banner table
    banner = doc.add_table(rows=1, cols=1)
    banner.autofit = False
    bcell = banner.rows[0].cells[0]
    bcell.width = Inches(7.0)
    set_cell_shading(bcell, "1B3B5C")
    set_cell_margins(bcell, 160, 160, 200, 200)
    bp1 = bcell.paragraphs[0]
    bp1.paragraph_format.space_after = Pt(4)
    br1 = bp1.add_run(data.get("title", "虚空 Akasha 任务交付与进度说明报告"))
    br1.bold = True
    br1.font.size = Pt(16)
    br1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    bp2 = bcell.add_paragraph()
    bp2.paragraph_format.space_after = Pt(0)
    br2 = bp2.add_run(
        f"项目：{data.get('project', '-')}   |   任务：{data.get('feature', '-')}   |   状态：{data.get('status', '已完成')}"
    )
    br2.font.size = Pt(9.5)
    br2.font.color.rgb = RGBColor(0xD8, 0xE6, 0xF3)

    # Metadata grid
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    meta_rows = [
        ["交付时间", data.get("date", datetime.now().strftime("%Y-%m-%d %H:%M")), "Git 分支 / Commit", data.get("git_ref", "-")],
        ["AOCI 索引状态", data.get("aoci_status", "已同步"), "测试总数变化", data.get("test_delta", "-")],
    ]
    add_styled_table(doc, ["属性", "值", "属性", "值"], meta_rows, [1.2, 2.3, 1.3, 2.2])

    # 1. Executive Summary
    add_heading_styled(doc, "一、执行摘要与交付成果")
    p_sum = doc.add_paragraph(data.get("executive_summary", "本次任务已完成核心目标并通过自动化验证。"))
    p_sum.paragraph_format.space_after = Pt(6)
    for item in data.get("deliverables", []):
        bp = doc.add_paragraph(style="List Bullet")
        bp.paragraph_format.space_after = Pt(3)
        bp.add_run(str(item))

    # 2. Progress
    add_heading_styled(doc, "二、阶段工作进度追踪")
    prog_rows = [
        [p.get("phase", ""), p.get("owner", ""), p.get("status", ""), p.get("note", "")]
        for p in data.get("progress", [])
    ] or [["全流程", "Akasha 专家团", "已完成", "无分阶段明细"]]
    add_styled_table(doc, ["阶段", "负责专家", "状态", "核心产物与进展"], prog_rows, [1.3, 1.1, 0.9, 3.7])

    # 3. Grilling Decisions
    if data.get("decisions"):
        add_heading_styled(doc, "三、需求审讯与关键决策对齐")
        dec_rows = [
            [d.get("topic", ""), d.get("choice", ""), d.get("rationale", "")]
            for d in data.get("decisions", [])
        ]
        add_styled_table(doc, ["决策维度", "拍板方案", "工程依据 / 边界约束"], dec_rows, [1.5, 2.2, 3.3])

    # 4. Changes & AOCI impact
    add_heading_styled(doc, "四、代码、架构与 AOCI 认知变更清单")
    chg_rows = [
        [c.get("path", ""), c.get("action", ""), c.get("summary", "")]
        for c in data.get("changes", [])
    ] or [["（无源码改动）", "-", "纯调研/文档任务"]]
    add_styled_table(doc, ["文件路径", "操作", "变更要点与影响范围"], chg_rows, [2.6, 0.8, 3.6])

    # 5. Deterministic Gate & Runtime QA
    add_heading_styled(doc, "五、自动化门禁与运行时 QA 实证")
    ver_rows = [
        [v.get("command", ""), str(v.get("exit_code", "0")), v.get("result", "")]
        for v in data.get("verification", [])
    ] or [["（未记录命令）", "-", "-"]]
    add_styled_table(doc, ["验证命令 / QA 检查项", "退出码", "实测结果与覆盖证据"], ver_rows, [2.8, 0.7, 3.5])

    # 6. Risks & Next Steps
    add_heading_styled(doc, "六、已知风险、遗留项与下一步建议")
    for item in data.get("risks_and_next", ["当前无阻塞遗留项。"]):
        bp = doc.add_paragraph(style="List Bullet")
        bp.paragraph_format.space_after = Pt(3)
        bp.add_run(str(item))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate Akasha v9.0 Word (.docx) Delivery Report")
    parser.add_argument("--input", required=True, help="Path to delivery_report.json")
    parser.add_argument("--output", required=True, help="Output .docx path")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out_path = Path(args.output)

    try:
        import docx  # noqa: F401
    except ImportError:
        md_fallback = render_markdown_fallback(data, out_path)
        print(
            json.dumps(
                {
                    "status": "fallback_markdown",
                    "reason": "python-docx not installed (run: pip install python-docx)",
                    "fallback_path": str(md_fallback),
                },
                ensure_ascii=False,
            )
        )
        sys.exit(0)

    final_path = build_docx(data, out_path)
    print(json.dumps({"status": "ok", "docx_path": str(final_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
