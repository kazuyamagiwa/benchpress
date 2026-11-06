---
type: Concept
title: Compounding knowledge
description: Knowledge that gets richer with each ingest and filed query instead of being rediscovered from scratch.
tags: [llm-wiki, knowledge-management]
sources:
  - raw/sources/karpathy-llm-wiki.md
updated: 2026-11-06T13:00:00+09:00
status: draft
---

# Compounding knowledge

In RAG-only workflows, every question restarts from raw chunks. In an [LLM Wiki](llm-wiki.md), each ingest updates entity and concept pages, and strong answers are filed back into the wiki. Cross-references, contradiction notes, and synthesis therefore **accumulate**.

For research codebases like [Benchpress](../entities/benchpress.md), compounding knowledge means algorithm notes, evaluation caveats, and config patterns can live as linked pages that stay current as modules evolve — without requiring a separate vector store for day-to-day agent navigation.

## Key Takeaways

- File reusable answers; chat transcripts evaporate.
- Lint periodically so the graph does not rot.
- Index-first retrieval keeps context small as the corpus grows.

## Sources

- `okf/raw/sources/karpathy-llm-wiki.md`
