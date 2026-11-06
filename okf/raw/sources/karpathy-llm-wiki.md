# Source capture: Karpathy LLM Wiki (gist summary)

- Origin: Andrej Karpathy, “LLM Wiki” gist
- URL: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Captured: 2026-11-06
- Note: Paraphrased/abridged for local immutable reference; consult the gist for the canonical text.

---

## Core idea

Most LLM+document workflows are RAG-like: retrieve chunks at query time and regenerate answers from scratch. There is no accumulation.

An LLM Wiki instead has the model **incrementally build and maintain a persistent wiki** of interlinked markdown between the user and raw sources. On ingest, the model integrates knowledge into entity/concept pages, flags contradictions, and updates synthesis. Knowledge is compiled once and kept current.

## Architecture

1. **Raw sources** — immutable curated documents.
2. **Wiki** — LLM-owned markdown (summaries, entities, concepts, comparisons).
3. **Schema** — agent instruction file (`AGENTS.md` / `CLAUDE.md`) defining structure and workflows.

## Operations

- **Ingest** — process a source into summary + cross-page updates + index + log.
- **Query** — answer from the wiki; file valuable answers back into the wiki.
- **Lint** — health-check contradictions, orphans, missing concepts, stale claims.

## Special files

- `index.md` — content catalog (category → page + one-line summary).
- `log.md` — append-only chronological record of operations.

Works well at moderate scale (~100 sources, hundreds of pages) with agentic navigation of the index rather than embeddings.
