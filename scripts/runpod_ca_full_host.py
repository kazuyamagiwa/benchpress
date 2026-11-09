#!/usr/bin/env python3
"""Host-native causal-automata full matrix (no Apptainer / Benchpress containers).

Matches ``config/runpod_full.json`` graph sizes / seeds / CA hyperparams as closely
as practical without pcalg::randDAG:

  graphs: ER + SF, p in {20,50,80,100}, expected degree d≈4, max_parents=5
  data:   SEM weights U[0.25,1], n=1000, column-standardized
  seeds:  1..10
  alg:    ticks=50, k=3, lr=0.1, alpha=0.01, Fisher-z death/birth

Shape-matched JAX warmup is excluded from wall time (same policy as script.py).

Run on the RunPod 4090 (Option C host CUDA)::

  cd /workspace/benchpress
  python scripts/runpod_ca_full_host.py

Outputs under ``results/runpod_ca_full_host/``.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np

from causal_automata import (
    CausalAutomaton,
    binarize,
    enable_x64,
    fisher_z_threshold,
    run,
    warmup,
)

P_LIST = (20, 50, 80, 100)
METHODS = ("er", "sf")
SEEDS = range(1, 11)
N_SAMPLES = 1000
D_AVG = 4.0
MAX_PARENTS = 5
WEIGHT_MIN, WEIGHT_MAX = 0.25, 1.0

TICKS = 50
K = 3
LEARNING_RATE = 0.1
ALPHA = 0.01


def _er_dag(p: int, d: float, max_parents: int, rng: np.random.Generator) -> np.ndarray:
    """Random topological order + Erdős–Rényi edges with E[degree]≈d."""
    order = rng.permutation(p)
    pos = {int(node): i for i, node in enumerate(order)}
    prob = min(1.0, d / max(p - 1, 1))
    A = np.zeros((p, p), dtype=np.int8)
    parent_count = np.zeros(p, dtype=int)
    for i in range(p):
        for j in range(i + 1, p):
            u, v = int(order[i]), int(order[j])  # u before v in topo → u → v
            if rng.random() >= prob:
                continue
            if parent_count[v] >= max_parents:
                continue
            A[v, u] = 1
            parent_count[v] += 1
    del pos
    return A


def _sf_dag(p: int, d: float, max_parents: int, rng: np.random.Generator) -> np.ndarray:
    """Preferential-attachment skeleton oriented along a random topo order."""
    m = max(1, int(round(d / 2)))
    # Build undirected BA-like edges then orient by topo order.
    targets = []
    for new in range(p):
        if new == 0:
            continue
        # sample m distinct earlier nodes with degree bias
        if new == 1:
            targets.append((0, 1))
            continue
        degrees = np.zeros(new, dtype=float)
        for a, b in targets:
            if a < new:
                degrees[a] += 1
            if b < new:
                degrees[b] += 1
        degrees = np.maximum(degrees, 0.1)
        probs = degrees / degrees.sum()
        k = min(m, new)
        chosen = rng.choice(new, size=k, replace=False, p=probs)
        for c in chosen:
            targets.append((int(c), new))

    order = rng.permutation(p)
    rank = {int(node): i for i, node in enumerate(order)}
    A = np.zeros((p, p), dtype=np.int8)
    parent_count = np.zeros(p, dtype=int)
    for a, b in targets:
        # orient lower topo rank → higher
        if rank[a] < rank[b]:
            src, dst = a, b
        else:
            src, dst = b, a
        if parent_count[dst] >= max_parents:
            continue
        A[dst, src] = 1
        parent_count[dst] += 1
    return A


def _sample_sem(A: np.ndarray, n: int, wmin: float, wmax: float, rng: np.random.Generator) -> np.ndarray:
    p = A.shape[0]
    W = A.astype(np.float64) * rng.uniform(wmin, wmax, size=A.shape) * rng.choice(
        [-1.0, 1.0], size=A.shape
    )
    # topological order from DAG
    indeg = A.sum(axis=1).astype(int)  # parents counted on rows if A[i,j]=1 means j→i
    # Our A[child, parent]=1 ⇒ indegree = row sum
    order = []
    indeg_work = A.sum(axis=1).copy()
    ready = [i for i in range(p) if indeg_work[i] == 0]
    while ready:
        i = ready.pop()
        order.append(i)
        children = np.where(A[:, i] == 1)[0]
        for c in children:
            indeg_work[c] -= 1
            if indeg_work[c] == 0:
                ready.append(int(c))
    if len(order) != p:
        # fallback: use any permutation (should not happen for DAG)
        order = list(range(p))

    X = np.zeros((n, p), dtype=np.float64)
    for i in order:
        parents = np.where(A[i] == 1)[0]
        noise = rng.normal(0.0, 1.0, size=n)
        if len(parents) == 0:
            X[:, i] = noise
        else:
            X[:, i] = X[:, parents] @ W[i, parents] + noise
    # column standardize
    std = X.std(axis=0, ddof=0)
    std[std == 0.0] = 1.0
    X = (X - X.mean(axis=0, keepdims=True)) / std
    return X


def _skeleton_counts(true_A: np.ndarray, est_A: np.ndarray) -> tuple[int, int, int, float]:
    t = ((true_A + true_A.T) > 0).astype(int)
    e = ((est_A + est_A.T) > 0).astype(int)
    np.fill_diagonal(t, 0)
    np.fill_diagonal(e, 0)
    # undirected edges as upper triangle
    tu = np.triu(t, 1)
    eu = np.triu(e, 1)
    tp = int(np.logical_and(tu == 1, eu == 1).sum())
    fp = int(np.logical_and(tu == 0, eu == 1).sum())
    fn = int(np.logical_and(tu == 1, eu == 0).sum())
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return tp, fp, fn, f1


def _shape_matched_warmup(n_nodes: int, n_samples: int, k_eff: int, thr_d: float, thr_b: float) -> None:
    import jax
    import jax.numpy as jnp

    print(f"[warmup] device={warmup(n=n_nodes, k=k_eff, fuzzy=False, multihop=False)}")
    A_w = jnp.zeros((n_nodes, n_nodes), dtype=jnp.float64)
    E_w = jnp.linspace(1.0, 0.0, n_nodes, dtype=jnp.float64)
    Cov_w = jnp.eye(n_nodes, dtype=jnp.float64)
    A1, _ = run(
        A_w,
        E_w,
        Cov_w,
        ticks=1,
        k=k_eff,
        learning_rate=LEARNING_RATE,
        threshold_death=thr_d,
        threshold_birth=thr_b,
        n_samples=n_samples,
        alpha=ALPHA,
        fuzzy=False,
        multihop=False,
    )
    jax.block_until_ready(A1)
    Af, _ = run(
        A_w,
        E_w,
        Cov_w,
        ticks=TICKS,
        k=k_eff,
        learning_rate=LEARNING_RATE,
        threshold_death=thr_d,
        threshold_birth=thr_b,
        n_samples=n_samples,
        alpha=ALPHA,
        fuzzy=False,
        multihop=False,
    )
    jax.block_until_ready(Af)


def run_one(method: str, p: int, seed: int, out_dir: Path) -> dict:
    rng = np.random.default_rng(seed + (0 if method == "er" else 10_007) + p * 1009)
    if method == "er":
        A_true = _er_dag(p, D_AVG, MAX_PARENTS, rng)
    else:
        A_true = _sf_dag(p, D_AVG, MAX_PARENTS, rng)

    X = _sample_sem(A_true, N_SAMPLES, WEIGHT_MIN, WEIGHT_MAX, rng)
    thr_d = fisher_z_threshold(N_SAMPLES, k_cond=K, alpha=ALPHA)
    thr_b = 1.2 * thr_d

    enable_x64()
    _shape_matched_warmup(p, N_SAMPLES, K, thr_d, thr_b)

    import jax

    print(f"[run] method={method} p={p} seed={seed} devices={jax.devices()}")
    t0 = time.perf_counter()
    model = CausalAutomaton(
        ticks=TICKS,
        k=K,
        learning_rate=LEARNING_RATE,
        threshold_death=None,
        threshold_birth=None,
        alpha=ALPHA,
        backend="jax",
        multihop=False,
        fuzzy=False,
        seed=seed,
    )
    model.fit(X)
    adj_raw = model.adjacency_
    if hasattr(adj_raw, "block_until_ready"):
        adj_raw.block_until_ready()
    est = np.asarray(binarize(adj_raw), dtype=int)
    np.fill_diagonal(est, 0)
    elapsed = time.perf_counter() - t0

    tp, fp, fn, f1 = _skeleton_counts(A_true, est)
    case_dir = out_dir / f"{method}_p{p}" / f"seed_{seed}"
    case_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(case_dir / "true_adjmat.csv", A_true, delimiter=",", fmt="%d")
    np.savetxt(case_dir / "est_adjmat.csv", est, delimiter=",", fmt="%d")
    (case_dir / "time.txt").write_text(str(elapsed))

    row = {
        "method": method,
        "p": p,
        "seed": seed,
        "n": N_SAMPLES,
        "ticks": TICKS,
        "k": K,
        "time_s": round(elapsed, 6),
        "skel_tp": tp,
        "skel_fp": fp,
        "skel_fn": fn,
        "skel_f1": round(f1, 6),
        "thr_death": thr_d,
        "thr_birth": thr_b,
    }
    print(
        f"[done] {method} p={p} seed={seed} time={elapsed:.4f}s "
        f"skel_f1={f1:.3f} tp/fp/fn={tp}/{fp}/{fn}"
    )
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/runpod_ca_full_host"),
        help="Output directory (default: results/runpod_ca_full_host)",
    )
    parser.add_argument("--methods", nargs="+", default=list(METHODS))
    parser.add_argument("--p", nargs="+", type=int, default=list(P_LIST))
    parser.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    args = parser.parse_args()

    import jax

    print("[info] jax.devices() =", jax.devices())
    args.out.mkdir(parents=True, exist_ok=True)

    rows = []
    for method in args.methods:
        for p in args.p:
            for seed in args.seeds:
                rows.append(run_one(method, p, seed, args.out))
                # checkpoint after each cell
                with (args.out / "summary.csv").open("w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(rows)

    (args.out / "meta.json").write_text(
        json.dumps(
            {
                "note": "Host-native CA full matrix; graphs approximate pcalg randDAG (not identical).",
                "n_samples": N_SAMPLES,
                "d_avg": D_AVG,
                "max_parents": MAX_PARENTS,
                "ca": {
                    "ticks": TICKS,
                    "k": K,
                    "learning_rate": LEARNING_RATE,
                    "alpha": ALPHA,
                },
            },
            indent=2,
        )
    )
    print(f"[info] wrote {args.out / 'summary.csv'} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
