---
name: okf-ingest
description: Ingest new okf/raw/sources files into the OKF wiki (Karpathy LLM Wiki workflow).
---

# OKF Ingest

Follow `okf/AGENTS.md`.

1. Read `okf/wiki/log.md` and list unprocessed files under `okf/raw/sources/` (skip `README.md`).
2. Process a small batch (prefer 1 source if the user wants review; otherwise ≤5).
3. Never modify raw files.
4. Create/update `okf/wiki/sources/`, then related `concepts/` and `entities/` pages with OKF frontmatter (`type` required).
5. Use standard markdown links between wiki pages; keep 2–5 strong outgoing links.
6. Run `python3 okf/okf.py index --write` and append a log entry.
7. Run `python3 okf/okf.py lint` and fix issues you introduced.
