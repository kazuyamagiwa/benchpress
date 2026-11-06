---
type: Overview
title: OKF Overview
description: Hub page for this experimental Open Knowledge Framework bundle.
tags: [okf, llm-wiki, benchpress]
sources:
  - raw/sources/karpathy-llm-wiki.md
  - raw/sources/okf-spec-overview.md
  - raw/sources/benchpress-readme.md
updated: 2026-11-06T13:00:00+09:00
status: draft
---

# OKF Overview

This bundle is a **lightweight experimental Open Knowledge Framework** living inside the Benchpress repository. It applies Karpathy’s LLM Wiki idea — a compounding, agent-maintained markdown wiki — using Open Knowledge Format conventions (`type`-tagged frontmatter, reserved `index.md` / `log.md`).

The goal is not a full knowledge product. It is a small, stdlib-only scaffold you can extend: drop sources under `raw/sources/`, ask an agent to ingest them, query the wiki, and periodically lint.

## Key Takeaways

- Raw sources are immutable; the wiki is the compiled layer.
- Agents follow `okf/AGENTS.md` for ingest / query / lint.
- Mechanical checks live in `python okf/okf.py lint`.
- Seed content covers [Benchpress](entities/benchpress.md), the [LLM Wiki](concepts/llm-wiki.md) pattern, and [OKF](concepts/open-knowledge-format.md).

## Map

- Concepts: [LLM Wiki](concepts/llm-wiki.md), [Open Knowledge Format](concepts/open-knowledge-format.md), [Compounding knowledge](concepts/compounding-knowledge.md), [Structure learning](concepts/structure-learning.md)
- Entities: [Benchpress](entities/benchpress.md)
- Source summaries: [Benchpress README](sources/benchpress-readme.md), [Karpathy LLM Wiki](sources/karpathy-llm-wiki.md), [OKF spec overview](sources/okf-spec-overview.md)

## Sources

- `okf/raw/sources/karpathy-llm-wiki.md`
- `okf/raw/sources/okf-spec-overview.md`
- `okf/raw/sources/benchpress-readme.md`
