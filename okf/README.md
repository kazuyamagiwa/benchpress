# Experimental Open Knowledge Framework (OKF)

A **very lightweight** experimental knowledge framework for this repository.

It combines:

1. **Andrej Karpathy’s [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern** — an LLM incrementally maintains a persistent, interlinked markdown wiki instead of re-deriving answers from raw files on every query.
2. **Google’s [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) conventions** — plain markdown concepts with YAML frontmatter (`type:` required), plus reserved `index.md` / `log.md`.

No vector DB, no embeddings service, no package install beyond the Python standard library.

## Layout

```
okf/
├── AGENTS.md          # Schema: how agents ingest, query, and lint
├── okf.py             # Stdlib CLI: lint | search | index | status
├── raw/sources/       # Immutable source captures (humans add; agents read)
├── wiki/              # Agent-maintained compounding knowledge
│   ├── index.md       # Content catalog (read this first when querying)
│   ├── log.md         # Append-only timeline of operations
│   ├── concepts/      # Idea / pattern pages
│   ├── entities/      # Named systems / people / projects
│   └── sources/       # Per-source summary pages
├── skills/            # Optional Cursor skill prompts
├── output/            # Generated query reports (local scratch)
└── tests/             # Smoke tests for the CLI
```

## Quick start

```bash
# Health-check the seed wiki
python3 okf/okf.py status
python3 okf/okf.py lint

# Keyword search across wiki pages
python3 okf/okf.py search "structure learning"

# Rebuild wiki/index.md from frontmatter
python3 okf/okf.py index --write
```

Then point an agent at `okf/AGENTS.md` and say:

- **Ingest** — “Process `okf/raw/sources/<file>` into the OKF wiki”
- **Query** — “Using the OKF wiki, answer: … and file the answer back if useful”
- **Lint** — “Run `python3 okf/okf.py lint` and fix what it reports”

## Core idea

Raw sources stay immutable. The wiki is the compiled, compounding layer: entity pages, concept pages, cross-links, contradictions flagged once, synthesis kept current. `index.md` is the navigation map; `log.md` is the audit trail.

## Status

Experimental. The seed wiki covers Benchpress plus the OKF/LLM-Wiki ideas themselves so the framework is immediately usable and self-documenting. Conventions may change.
