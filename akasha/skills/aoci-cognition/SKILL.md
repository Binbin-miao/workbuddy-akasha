---
name: aoci-cognition
description: AOCI (aoci-spec/aoci-code v0.2.0-rc2) Volume-First 机器可读全域认知索引协议：由专职测绘 Agent（艾尔海森）结合确定性预扫脚本生成 aoci.txt / aoci.meta.txt / aoci.code.txt，供其他专家直读零盲扫、省 60-80% Token。
---

# AOCI Volume-First Machine-Cognition Protocol (v9.0)

## 1. CORE ARCHITECTURE: DEDICATED INDEXER + MACHINE-FIRST VOLUMES
- **Dedicated Owner**: ONLY `aoci-codebase-cartographer` (**艾尔海森**) builds and refreshes the AOCI CognitionSet. Other agents (`纳西妲`, `可莉`, `心海`, `希格雯`) are **READ-ONLY consumers** of the AOCI volumes and NEVER re-traverse the repository from scratch.
- **Standard Plain-Text Volume Layout (`aoci-spec/aoci-code` v0.2.0-rc2 `cognition-volumes/v1`)**:
  - Storage location:
    * `own_repo` with `.aoci/config.json` (or user opted-in): repo root `aoci.txt`, `aoci.meta.txt`, `aoci.code.txt` (+ optional `aoci.database.txt`).
    * `external_pr` or zero-daemon mode (default): `.scratch/aoci/aoci.txt`, `.scratch/aoci/aoci.meta.txt`, `.scratch/aoci/aoci.code.txt`, `.scratch/aoci/baseline.json` (auto-hidden via `.git/info/exclude`).
  - **Volume 1 — Root Manifest (`aoci.txt`)**:
    ```text
    #AOCI-ROOT-MANIFEST: 1
    #Format-Version: cognition-volumes/v1
    #Locale: zh-CN
    #Project: <project-name>
    #Global-Invariants: <1-line global system invariants>
    #Volume: id=meta kind=meta path=aoci.meta.txt format=meta-v1 depends=- state=enabled
    #Volume: id=code kind=code path=aoci.code.txt format=object-fras-v2 depends=meta state=enabled
    ```
  - **Volume 2 — Meta & Tag Dictionary (`aoci.meta.txt`, `meta-v1`)**:
    Defines 4-char tag `[Layer][Domain][Importance:9-1][Size:L/M/S/T]` + `#S-Admission` rules so every consuming agent decodes the index in 0 ambiguity.
  - **Volume 3 — Code Index (`aoci.code.txt`, `object-fras-v2`)**:
    Starts with `#AOCI-CODE-VOLUME: 1`, followed strictly by 1 machine-dense line per managed file:
    ```text
    <relative_path>[<Layer><Domain><Imp><Size>]: F:<what it owns> | R:<coupled files/symbols to read/update together> | A:<public API/commands/schemas> | S:<non-obvious invariant ONLY — locks, ordering, parity, concurrency, traps>
    ```

## 2. ZERO-WASTE DETERMINISTIC PRESCAN (`scripts/aoci_prescan.py`)
1. Run `python <skill_dir>/scripts/aoci_prescan.py --repo "<workspace>"` in **1 single tool call**.
2. Inspect `added`, `modified`, `deleted` arrays (computed via SHA-256 against `.scratch/aoci/baseline.json`).
   - If `added == []` AND `modified == []` AND `deleted == []` AND `aoci.code.txt` exists -> **INSTANT CACHE HIT (0 files read, exit in 1 turn!)**.
3. Read ONLY the `added` and `modified` source files in batches and author genuine semantic `F|R|A|S` lines (NEVER fabricate business meaning from filenames or AST alone).
4. After updating `aoci.code.txt`, commit the baseline: `python <skill_dir>/scripts/aoci_prescan.py --repo "<workspace>" --commit-baseline`.

## 3. CONSUMER READING CONTRACT (FOR ALL OTHER AGENTS)
- Every agent starts by reading `aoci.code.txt` (1 read call) to obtain the complete dependency graph (`R`), public contracts (`A`), and hidden traps (`S`).
- Open raw source files ONLY for the exact target paths + their `R` neighbors. NEVER run repository-wide `find`/`grep` sweeps when `aoci.code.txt` is fresh.
