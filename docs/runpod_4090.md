# RunPod RTX 4090 — Benchpress full GPU runbook

How to run the fork’s full causal-automata benchmark matrix on a RunPod
**Ubuntu 22.04** pod using template

`runpod/base:1.5.0-cuda1281-ubuntu2204`

with a single **RTX 4090**.

This is a host-side guide for the fork branch
`cursor/causal-automata-warmup-gpu-upstream-bb9c`. It is not part of the
upstream Benchpress module PR.

## What this pod is for

| Piece | Role |
| --- | --- |
| RunPod base image | Host OS + NVIDIA driver / CUDA 12.8 runtime |
| `config/runpod_full.json` | Full matrix: ER/SF, `p ∈ {20,50,80,100}`, `n=1000`, seeds `1..10` |
| `Dockerfile.gpu` | JAX CUDA 12 + `causal-automata==0.3.6` image for GPU timing |
| Apptainer / Singularity | How Benchpress launches each algorithm container (`--nv`) |

The base template is **not** the algorithm container. Benchpress still pulls
or builds per-algorithm images (including `causal_automata`).

## 1. Deploy the pod

1. In the RunPod console, pick **GPU Pod** → **RTX 4090**.
2. Template: **Ubuntu 22.04** / `runpod/base:1.5.0-cuda1281-ubuntu2204`.
3. Prefer **On-Demand** over Spot for a long `runpod_full` run.
4. Disk: ≥ 50 GB container disk (Apptainer cache + Snakemake outputs grow).
5. Attach a **network volume** if you want results to survive pod destroy.
6. SSH in (or use the web terminal).

Sanity-check the GPU:

```bash
nvidia-smi
```

## 2. Clone the fork branch

```bash
cd /workspace   # or your volume mount
git clone https://github.com/kazuyamagiwa/benchpress.git
cd benchpress
git checkout cursor/causal-automata-warmup-gpu-upstream-bb9c
```

## 3. Install Apptainer (Singularity-compatible)

On Ubuntu 22.04:

```bash
sudo apt-get update
sudo apt-get install -y software-properties-common \
  uidmap squashfuse fuse2fs fuse-overlayfs squashfs-tools
sudo add-apt-repository -y ppa:apptainer/ppa
sudo apt-get update
sudo apt-get install -y apptainer apptainer-suid || sudo apt-get install -y apptainer
sudo ln -sf "$(command -v apptainer)" /usr/local/bin/singularity
apptainer --version
```

If an unauthenticated GHCR pull ever hits stale Docker credentials:

```bash
apptainer registry logout docker://ghcr.io || true
export DOCKER_CONFIG="$(mktemp -d)"
```

## 4. Install Snakemake (host)

Minimal micromamba/conda env on the pod:

```bash
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
./bin/micromamba create -y -n benchpress -c conda-forge -c bioconda \
  python=3.10 snakemake
eval "$(./bin/micromamba shell hook -s bash)"
micromamba activate benchpress
```

(Or use any other host Python env that provides `snakemake ≥ 7.30`.)

## 5. Get a **GPU** runtime for causal-automata

`rule.smk` defaults to `docker://ghcr.io/kazuyamagiwa/causal_automata:0.3.6`
(often CPU JAX). On an RTX 4090 you want CUDA JAX.

**RunPod pods are nested containers.** Apptainer `%post` often fails with:

`Failed to create user namespace: … unprivileged_userns_clone`

Try **Option A** once; if userns stays blocked, use **Option C** (recommended
fallback on RunPod — no SIF build).

### Option A — build SIF from `causal_automata_gpu.def`

Do **not** pass `Dockerfile.gpu` to `apptainer build` (Apptainer mis-parses
Docker `FROM`). Use the sibling `.def`, with the setuid helper:

```bash
sudo apt-get update
sudo apt-get install -y apptainer-suid || true

# May be denied inside a nested RunPod container — OK if it fails.
sudo sysctl -w kernel.unprivileged_userns_clone=1 || true
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0 || true

cd workflow/rules/structure_learning_algorithms/causal_automata
apptainer build --fakeroot causal_automata_0.3.6_gpu.sif causal_automata_gpu.def
```

If that still dies on user namespaces, skip to **Option C**.

Verify GPU JAX:

```bash
apptainer exec --nv causal_automata_0.3.6_gpu.sif \
  python -c "import jax; print(jax.devices()); import causal_automata as ca; print(ca.__version__)"
```

Point `rule.smk` at the absolute SIF path:

```python
container:
    "/workspace/benchpress/workflow/rules/structure_learning_algorithms/causal_automata/causal_automata_0.3.6_gpu.sif"
```

### Option B — pull a prebuilt GPU OCI image (no `%post`)

Only if a CUDA-tagged image exists in a registry you can pull, e.g.:

```bash
apptainer pull causal_automata_0.3.6_gpu.sif \
  docker://ghcr.io/kazuyamagiwa/causal_automata:0.3.6-gpu
```

`pull` does not run `%post`, so it avoids the userns build failure. Confirm
`jax.devices()` shows a GPU under `apptainer exec --nv`, then point `rule.smk`
at the SIF as in Option A.

### Option C — host CUDA pip (recommended RunPod fallback)

Install CUDA JAX on the **pod host** (drivers already come from the RunPod
template) and run `causal_automata` without its own container. Other
algorithms still use Apptainer via `--use-singularity`.

