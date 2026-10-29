sys.path.append("workflow/scripts/utils")

import time

import numpy as np
import pandas as pd
from add_timeout import *
from causal_automata import binarize, default_conditioning_k, enable_x64, run, warmup
from causal_automata.bayesian_synth import (
    correlation_skeleton_adjacency,
    empirical_covariance,
    flat_elevations,
)


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes"}


def myalg():
    """Estimate a DAG adjacency with causal-automata (JAX CA engine)."""
    print("[causal_automata] Reading input data")
    df = pd.read_csv(snakemake.input["data"])
    X = np.asarray(df.values, dtype=np.float64)
    n_nodes = X.shape[1]
    print(f"[causal_automata] Data shape={X.shape}")

    seed = int(snakemake.wildcards["seed"])
    ticks = int(snakemake.wildcards["ticks"])
    learning_rate = float(snakemake.wildcards["learning_rate"])
    threshold_death = float(snakemake.wildcards["threshold_death"])
    threshold_birth = float(snakemake.wildcards["threshold_birth"])
    skeleton_threshold = float(snakemake.wildcards["skeleton_threshold"])
    multihop = _as_bool(snakemake.wildcards["multihop"])
    fuzzy = _as_bool(snakemake.wildcards["fuzzy"])

    k_raw = snakemake.wildcards["k"]
    if str(k_raw).lower() in {"none", "null", ""}:
        k = int(default_conditioning_k(n_nodes))
    else:
        k = int(k_raw)

    # Column-standardize continuous observations (package synth path does this for n>10).
    col_std = X.std(axis=0, ddof=0)
    col_std[col_std == 0.0] = 1.0
    X = (X - X.mean(axis=0, keepdims=True)) / col_std

    Cov = empirical_covariance(X)
    A0 = correlation_skeleton_adjacency(Cov, threshold=skeleton_threshold)
    e_rng = np.random.default_rng(seed + 91_733)
    E0 = flat_elevations(n_nodes, e_rng, noise=1e-4)

    print(
        "[causal_automata] Running discovery: "
        f"ticks={ticks}, k={k}, multihop={multihop}, fuzzy={fuzzy}"
    )
    enable_x64()
    print(f"[causal_automata] warmup: {warmup(n=min(8, n_nodes), k=min(k, 2))}")

    import jax.numpy as jnp

    A_final, _E_final = run(
        jnp.asarray(A0),
        jnp.asarray(E0),
        jnp.asarray(Cov),
        ticks=ticks,
        k=k,
        learning_rate=learning_rate,
        threshold_death=threshold_death,
        threshold_birth=threshold_birth,
        fuzzy=fuzzy,
        multihop=multihop,
    )
    adjmat = np.asarray(binarize(A_final), dtype=int)
    np.fill_diagonal(adjmat, 0)
    print(f"[causal_automata] Finished; adjmat shape={adjmat.shape}")

    tottime = time.perf_counter() - start
    with open(snakemake.output["time"], "w") as text_file:
        text_file.write(str(tottime))

    adjmat_df = pd.DataFrame(adjmat)
    adjmat_df.columns = df.columns
    adjmat_df.to_csv(snakemake.output["adjmat"], index=False)

    with open(snakemake.output["ntests"], "w") as text_file:
        text_file.write("None")


start = time.perf_counter()

if snakemake.wildcards["timeout"] == "None":
    myalg()
else:
    with timeoutf(
        int(snakemake.wildcards["timeout"]),
        snakemake.output["adjmat"],
        snakemake.output["time"],
        snakemake.output["ntests"],
        start,
    ):
        myalg()
