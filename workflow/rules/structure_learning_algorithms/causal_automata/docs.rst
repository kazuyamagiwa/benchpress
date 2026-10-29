causal-automata :footcite:t:`yamagiwa2025causalautomata` is a JAX-accelerated
cellular automaton engine for causal discovery. It evolves an adjacency matrix
and a node elevation field under synchronous gravity / V-well / death / birth
updates, compiled with XLA for CPU or GPU backends.

This module wraps :func:`causal_automata.run` and :func:`causal_automata.binarize`.
Continuous observational data are column-standardized, an empirical covariance
is estimated, and the CA is initialized from a correlation skeleton with near-flat
elevations (the package's ``corr_flat`` init mode).

.. rubric:: Example

Config snippet under ``resources.structure_learning_algorithms``:

.. code:: json

    "causal_automata": [
      {
        "id": "causal-automata-default",
        "ticks": 100,
        "k": null,
        "learning_rate": 0.1,
        "threshold_death": 0.05,
        "threshold_birth": 0.15,
        "skeleton_threshold": 0.1,
        "multihop": false,
        "fuzzy": false,
        "timeout": null
      }
    ]

Local conda test (after pointing evaluation ids at ``causal-automata-default``):

.. code:: bash

    snakemake --cores all --use-conda --configfile config/causal_automata_test.json
