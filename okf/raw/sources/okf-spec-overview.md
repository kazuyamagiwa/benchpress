# Source capture: Open Knowledge Format (OKF) overview

- Origin: Google Cloud Platform `open-knowledge-format` SPEC.md (v0.2)
- URL: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
- Captured: 2026-11-06
- Note: Abridged local reference for this experimental framework.

---

OKF is a vendor-neutral format for knowledge as a **directory of UTF-8 markdown files with YAML frontmatter**.

Key points:

- A **bundle** is a directory tree of concept documents.
- Reserved filenames: `index.md` (directory listing), `log.md` (update history).
- Every concept has frontmatter; the only always-required key is non-empty `type:`.
- Recommended fields: `title`, `description`, `resource`, `tags`.
- v0.2 emphasizes provenance, trust, lifecycle, and attested computation metadata while staying minimally opinionated.
- Links between concepts are standard markdown links.
- Bundles are meant to be git-friendly, human-readable, and agent-writable.
