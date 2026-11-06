#!/usr/bin/env python3
"""Lightweight OKF CLI — lint, search, index, status.

Stdlib only. Run from repo root or any cwd:

    python3 okf/okf.py status
    python3 okf/okf.py lint
    python3 okf/okf.py search "causal"
    python3 okf/okf.py index --write
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

RESERVED = frozenset({"index.md", "log.md"})
WIKI_LINK_RE = re.compile(
    r"(?<!`)\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\](?!`)"
)
MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)


def bundle_root() -> Path:
    return Path(__file__).resolve().parent


def wiki_dir() -> Path:
    return bundle_root() / "wiki"


def raw_dir() -> Path:
    return bundle_root() / "raw"


@dataclass
class Page:
    path: Path  # absolute
    rel: str  # path relative to wiki/, posix
    frontmatter: dict[str, object] = field(default_factory=dict)
    body: str = ""
    outgoing: set[str] = field(default_factory=set)  # wiki-relative targets .md
    issues: list[str] = field(default_factory=list)

    @property
    def concept_id(self) -> str:
        return self.rel[:-3] if self.rel.endswith(".md") else self.rel

    @property
    def is_reserved(self) -> bool:
        return Path(self.rel).name in RESERVED


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Minimal YAML subset: key: value, key: [a, b], and simple nested lists."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw_fm, body = m.group(1), m.group(2)
    data: dict[str, object] = {}
    lines = raw_fm.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest in ("", "|", ">"):
            # block / list follows
            items: list[str] = []
            i += 1
            while i < len(lines) and (
                lines[i].startswith("  - ")
                or lines[i].startswith("\t- ")
                or (lines[i].startswith("  ") and not lines[i].strip().startswith("#"))
            ):
                item = lines[i].strip()
                if item.startswith("- "):
                    items.append(_unquote(item[2:].strip()))
                i += 1
            data[key] = items
            continue
        if rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            data[key] = (
                [_unquote(x.strip()) for x in inner.split(",") if x.strip()]
                if inner
                else []
            )
        else:
            data[key] = _unquote(rest)
        i += 1
    return data, body


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def walk_markdown(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def load_pages(wiki: Path) -> list[Page]:
    pages: list[Page] = []
    for path in walk_markdown(wiki):
        rel = path.relative_to(wiki).as_posix()
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        page = Page(path=path, rel=rel, frontmatter=fm, body=body)
        if not page.is_reserved:
            if not fm:
                page.issues.append("missing frontmatter block")
            elif not str(fm.get("type") or "").strip():
                page.issues.append("missing required frontmatter key: type")
        page.outgoing = _extract_links(page, wiki)
        pages.append(page)
    return pages


def _extract_links(page: Page, wiki: Path) -> set[str]:
    targets: set[str] = set()
    # [[wiki-links]]
    for name in WIKI_LINK_RE.findall(page.body):
        name = name.strip()
        resolved = _resolve_wiki_link(name, wiki)
        if resolved:
            targets.add(resolved)
        else:
            # keep dangling marker as synthetic path for lint
            targets.add(f"[[{name}]]")
    # markdown links to .md within wiki
    for _, href in MD_LINK_RE.findall(page.body):
        href = href.strip()
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        href = href.split("#", 1)[0]
        if not href.endswith(".md"):
            continue
        try:
            dest = (page.path.parent / href).resolve()
            if wiki.resolve() in dest.parents or dest.parent == wiki.resolve():
                targets.add(dest.relative_to(wiki.resolve()).as_posix())
        except (OSError, ValueError):
            continue
    return targets


def _resolve_wiki_link(name: str, wiki: Path) -> str | None:
    """Match [[Name]] to a wiki file by stem (basename without .md)."""
    stem = name.strip()
    matches = [p for p in walk_markdown(wiki) if p.stem == stem and p.name not in RESERVED]
    if len(matches) == 1:
        return matches[0].relative_to(wiki).as_posix()
    # also allow full relative path without .md
    candidate = wiki / f"{stem}.md"
    if candidate.is_file():
        return candidate.relative_to(wiki).as_posix()
    return None


def cmd_status(_: argparse.Namespace) -> int:
    wiki = wiki_dir()
    pages = load_pages(wiki)
    concepts = [p for p in pages if not p.is_reserved]
    raw_files = [p for p in walk_markdown(raw_dir()) if p.name != "README.md"]
    print("OKF bundle:", bundle_root())
    print(f"raw sources: {len(raw_files)}")
    print(f"wiki pages:  {len(concepts)} concepts + reserved index/log")
    by_type: dict[str, int] = defaultdict(int)
    for p in concepts:
        by_type[str(p.frontmatter.get("type") or "(missing)")] += 1
    if by_type:
        print("by type:")
        for t, n in sorted(by_type.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {t}: {n}")
    return 0


def cmd_lint(_: argparse.Namespace) -> int:
    wiki = wiki_dir()
    pages = load_pages(wiki)
    concepts = [p for p in pages if not p.is_reserved]
    by_rel = {p.rel: p for p in concepts}

    frontmatter_issues: list[str] = []
    dangling: list[str] = []
    orphans: list[str] = []
    incoming: dict[str, set[str]] = defaultdict(set)

    for page in concepts:
        for issue in page.issues:
            frontmatter_issues.append(f"{page.rel}: {issue}")
        for target in page.outgoing:
            if target.startswith("[[") and target.endswith("]]"):
                dangling.append(f"{page.rel} -> {target}")
                continue
            if target in RESERVED or Path(target).name in RESERVED:
                continue
            if target not in by_rel:
                dangling.append(f"{page.rel} -> {target}")
            else:
                incoming[target].add(page.rel)

    for page in concepts:
        if not page.outgoing and not incoming.get(page.rel):
            orphans.append(page.rel)

    index_path = wiki / "index.md"
    missing_from_index: list[str] = []
    extra_in_index: list[str] = []
    if index_path.is_file():
        index_text = index_path.read_text(encoding="utf-8")
        mentioned = set()
        for rel in by_rel:
            # match relative path or basename stem in index
            stem = Path(rel).stem
            if rel in index_text or stem in index_text or Path(rel).name in index_text:
                mentioned.add(rel)
            else:
                missing_from_index.append(rel)
        # extras: links in index that don't exist
        _, index_body = parse_frontmatter(index_text)
        for _, href in MD_LINK_RE.findall(index_body):
            href = href.strip().split("#", 1)[0]
            if not href.endswith(".md"):
                continue
            try:
                dest = (index_path.parent / href).resolve()
                rel = dest.relative_to(wiki.resolve()).as_posix()
            except (OSError, ValueError):
                continue
            if Path(rel).name in RESERVED:
                continue
            if rel not in by_rel:
                extra_in_index.append(rel)
    else:
        missing_from_index = list(by_rel)

    def section(title: str, items: Iterable[str], empty: str) -> None:
        items = list(items)
        print(f"\n{title}")
        if not items:
            print(f"  (none — {empty})")
            return
        for item in items:
            print(f"  - {item}")

    print("=== OKF Lint ===")
    print(f"concept pages: {len(concepts)}")
    section("FRONTMATTER ISSUES", frontmatter_issues, "all pages valid")
    section("DANGLING LINKS", dangling, "all links resolve")
    section("ORPHAN PAGES (no in/out links)", orphans, "all pages connected")
    section("MISSING FROM index.md", missing_from_index, "index is complete")
    section("EXTRA IN index.md", extra_in_index, "index is clean")

    problems = (
        len(frontmatter_issues)
        + len(dangling)
        + len(missing_from_index)
        + len(extra_in_index)
    )
    print("\n=== Done ===")
    return 1 if problems else 0


def cmd_search(args: argparse.Namespace) -> int:
    terms = [t.lower() for t in args.terms]
    if not terms:
        print("Provide one or more search terms.", file=sys.stderr)
        return 2
    wiki = wiki_dir()
    hits: list[tuple[int, str, str]] = []
    for path in walk_markdown(wiki):
        rel = path.relative_to(wiki).as_posix()
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        score = sum(lower.count(t) for t in terms)
        if score == 0:
            continue
        fm, body = parse_frontmatter(text)
        title = str(fm.get("title") or path.stem)
        desc = str(fm.get("description") or "")
        snippet = desc
        if not snippet:
            for line in body.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    snippet = line[:140]
                    break
        hits.append((score, rel, f"{title} — {snippet}" if snippet else title))
    hits.sort(key=lambda x: (-x[0], x[1]))
    if not hits:
        print("No matches.")
        return 0
    print(f"=== Search: {' '.join(args.terms)} ({len(hits)} hits) ===")
    for score, rel, summary in hits[:50]:
        print(f"  [{score}] {rel}")
        print(f"       {summary}")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    wiki = wiki_dir()
    pages = [p for p in load_pages(wiki) if not p.is_reserved]
    groups: dict[str, list[Page]] = defaultdict(list)
    for page in pages:
        top = page.rel.split("/", 1)[0] if "/" in page.rel else "(root)"
        groups[top].append(page)

    lines = [
        "---",
        'okf_version: "0.2"',
        "type: Index",
        "title: OKF Wiki Index",
        "description: Content catalog for progressive disclosure.",
        f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "---",
        "",
        "# OKF Wiki Index",
        "",
        "Catalog of concept pages. Agents: read this first, then open only relevant pages.",
        "",
    ]
    for group in sorted(groups):
        lines.append(f"## {group}")
        lines.append("")
        for page in sorted(groups[group], key=lambda p: p.rel):
            title = str(page.frontmatter.get("title") or Path(page.rel).stem)
            desc = str(page.frontmatter.get("description") or "").strip()
            href = page.rel
            if desc:
                lines.append(f"- [{title}]({href}): {desc}")
            else:
                lines.append(f"- [{title}]({href})")
        lines.append("")

    text = "\n".join(lines).rstrip() + "\n"
    if args.write:
        (wiki / "index.md").write_text(text, encoding="utf-8")
        print(f"Wrote {wiki / 'index.md'} ({len(pages)} pages)")
    else:
        sys.stdout.write(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="okf",
        description="Lightweight experimental Open Knowledge Framework CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Summarize bundle contents")
    p_status.set_defaults(func=cmd_status)

    p_lint = sub.add_parser("lint", help="Validate frontmatter, links, and index")
    p_lint.set_defaults(func=cmd_lint)

    p_search = sub.add_parser("search", help="Keyword search over wiki markdown")
    p_search.add_argument("terms", nargs="+", help="Search terms (AND scoring by count)")
    p_search.set_defaults(func=cmd_search)

    p_index = sub.add_parser("index", help="Generate wiki/index.md from frontmatter")
    p_index.add_argument(
        "--write",
        action="store_true",
        help="Write wiki/index.md (default: print to stdout)",
    )
    p_index.set_defaults(func=cmd_index)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
