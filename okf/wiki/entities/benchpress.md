---
type: Entity
title: Benchpress
description: Snakemake platform for benchmarking structure learning / causal discovery algorithms.
tags: [benchpress, snakemake, causal-discovery]
sources:
  - raw/sources/benchpress-readme.md
resource: https://benchpressdocs.readthedocs.io
updated: 2026-11-06T13:00:00+09:00
status: stable
---

# Benchpress

Benchpress is a versatile Snakemake-based platform for [structure learning](../concepts/structure-learning.md) in causal and probabilistic graphical models. It runs algorithms (possibly in different languages) under comparable configurations and scales from laptops to clusters without rewriting the workflow.

Primary uses: algorithm benchmarks, in-development algorithm comparison, and estimating graphs from user datasets. Cited in the Journal of Statistical Software (2025). This experimental [OKF](../concepts/open-knowledge-format.md) / [LLM Wiki](../concepts/llm-wiki.md) bundle sits beside the workflow code so agent-maintained notes can compound next to the software.

## Key Takeaways

- Orchestration: Snakemake (≥7.30.1 per project badge).
- Docs: https://benchpressdocs.readthedocs.io
- License: GPL-2.0
- JSS paper DOI: https://doi.org/10.18637/jss.v114.i12

## Sources

- `okf/raw/sources/benchpress-readme.md`
- Repository `README.md`
