---
type: Source Summary
title: Karpathy LLM Wiki (source summary)
description: Summary of the LLM Wiki gist — persistent agent-maintained wikis vs query-time RAG.
tags: [llm-wiki, source]
sources:
  - raw/sources/karpathy-llm-wiki.md
resource: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
updated: 2026-11-06T13:00:00+09:00
status: stable
---

# Karpathy LLM Wiki (source summary)

Abridged local capture of Andrej Karpathy’s LLM Wiki idea: build a compounding markdown wiki rather than rediscovering knowledge with RAG on every question. Defines raw / wiki / schema layers and ingest / query / lint operations, plus `index.md` and `log.md`.

Concept page: [LLM Wiki](../concepts/llm-wiki.md). Related: [compounding knowledge](../concepts/compounding-knowledge.md).

## Key Takeaways

- Wiki is a persistent compiled artifact.
- Schema file disciplines the agent.
- File query answers back into the wiki.
- Moderate scale can rely on index navigation.

## Sources

- Raw: [`okf/raw/sources/karpathy-llm-wiki.md`](../../raw/sources/karpathy-llm-wiki.md)
- Canonical: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
