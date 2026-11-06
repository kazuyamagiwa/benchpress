---
name: okf-lint
description: Health-check the OKF wiki with the CLI linter and fix structural issues.
---

# OKF Lint

1. From repo root: `python3 okf/okf.py lint`
2. Fix frontmatter, dangling links, and index drift.
3. Skim for contradictions / stale claims the linter cannot see.
4. Re-run lint until clean (orphans may remain if intentionally stubbed — note them).
5. Append a `lint` entry to `okf/wiki/log.md`.
