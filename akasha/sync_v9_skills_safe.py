#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safe Additive-Only Skill Installer for Akasha v9.0
Copies the 9 v9.2 exclusive skills (including scripts/) to ~/.workbuddy/skills/.
Pass --update-v9 to overwrite existing copies of these 8 skills only.
"""
import shutil
import sys
from pathlib import Path

V9_EXCLUSIVE_SKILLS = [
    "aoci-cognition",
    "git-worktree-isolation",
    "docx-delivery-reporter",
    "trellis-workflow",
    "matt-2026-suite",
    "prompt-optimizer-dispatch",
    "self-improving-agent",
    "clean-code-and-commit-guard",
    "modern-web-guidance",
]


def main():
    force_update = "--update-v9" in sys.argv or "--update" in sys.argv
    target_root = Path.home() / ".workbuddy" / "skills"
    target_root.mkdir(parents=True, exist_ok=True)
    local_skills = Path(__file__).resolve().parent / "skills"

    for sname in V9_EXCLUSIVE_SKILLS:
        src = local_skills / sname
        dst = target_root / sname
        if not src.is_dir():
            continue
        if dst.exists() and not force_update:
            print(f"[SKIP] {sname} 已存在于 {dst}（如需更新请加 --update-v9）")
            continue
        if dst.exists() and force_update:
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"[INSTALLED] {sname} -> {dst}")


if __name__ == "__main__":
    main()
