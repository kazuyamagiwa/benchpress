#!/usr/bin/env python
"""Snakemake wrapper for the causal-automata causal discovery engine."""

import argparse

import numpy as np
import pandas as pd
from causal_automata import run_discovery


def main():
    parser = argparse.ArgumentParser(
        description="Run causal-automata structure discovery on CSV data."
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Path to the input CSV dataset.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the estimated adjacency matrix CSV.",
    )
    args = parser.parse_args()

    print(f"[causal-automata] Loading input data from: {args.data}")
    data = pd.read_csv(args.data)
    print(f"[causal-automata] Loaded data with shape {data.shape}")

    print("[causal-automata] Running causal discovery via run_discovery...")
    adjmat = run_discovery(data)
    adjmat = np.asarray(adjmat)
    print(f"[causal-automata] Discovery finished; adjacency matrix shape {adjmat.shape}")

    print(f"[causal-automata] Writing adjacency matrix to: {args.output}")
    pd.DataFrame(adjmat).to_csv(args.output, header=False, index=False)
    print("[causal-automata] Done.")


if __name__ == "__main__":
    main()
