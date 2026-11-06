---
type: Concept
title: LLM Wiki
description: Pattern where an LLM maintains a persistent interlinked markdown wiki between users and raw sources.
tags: [llm-wiki, knowledge-management, agents]
sources:
  - raw/sources/karpathy-llm-wiki.md
resource: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
updated: 2026-11-06T13:00:00+09:00
status: stable
---

# LLM Wiki

Proposed by Andrej Karpathy, an LLM Wiki treats the model as a librarian rather than a one-shot retriever. Instead of only chunking documents for RAG at query time, the agent **compiles** knowledge into a growing set of markdown pages and keeps them consistent as new sources arrive.

The architecture has three layers: immutable raw sources, an agent-owned wiki, and a schema document that encodes conventions. Primary operations are ingest, query (with filing answers back), and lint. Navigation at moderate scale uses `index.md` plus link following — [compounding knowledge](compounding-knowledge.md) without a mandatory vector index.

This experimental OKF bundle implements that pattern with [Open Knowledge Format](open-knowledge-format.md) frontmatter so pages stay portable.

## Key Takeaways

- Persistence beats re-derivation: synthesis and contradiction flags survive across sessions.
- Humans curate sources and questions; agents do bookkeeping.
- `index.md` + `log.md` are the two special navigation/audit files.
- Good query answers should become wiki pages when reusable.

## Sources

- [Karpathy LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- Local capture: `okf/raw/sources/karpathy-llm-wiki.md`
