#!/usr/bin/env python3
"""Smoke tests for the experimental OKF CLI (stdlib unittest)."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OKF = ROOT / "okf" / "okf.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(OKF), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class OkfCliTests(unittest.TestCase):
    def test_status(self) -> None:
        proc = run("status")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("wiki pages", proc.stdout)

    def test_lint_clean(self) -> None:
        proc = run("lint")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_search_finds_benchpress(self) -> None:
        proc = run("search", "benchpress")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("entities/benchpress.md", proc.stdout)

    def test_index_stdout(self) -> None:
        proc = run("index")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("okf_version", proc.stdout)
        self.assertIn("Benchpress", proc.stdout)


if __name__ == "__main__":
    unittest.main()
