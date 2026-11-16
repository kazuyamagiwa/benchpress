causal-automata :footcite:t:`yamagiwa2026causalautomata` is a JAX-accelerated
cellular automaton engine for causal discovery. It evolves an adjacency matrix
and a node elevation field under synchronous gravity / V-well / death / birth
updates, compiled with XLA for CPU or GPU backends.

This module wraps :class:`causal_automata.CausalAutomaton` (preferred) and
falls back to :func:`causal_automata.run` when an explicit
``skeleton_threshold`` is set. Continuous observations are column-standardized.
With ``threshold_death`` / ``threshold_birth`` / ``skeleton_threshold`` set to
``null``, Fisher-z thresholds are calibrated from ``n_samples`` and ``alpha``
(default ``0.01``), and the initial correlation skeleton is aligned to the
calibrated birth threshold (package ``corr_flat`` init).

The default Benchpress container is **CPU JAX** (multi-arch
``linux/amd64`` + ``linux/arm64``)::

    docker://ghcr.io/kazuyamagiwa/causal_automata:0.3.6

This module is **container-only** (no ``env.yaml`` / conda env). Use
``--use-singularity`` (or Docker) as in the smoke command below.

.. rubric:: GPU / Apptainer

``rule.smk`` pins the CPU image above. On NVIDIA hosts, build a **GPU**
image from the files in this directory (do **not** pass ``Dockerfile.gpu``
directly to ``apptainer build`` — Docker ``FROM`` is mis-parsed as a
Singularity definition):

.. code:: bash

    cd workflow/rules/structure_learning_algorithms/causal_automata
    apptainer build causal_automata_0.3.6_gpu.sif causal_automata_gpu.def
    apptainer exec --nv causal_automata_0.3.6_gpu.sif \
      python -c "import jax; print(jax.devices())"
    # expect CudaDevice(...) on a working GPU host

Equivalent Docker build (then convert with ``apptainer build … docker-daemon://…``
if desired): ``Dockerfile.gpu``.

Run Benchpress with GPU passthrough, e.g.::

    snakemake --cores N --resources gpu=1 --use-singularity \
      --singularity-args="--nv" --configfile … 

**Validated:** Apptainer ``--nv`` + the GPU SIF on an NVIDIA A10 (JAX reported
``CudaDevice``; module smoke completed). Nested-userns hosts (some RunPod
images) may block unprivileged ``apptainer build``; build the SIF on a normal
Linux GPU box or use a pre-built SIF.

.. rubric:: Example

Config snippet under ``resources.structure_learning_algorithms``:

.. code:: json

    "causal_automata": [
      {
        "id": "causal_automata",
        "ticks": 100,
        "k": null,
        "learning_rate": 0.1,
        "threshold_death": null,
        "threshold_birth": null,
        "skeleton_threshold": null,
        "alpha": 0.01,
        "multihop": false,
        "fuzzy": false,
        "timeout": null
      }
    ]

Smoke (CPU container via Singularity/Apptainer):

.. code:: bash

    snakemake --cores all --use-singularity \
      --configfile workflow/rules/structure_learning_algorithms/causal_automata/causal_automata.json
