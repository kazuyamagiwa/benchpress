---
name: okf-query
description: Answer questions using the OKF wiki via index-first agentic retrieval; file reusable answers back.
---

# OKF Query

Follow `okf/AGENTS.md`.

1. Read `okf/wiki/index.md`.
2. Optionally run `python3 okf/okf.py search "<keywords>"` to shortlist pages.
3. Open only relevant wiki pages; follow links as needed. Prefer wiki synthesis over re-reading all raw sources.
4. Answer with citations to wiki paths (and raw sources when necessary).
5. If the answer is reusable, file it under `okf/wiki/concepts/` or similar with frontmatter, update the index, and append a `query` log entry.
6. Optionally write a full report to `okf/output/`.
