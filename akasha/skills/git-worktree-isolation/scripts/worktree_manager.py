#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Akasha v9.2 Codex-Style Git Worktree Manager
Zero-dependency Python CLI bringing Codex-like isolated worktrees to WorkBuddy.

Features:
- Sibling worktree layout outside repo root (<parent>/.akasha-worktrees/<repo>/<slug>)
  to avoid nested-repo scanner pollution & Windows MAX_PATH issues.
- Keeps main workspace 100% untouched; optional non-destructive --include-dirty
  snapshot via `git stash create` + `git apply`.
- Automatically excludes `.akasha-worktree.json` in main `.git/info/exclude`.
- Safe `.env*` local config copy so Runtime QA runs immediately.
- Optional safe junction/symlink for `node_modules` with safe pre-unlink on cleanup.
- 4 Codex-style landing modes: `apply-patch`, `squash-merge`, `merge`, `keep`.
- Clean graceful fallback JSON (`fallback_in_place`) for non-git folders or 0-commit repos.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

META_FILENAME = ".akasha-worktree.json"
DEFAULT_EXCLUDE_LINES = [
    ".scratch/",
    ".learnings/",
    ".aoci/",
    ".akasha-worktree.json",
]


def run_git(repo: Path, args, check=False, capture=True):
    cmd = ["git", "-C", str(repo)] + list(args)
    try:
        return subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=check,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(cmd, 127, stdout="", stderr="git binary not found")


def sanitize_slug(raw: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", raw.strip().lower()).strip("-._")
    return slug[:48] or "task"


def ensure_git_exclude(git_common_dir: Path):
    exclude_file = git_common_dir / "info" / "exclude"
    exclude_file.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude_file.read_text(encoding="utf-8", errors="ignore") if exclude_file.exists() else ""
    lines = [ln.strip() for ln in existing.splitlines()]
    to_add = [p for p in DEFAULT_EXCLUDE_LINES if p not in lines]
    if to_add:
        prefix = "" if (not existing or existing.endswith("\n")) else "\n"
        with exclude_file.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(prefix + "\n".join(to_add) + "\n")


def detect_repo_info(repo: Path):
    res = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if res.returncode == 127:
        return {"is_git": False, "reason": "git_binary_not_found"}
    if res.returncode != 0 or res.stdout.strip().lower() != "true":
        return {"is_git": False, "reason": "not_a_git_repo"}

    top = Path(run_git(repo, ["rev-parse", "--show-toplevel"], check=True).stdout.strip()).resolve()
    common_raw = run_git(top, ["rev-parse", "--git-common-dir"], check=True).stdout.strip()
    common_dir = Path(common_raw)
    if not common_dir.is_absolute():
        common_dir = (top / common_dir).resolve()
    else:
        common_dir = common_dir.resolve()

    head_res = run_git(top, ["rev-parse", "--verify", "HEAD"])
    if head_res.returncode != 0:
        return {
            "is_git": True,
            "has_commits": False,
            "repo_root": str(top),
            "reason": "no_commits_yet",
        }

    head_sha = head_res.stdout.strip()
    branch = run_git(top, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    status_lines = [ln for ln in run_git(top, ["status", "--short"]).stdout.splitlines() if ln.strip()]
    return {
        "is_git": True,
        "has_commits": True,
        "repo_root": str(top),
        "git_common_dir": str(common_dir),
        "branch": branch,
        "head": head_sha,
        "dirty": len(status_lines) > 0,
        "dirty_count": len(status_lines),
    }


def default_worktree_base(repo_root: Path, custom_root: str = None) -> Path:
    if custom_root:
        return Path(custom_root).expanduser().resolve() / repo_root.name
    return repo_root.parent / ".akasha-worktrees" / repo_root.name


def list_akasha_worktrees(repo_root: Path, custom_root: str = None):
    base = default_worktree_base(repo_root, custom_root)
    results = []
    if not base.is_dir():
        return results
    for child in sorted(base.iterdir()):
        meta_path = child / META_FILENAME
        if child.is_dir() and meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                meta = {"slug": child.name, "worktree_path": str(child)}
            st = run_git(child, ["status", "--short"]).stdout.splitlines()
            ahead_res = run_git(child, ["rev-list", "--count", f"{meta.get('base_commit', 'HEAD')}..HEAD"])
            ahead = int(ahead_res.stdout.strip()) if ahead_res.returncode == 0 and ahead_res.stdout.strip().isdigit() else 0
            meta["dirty_files"] = [ln for ln in st if ln.strip()]
            meta["ahead_commits"] = ahead
            results.append(meta)
    return results


def safe_unlink_link(path: Path):
    """Safely remove symlink or Windows junction WITHOUT deleting target contents."""
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink():
        path.unlink()
        return
    # On Windows, directory junctions are detected via os.path.islink or reparse point;
    # os.rmdir removes a junction safely without touching target files.
    if os.name == "nt":
        try:
            st = os.lstat(path)
            if getattr(st, "st_file_attributes", 0) & 0x0400:  # FILE_ATTRIBUTE_REPARSE_POINT
                os.rmdir(path)
        except OSError:
            pass


def create_dir_link(src_dir: Path, dst_dir: Path) -> bool:
    if not src_dir.is_dir() or dst_dir.exists() or dst_dir.is_symlink():
        return False
    try:
        if os.name == "nt":
            res = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst_dir), str(src_dir)],
                capture_output=True,
                text=True,
            )
            return res.returncode == 0
        os.symlink(src_dir, dst_dir, target_is_directory=True)
        return True
    except OSError:
        return False


