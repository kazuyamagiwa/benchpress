# OKF Agent Schema

Instructions for LLM agents maintaining this Open Knowledge Framework bundle.
Inspired by [Karpathy’s LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and aligned with [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) markdown+YAML conventions.

## Layers

| Layer | Path | Who writes | Rules |
|---|---|---|---|
| Schema | `okf/AGENTS.md` | Human + agent (co-evolve) | This file. Conventions and workflows. |
| Raw sources | `okf/raw/sources/` | Human | **Immutable after capture.** Agents read only. |
| Wiki | `okf/wiki/` | Agent | Agents create/update pages, links, index, log. |
| Output | `okf/output/` | Agent | Query reports and scratch artifacts. Optional to gitignore later. |

Reserved filenames (never use as concept pages): `index.md`, `log.md`.

## Frontmatter (OKF-compatible)

Every concept page under `okf/wiki/` **except** reserved files MUST start with YAML frontmatter. Required:

```yaml
---
type: Concept          # REQUIRED (OKF). Free-form string; see suggested types below
title: Display Title
description: One-line summary for index and search snippets
tags: [tag-one, tag-two]
sources:               # Provenance (OKF-style); paths relative to okf/
  - raw/sources/example.md
updated: 2026-11-06T00:00:00+09:00
---
```

Suggested `type` values for this experiment (not a registry — unknown types are fine):

- `Source Summary` — wiki page summarizing one raw source
- `Concept` — abstract idea / pattern
- `Entity` — named project, person, system
- `Comparison` — filed query answer comparing things
- `Playbook` — how-to / workflow
- `Overview` — hub / synthesis page

Recommended optional fields: `resource` (canonical URI), `verified` (`human` / `machine` / omit), `status` (`draft` / `stable`).

## Page body conventions

1. `# Title` matching `title:` (or clearly derived from it).
2. Short prose (what / why / how). Prefer compounding synthesis over dumping quotes.
3. `## Key Takeaways` with concrete bullets when useful.
4. Cross-links:
   - Prefer **standard markdown links** to other wiki pages (OKF-portable), e.g. `[Benchpress](../entities/benchpress.md)`.
   - `[[wiki-links]]` are also accepted by the linter (Karpathy/Obsidian style); resolve them to filenames without `.md`.
5. End with `## Sources` citing raw paths and/or external URLs.

Quality over quantity for links: typically 2–5 meaningful outgoing links. Avoid linking every page to a generic hub.

## Operations

### Ingest

When the user drops a file into `okf/raw/sources/` (or asks to ingest an existing one):

1. Read `wiki/log.md` and skip already-processed sources.
2. Read the raw file. Do not modify it.
3. Write or update a `wiki/sources/<slug>.md` summary.
4. Update or create related `wiki/concepts/` and `wiki/entities/` pages; flag contradictions explicitly.
5. Refresh `wiki/index.md` (or run `python3 okf/okf.py index --write`).
6. Append a log entry:

```markdown
## [YYYY-MM-DD] ingest | <source filename>
- pages: …
- notes: …
```

Prefer one source at a time when the user wants to review; batch only when asked.

### Query

1. Read `wiki/index.md` first.
2. Open only the pages that look relevant; follow links as needed.
3. Answer with citations to wiki paths (and raw sources when claims depend on them).
4. If the answer is reusable (comparison, synthesis, decision), **file it back** under `wiki/concepts/` or `wiki/comparisons/` and log:

```markdown
## [YYYY-MM-DD] query | <short question>
- filed: wiki/…
```

Optionally save a full report under `okf/output/`.

### Lint

1. Run `python3 okf/okf.py lint` from the repo root.
2. Fix frontmatter, dangling links, orphans (if intentional, note why), and index drift.
3. Skim for contradictions / stale claims the mechanical linter cannot see.
4. Append a `## [YYYY-MM-DD] lint | …` log entry.

## Focus areas (this repo)

- Structure learning / causal discovery benchmarking (Benchpress)
- How OKF + LLM Wiki apply to research codebases
- Algorithm modules, evaluation metrics, and workflow configuration

## Tooling

```bash
python3 okf/okf.py status
python3 okf/okf.py lint
python3 okf/okf.py search "<terms>"
python3 okf/okf.py index --write
```

Stdlib only. See `okf/README.md`.
