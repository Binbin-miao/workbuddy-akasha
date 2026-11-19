#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AOCI Deterministic Pre-Scanner & SHA-256 Drift Detector (v9.0)
Purpose:
- Replaces 15-20 expensive LLM glob/ls/grep calls with 1 deterministic local run.
- Computes SHA-256 checksums against `.scratch/aoci/baseline.json` to identify
  exact ADDED / MODIFIED / DELETED managed files.
- Extracts lightweight structural metadata (size tier L/M/S/T, line count, top imports/exports)
  STRICTLY as reading hints. Per AOCI-CODE v0.2 spec, actual F|R|A|S business semantics
  MUST be authored by `aoci-codebase-cartographer` (艾尔海森) after reading source files.
"""
import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

IGNORED_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "target", "dist", "build", "out",
    ".next", ".nuxt", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".scratch", ".learnings", ".aoci",
    ".idea", ".vscode", "coverage", "vendor", "Pods", ".gradle",
}
IGNORED_EXTS = {
    ".lock", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".bmp",
    ".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".pdf", ".docx", ".xlsx",
    ".pptx", ".zip", ".tar", ".gz", ".7z", ".exe", ".dll", ".so", ".dylib",
    ".wasm", ".ttf", ".otf", ".woff", ".woff2", ".pyc", ".class", ".o", ".a",
    ".min.js", ".min.css", ".map", ".db", ".sqlite", ".sqlite3",
}
IGNORED_NAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock",
    "poetry.lock", "uv.lock", "composer.lock", "Gemfile.lock",
    "aoci.txt", "aoci.meta.txt", "aoci.code.txt", "aoci.database.txt",
}

SYMBOL_RE = re.compile(
    r"^(?:export\s+)?(?:async\s+)?(?:pub(?:\([^)]*\))?\s+)?"
    r"(?:fn|def|class|struct|enum|trait|interface|type|const|function)\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.MULTILINE,
)


def size_tier(lines: int) -> str:
    if lines >= 400:
        return "L"
    if lines >= 150:
        return "M"
    if lines >= 40:
        return "S"
    return "T"


def is_binary_bytes(chunk: bytes) -> bool:
    return b"\x00" in chunk


def scan_repo(repo_root: Path):
    files = {}
    for root, dirs, filenames in os.walk(repo_root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".tmp"))
        for fname in sorted(filenames):
            if fname in IGNORED_NAMES or fname.endswith((".bak", ".tmp")):
                continue
            fpath = Path(root) / fname
            suffix = fpath.suffix.lower()
            if suffix in IGNORED_EXTS or fname.endswith((".min.js", ".min.css")):
                continue
            try:
                raw = fpath.read_bytes()
            except OSError:
                continue
            if len(raw) > 512 * 1024 or is_binary_bytes(raw[:4096]):
                continue
            rel = fpath.relative_to(repo_root).as_posix()
            sha = hashlib.sha256(raw).hexdigest()[:16]
            text = raw.decode("utf-8", errors="ignore")
            lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
            syms = SYMBOL_RE.findall(text)[:10]
            files[rel] = {
                "sha256": sha,
                "lines": lines,
                "size": size_tier(lines),
                "symbols": syms,
            }
    return files


def main():
    parser = argparse.ArgumentParser(description="AOCI Deterministic Pre-Scanner & Drift Detector")
    parser.add_argument("--repo", default=".", help="Repository root path")
    parser.add_argument("--baseline", default=".scratch/aoci/baseline.json", help="Baseline JSON path")
    parser.add_argument("--commit-baseline", action="store_true", help="Write current scan as new baseline")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    baseline_path = Path(args.baseline)
    if not baseline_path.is_absolute():
        baseline_path = repo_root / baseline_path

    current = scan_repo(repo_root)
    previous = {}
    if baseline_path.exists():
        try:
            previous = json.loads(baseline_path.read_text(encoding="utf-8")).get("files", {})
        except Exception:
            previous = {}

    added = [p for p in current if p not in previous]
    modified = [p for p in current if p in previous and current[p]["sha256"] != previous[p].get("sha256")]
    deleted = [p for p in previous if p not in current]
    unchanged_count = len(current) - len(added) - len(modified)

    if args.commit_baseline:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "aoci-baseline/v1",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "file_count": len(current),
            "files": current,
        }
        baseline_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "repo": str(repo_root),
        "total_managed_files": len(current),
        "unchanged": unchanged_count,
        "added": [{**current[p], "path": p} for p in added],
        "modified": [{**current[p], "path": p} for p in modified],
        "deleted": deleted,
        "baseline_committed": args.commit_baseline,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