```bash
# Use the same Python that Snakemake’s script: directive will call
# (the micromamba env from step 4 is fine).
python -m pip install -U pip
python -m pip install --no-cache-dir \
  "jax[cuda12]==0.4.38" \
  "causal-automata==0.3.6" \
  pandas

python -c "import jax; print(jax.devices()); import causal_automata as ca; print(ca.__version__)"
```

You should see a CUDA device. Then comment out / remove the `container:`
block in `rule.smk` so this rule runs on the host:

```python
# container:
#     "docker://ghcr.io/kazuyamagiwa/causal_automata:0.3.6"
```

Keep `--use-singularity --singularity-args="--nv"` for the rest of the
workflow; rules without `container:` execute locally.

## 6. Smoke test (optional but recommended)

```bash
cd /workspace/benchpress   # repo root
snakemake --cores 4 --resources gpu=1 --use-singularity \
  --singularity-args="--nv" \
  --configfile config/codespaces_smoke_test.json
```

Confirm `causal_automata` finishes and adjmat / time files appear under
`results/`.

## 7. Full matrix

### 7a. causal-automata only on this RunPod (no Apptainer) — recommended now

Nested RunPod pods block Apptainer (already inside a user namespace), so
Benchpress data-gen containers (`bpimages/pcalg`, …) cannot run here.
Use the host-native GPU runner that mirrors the `runpod_full` matrix for
**causal-automata only** (ER/SF, p∈{20,50,80,100}, seeds 1..10, n=1000):

```bash
cd /workspace/benchpress
# Option C host packages must already be installed; jax.devices() must show GPU
python -c "import jax; print(jax.devices())"
python scripts/runpod_ca_full_host.py
# optional subset: python scripts/runpod_ca_full_host.py --p 20 --seeds 1 2 3
```

Results: `results/runpod_ca_full_host/summary.csv` (post-warmup wall time +
skeleton F1). Graphs are ER/SF approximations (not bit-identical to
`pcalg::randDAG`).

### 7b. Full multi-algorithm Benchpress (`runpod_full`) — needs a VM

Requires working Apptainer (Jarvislabs `--vm`, Lambda Cloud, etc.), not a
nested RunPod pod:

```bash
cd /workspace/benchpress
snakemake --cores 8 --resources gpu=1 --use-singularity \
  --configfile config/runpod_full.json
# CA-only Snakemake variant (still needs Apptainer for data gen):
#   --configfile config/runpod_ca_only.json
```

Notes:

- `--resources gpu=1` matches `resources: gpu=1` in
  `causal_automata/rule.smk` so only one GPU job runs at a time.
- Other algorithms in `runpod_full.json` use their own containers; they
  typically run on CPU unless those modules declare GPU resources.
- Shape-matched JAX warmup in `script.py` excludes compile time from the
  recorded wall clock.
- Do **not** pass global `--nv` / `--userns` unless you have verified
  Apptainer exec works on that host.

### 7c. Known-good host: Lambda Cloud A10 (2026-11-09)

Nested RunPod failed Apptainer userns; the full `runpod_full` matrix for
this fork was completed on a **Lambda Cloud** instance with native
Apptainer + `--nv` GPU pass-through. Fingerprint for the paper / PR
record:

```text
GPU:        NVIDIA A10, 23028 MiB, driver 580.105.08
            UUID GPU-49da81ac-19cb-7ea6-ba81-e71e6373ca4a
CPU:        30× Intel Xeon Platinum 8358 @ 2.60GHz
RAM:        222 GiB
OS/kernel:  Ubuntu 22.04 / Lambda Stack, 6.8.0-1064-nvidia
Hostname:   159-54-176-210
Apptainer:  1.5.5
```

Capture the same block on any new host before a paper-facing run:

```bash
nvidia-smi -L
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
lscpu | egrep 'Model name|CPU\(s\)|Thread|Core'
free -h | head -2
uname -a
apptainer --version
```

## 8. Where results land

Under the usual Benchpress `results/` tree. Plots / tables for this config
use the prefix `runpod_full/` (see `filename_prefix` in
`config/runpod_full.json`).

Copy artifacts off the pod before destroying it:

```bash
# example
rsync -avz -e ssh results/ user@home:~/benchpress-runpod-full/
```

## Quick troubleshooting

| Symptom | Likely fix |
| --- | --- |
| `jax.devices()` is CPU-only | Use Option A/C CUDA JAX; pass `--nv` for SIF exec |
| GHCR `403` on pull | `apptainer registry logout docker://ghcr.io`; empty `DOCKER_CONFIG` |
| `unprivileged_userns_clone` / `%post` fails | Install `apptainer-suid` + `--fakeroot`; if still blocked, **Option C** |
| Apptainer mount errors | Install `apptainer-suid` + fuse packages |
| Pod preempted (Spot) | Switch to On-Demand; keep outputs on a network volume |
| Disk full | Grow container disk; prune old SIFs under `~/.apptainer` |

## Related files

- `config/runpod_full.json` — full benchmark config
- `config/codespaces_smoke_test.json` — small smoke config
- `workflow/rules/structure_learning_algorithms/causal_automata/Dockerfile.gpu`
- `workflow/rules/structure_learning_algorithms/causal_automata/causal_automata_gpu.def`
- `workflow/rules/structure_learning_algorithms/causal_automata/rule.smk`
- `workflow/rules/structure_learning_algorithms/causal_automata/script.py`