def cmd_probe(args):
    info = detect_repo_info(Path(args.repo).resolve())
    if not info.get("is_git") or not info.get("has_commits"):
        info["mode"] = "fallback_in_place"
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return
    info["mode"] = "worktree_ready"
    info["active_worktrees"] = list_akasha_worktrees(Path(info["repo_root"]), args.root)
    print(json.dumps(info, indent=2, ensure_ascii=False))


def cmd_create(args):
    info = detect_repo_info(Path(args.repo).resolve())
    if not info.get("is_git") or not info.get("has_commits"):
        print(
            json.dumps(
                {
                    "status": "fallback_in_place",
                    "reason": info.get("reason", "git_unavailable"),
                    "worktree_path": str(Path(args.repo).resolve()),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    repo_root = Path(info["repo_root"])
    common_dir = Path(info["git_common_dir"])
    ensure_git_exclude(common_dir)

    slug = sanitize_slug(args.slug)
    wt_dir = default_worktree_base(repo_root, args.root) / slug
    branch_name = f"akasha/{slug}"
    base_ref = args.base or "HEAD"
    base_commit = run_git(repo_root, ["rev-parse", base_ref], check=True).stdout.strip()

    # Reuse existing worktree if already active for same slug
    meta_file = wt_dir / META_FILENAME
    if wt_dir.is_dir() and meta_file.is_file():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        meta["status"] = "reused_existing"
        print(json.dumps(meta, indent=2, ensure_ascii=False))
        return

    wt_dir.parent.mkdir(parents=True, exist_ok=True)
    # Check if branch already exists
    branch_exists = run_git(repo_root, ["show-ref", "--verify", f"refs/heads/{branch_name}"]).returncode == 0
    if branch_exists:
        add_res = run_git(repo_root, ["worktree", "add", str(wt_dir), branch_name])
    else:
        add_res = run_git(repo_root, ["worktree", "add", "-b", branch_name, str(wt_dir), base_commit])

    if add_res.returncode != 0:
        print(
            json.dumps(
                {"status": "error", "stderr": add_res.stderr.strip(), "stdout": add_res.stdout.strip()},
                indent=2,
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    copied_envs = []
    if args.copy_env:
        for env_file in sorted(repo_root.glob(".env*")):
            if env_file.is_file() and env_file.name != ".env.example":
                dst = wt_dir / env_file.name
                if not dst.exists():
                    shutil.copy2(env_file, dst)
                    copied_envs.append(env_file.name)

    dirty_carried = False
    if args.include_dirty and info["dirty"]:
        stash_sha = run_git(repo_root, ["stash", "create", "akasha-worktree-snapshot"]).stdout.strip()
        if stash_sha:
            diff_res = run_git(repo_root, ["diff", f"{info['head']}..{stash_sha}"])
            if diff_res.returncode == 0 and diff_res.stdout:
                apply_proc = subprocess.run(
                    ["git", "-C", str(wt_dir), "apply", "--3way"],
                    input=diff_res.stdout,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
                dirty_carried = apply_proc.returncode == 0

    linked_deps = []
    if args.link_node_modules and (repo_root / "node_modules").is_dir():
        if create_dir_link(repo_root / "node_modules", wt_dir / "node_modules"):
            linked_deps.append("node_modules")

    meta = {
        "schema": "akasha-worktree/v1",
        "status": "created",
        "slug": slug,
        "branch": branch_name,
        "base_branch": info["branch"],
        "base_commit": base_commit,
        "main_repo": str(repo_root),
        "worktree_path": str(wt_dir),
        "copied_envs": copied_envs,
        "dirty_carried": dirty_carried,
        "linked_deps": linked_deps,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


def load_worktree_meta(repo_root: Path, slug: str, custom_root: str = None):
    s = sanitize_slug(slug)
    wt_dir = default_worktree_base(repo_root, custom_root) / s
    meta_file = wt_dir / META_FILENAME
    if not meta_file.is_file():
        print(json.dumps({"status": "error", "reason": f"worktree_not_found: {wt_dir}"}, ensure_ascii=False))
        sys.exit(1)
    return json.loads(meta_file.read_text(encoding="utf-8")), wt_dir


def cmd_status(args):
    info = detect_repo_info(Path(args.repo).resolve())
    if not info.get("is_git"):
        print(json.dumps({"status": "not_a_git_repo"}, ensure_ascii=False))
        return
    repo_root = Path(info["repo_root"])
    wts = list_akasha_worktrees(repo_root, args.root)
    if args.slug:
        s = sanitize_slug(args.slug)
        wts = [w for w in wts if w.get("slug") == s]
    print(
        json.dumps(
            {
                "main_repo": str(repo_root),
                "main_branch": info.get("branch"),
                "main_dirty": info.get("dirty"),
                "worktrees": wts,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def compute_worktree_patch(wt_dir: Path, base_commit: str):
    """Returns full unified diff from base_commit to current worktree working state (including untracked files)."""
    # Temporarily intent-to-add untracked files (excluding META_FILENAME & linked deps) so git diff sees them,
    # then reset intent-to-add cleanly after generating patch.
    untracked_raw = run_git(wt_dir, ["ls-files", "--others", "--exclude-standard"]).stdout.splitlines()
    untracked = [f for f in untracked_raw if f and f != META_FILENAME and not f.startswith(".env")]
    if untracked:
        run_git(wt_dir, ["add", "-N", "--"] + untracked)
    try:
        stat = run_git(wt_dir, ["diff", "--stat", base_commit]).stdout.strip()
        patch = run_git(wt_dir, ["diff", "--binary", base_commit]).stdout
    finally:
        if untracked:
            run_git(wt_dir, ["reset", "--"] + untracked)
    return stat, patch, untracked


def cmd_diff(args):
    info = detect_repo_info(Path(args.repo).resolve())
    repo_root = Path(info["repo_root"])
    meta, wt_dir = load_worktree_meta(repo_root, args.slug, args.root)
    stat, patch, untracked = compute_worktree_patch(wt_dir, meta["base_commit"])
    out = {
        "slug": meta["slug"],
        "branch": meta["branch"],
        "worktree_path": str(wt_dir),
        "base_commit": meta["base_commit"],
        "untracked_new_files": untracked,
        "diff_stat": stat,
    }
    if args.full:
        out["patch"] = patch
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_land(args):
    info = detect_repo_info(Path(args.repo).resolve())
    repo_root = Path(info["repo_root"])
    meta, wt_dir = load_worktree_meta(repo_root, args.slug, args.root)
    mode = args.mode

    if mode == "keep":
        print(
            json.dumps(
                {
                    "status": "kept",
                    "branch": meta["branch"],
                    "worktree_path": str(wt_dir),
                    "hint": "Worktree and branch preserved for manual inspection or PR push.",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    if mode == "apply-patch":
        stat, patch, untracked = compute_worktree_patch(wt_dir, meta["base_commit"])
        if not patch.strip():
            print(json.dumps({"status": "noop", "reason": "no_changes_in_worktree"}, ensure_ascii=False))
            return
        chk = subprocess.run(
            ["git", "-C", str(repo_root), "apply", "--check"],
            input=patch,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if chk.returncode != 0:
            print(
                json.dumps(
                    {
                        "status": "conflict",
                        "mode": "apply-patch",
                        "stderr": chk.stderr.strip(),
                        "hint": "Main workspace conflicts with worktree patch; commit/stash main changes or keep worktree.",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            sys.exit(2)
        app = subprocess.run(
            ["git", "-C", str(repo_root), "apply"],
            input=patch,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if app.returncode != 0:
            print(json.dumps({"status": "error", "stderr": app.stderr.strip()}, ensure_ascii=False))
            sys.exit(1)
        print(
            json.dumps(
                {
                    "status": "landed",
                    "mode": "apply-patch",
                    "main_repo": str(repo_root),
                    "diff_stat": stat,
                    "untracked_applied": untracked,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    # For squash-merge / merge: ensure worktree changes are committed and main repo is clean
    wt_dirty = [
        ln for ln in run_git(wt_dir, ["status", "--short"]).stdout.splitlines()
        if ln.strip() and not ln.strip().endswith(META_FILENAME)
    ]
    if wt_dirty:
        if args.commit_message:
            # Stage all modified/new tracked & untracked source files except meta & .env
            untracked = [
                f for f in run_git(wt_dir, ["ls-files", "--others", "--exclude-standard"]).stdout.splitlines()
                if f and f != META_FILENAME and not f.startswith(".env")
            ]
            run_git(wt_dir, ["add", "-u"], check=True)
            if untracked:
                run_git(wt_dir, ["add", "--"] + untracked, check=True)
            c_res = run_git(wt_dir, ["commit", "-m", args.commit_message])
            if c_res.returncode != 0:
                print(json.dumps({"status": "error", "stage": "worktree_commit", "stderr": c_res.stderr.strip()}, ensure_ascii=False))
                sys.exit(1)
        else:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "reason": "worktree_has_uncommitted_changes",
                        "hint": "Commit changes inside worktree first, pass --commit-message, or use --mode apply-patch.",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            sys.exit(1)

    if info["dirty"]:
        print(
            json.dumps(
                {
                    "status": "error",
                    "reason": "main_workspace_dirty",
                    "hint": "Main workspace has uncommitted edits. Use --mode apply-patch or commit/stash main workspace first.",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        sys.exit(2)

    if mode == "squash-merge":
        m_res = run_git(repo_root, ["merge", "--squash", meta["branch"]])
        if m_res.returncode != 0:
            print(json.dumps({"status": "conflict", "mode": mode, "stderr": m_res.stderr.strip()}, ensure_ascii=False))
            sys.exit(2)
        committed = False
        if args.commit_message:
            cm = run_git(repo_root, ["commit", "-m", args.commit_message])
            committed = cm.returncode == 0
        print(
            json.dumps(
                {
                    "status": "landed",
                    "mode": "squash-merge",
                    "branch": meta["branch"],
                    "committed_on_main": committed,
                    "stdout": m_res.stdout.strip(),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    if mode == "merge":
        m_res = run_git(repo_root, ["merge", "--no-ff", meta["branch"], "-m", args.commit_message or f"Merge {meta['branch']}"])
        if m_res.returncode != 0:
            print(json.dumps({"status": "conflict", "mode": mode, "stderr": m_res.stderr.strip()}, ensure_ascii=False))
            sys.exit(2)
        print(
            json.dumps(
                {
                    "status": "landed",
                    "mode": "merge",
                    "branch": meta["branch"],
                    "stdout": m_res.stdout.strip(),
                },
                indent=2,
                ensure_ascii=False,
            )
        )


def cmd_cleanup(args):
    info = detect_repo_info(Path(args.repo).resolve())
    repo_root = Path(info["repo_root"])
    meta, wt_dir = load_worktree_meta(repo_root, args.slug, args.root)

    # 1. Safely unlink any linked dependency folders first (protects main repo node_modules!)
    for dep in meta.get("linked_deps", []):
        safe_unlink_link(wt_dir / dep)

    # 2. Remove meta file & copied envs so non-forced removal stays clean
    meta_file = wt_dir / META_FILENAME
    if meta_file.exists():
        meta_file.unlink()
    for env_name in meta.get("copied_envs", []):
        ep = wt_dir / env_name
        if ep.is_file():
            ep.unlink()

    rm_args = ["worktree", "remove"]
    if args.force:
        rm_args.append("--force")
    rm_args.append(str(wt_dir))
    rm_res = run_git(repo_root, rm_args)
    if rm_res.returncode != 0:
        print(json.dumps({"status": "error", "stderr": rm_res.stderr.strip()}, ensure_ascii=False))
        sys.exit(1)

    run_git(repo_root, ["worktree", "prune"])

    branch_deleted = False
    if args.delete_branch:
        del_flag = "-D" if args.force else "-d"
        b_res = run_git(repo_root, ["branch", del_flag, meta["branch"]])
        branch_deleted = b_res.returncode == 0

    print(
        json.dumps(
            {
                "status": "cleaned",
                "slug": meta["slug"],
                "removed_path": str(wt_dir),
                "branch_deleted": branch_deleted,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Akasha v9.2 Codex-Style Git Worktree Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe")
    p_probe.add_argument("--repo", default=".")
    p_probe.add_argument("--root", default=None)
    p_probe.set_defaults(func=cmd_probe)

    p_create = sub.add_parser("create")
    p_create.add_argument("--repo", default=".")
    p_create.add_argument("--slug", required=True)
    p_create.add_argument("--base", default="HEAD")
    p_create.add_argument("--root", default=None)
    p_create.add_argument("--copy-env", action="store_true", default=True)
    p_create.add_argument("--no-copy-env", dest="copy_env", action="store_false")
    p_create.add_argument("--include-dirty", action="store_true")
    p_create.add_argument("--link-node-modules", action="store_true")
    p_create.set_defaults(func=cmd_create)

    p_status = sub.add_parser("status")
    p_status.add_argument("--repo", default=".")
    p_status.add_argument("--slug", default=None)
    p_status.add_argument("--root", default=None)
    p_status.set_defaults(func=cmd_status)

    p_diff = sub.add_parser("diff")
    p_diff.add_argument("--repo", default=".")
    p_diff.add_argument("--slug", required=True)
    p_diff.add_argument("--root", default=None)
    p_diff.add_argument("--full", action="store_true")
    p_diff.set_defaults(func=cmd_diff)

    p_land = sub.add_parser("land")
    p_land.add_argument("--repo", default=".")
    p_land.add_argument("--slug", required=True)
    p_land.add_argument("--mode", choices=["apply-patch", "squash-merge", "merge", "keep"], required=True)
    p_land.add_argument("--commit-message", default=None)
    p_land.add_argument("--root", default=None)
    p_land.set_defaults(func=cmd_land)

    p_clean = sub.add_parser("cleanup")
    p_clean.add_argument("--repo", default=".")
    p_clean.add_argument("--slug", required=True)
    p_clean.add_argument("--delete-branch", action="store_true")
    p_clean.add_argument("--force", action="store_true")
    p_clean.add_argument("--root", default=None)
    p_clean.set_defaults(func=cmd_cleanup)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
