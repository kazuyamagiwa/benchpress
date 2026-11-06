---
type: Concept
title: Structure learning
description: Inferring graph structure (often causal or probabilistic) from data; the core task Benchpress benchmarks.
tags: [causal-discovery, graphical-models, benchpress]
sources:
  - raw/sources/benchpress-readme.md
updated: 2026-11-06T13:00:00+09:00
status: draft
---

# Structure learning

Structure learning (sometimes called causal discovery when the target is a causal graph) is the problem of estimating the edges of a graphical model from data. Algorithms differ in assumptions, score vs constraint paradigms, language/runtime, and scalability.

[Benchpress](../entities/benchpress.md) packages many such algorithms in a Snakemake workflow so they can be compared under shared data, graph, and evaluation settings. This OKF wiki can accumulate notes on algorithms, metrics, and pitfalls as modules are added.

## Key Takeaways

- Same task, many implementations — fair comparison needs shared scaffolding.
- Benchpress targets benchmarks, algorithm development, and applied data analysis.
- Domain knowledge here should cite modules and docs as sources when ingested.

## Sources

- `okf/raw/sources/benchpress-readme.md`
- Docs: https://benchpressdocs.readthedocs.io
