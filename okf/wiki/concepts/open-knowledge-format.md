---
type: Concept
title: Open Knowledge Format
description: Vendor-neutral markdown+YAML format for portable, agent-friendly knowledge bundles.
tags: [okf, format, interoperability]
sources:
  - raw/sources/okf-spec-overview.md
resource: https://github.com/GoogleCloudPlatform/open-knowledge-format
updated: 2026-11-06T13:00:00+09:00
status: stable
---

# Open Knowledge Format

Google’s Open Knowledge Format (OKF) standardizes knowledge as a directory of markdown files with YAML frontmatter. The only always-required field is a non-empty `type`. Reserved names `index.md` and `log.md` provide progressive disclosure and update history.

OKF is intentionally minimal: no central type registry, no required runtime. It is meant for humans and agents to author, git to version, and diverse consumers to read. v0.2 adds richer optional metadata for provenance, trust, lifecycle, and attested computation.

This repository’s experimental framework uses OKF-shaped pages as the storage layer for an [LLM Wiki](llm-wiki.md) workflow — format for portability, wiki pattern for compounding maintenance.

## Key Takeaways

- Bundle = directory tree of concept markdown files.
- `type` is required; `title` / `description` / `resource` / `tags` are recommended.
- Prefer standard markdown links for cross-concept relationships (portable).
- Compatible with Obsidian-style `[[wiki-links]]` in this experiment; the linter accepts both.

## Sources

- [OKF SPEC.md](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
- Local capture: `okf/raw/sources/okf-spec-overview.md`
