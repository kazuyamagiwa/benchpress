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

## 5. Build / verify the causal-automata **GPU** image

`rule.smk` defaults to the public immutable tag
`docker://ghcr.io/kazuyamagiwa/causal_automata:0.3.6`. For fair GPU wall
times on the 4090, build the CUDA image from this repo and point the rule
at that SIF (or a GPU-tagged registry image).

### Option A — local SIF from `causal_automata_gpu.def` (recommended on this pod)

Apptainer does **not** build Dockerfiles directly. Passing `Dockerfile.gpu`
makes it treat the file as a Singularity definition, which fails with:

`invalid header keyword found: from nvidia/cuda`

Use the sibling definition file instead (same contents as `Dockerfile.gpu`):

```bash
cd workflow/rules/structure_learning_algorithms/causal_automata
apptainer build causal_automata_0.3.6_gpu.sif causal_automata_gpu.def

apptainer exec --nv causal_automata_0.3.6_gpu.sif \
  python -c "import jax; print(jax.devices()); import causal_automata as ca; print(ca.__version__)"
```

You should see a `cuda` / GPU device, not only `CpuDevice`.

Then set the container URI in `rule.smk` to the absolute SIF path, e.g.:

```python
container:
    "/workspace/benchpress/workflow/rules/structure_learning_algorithms/causal_automata/causal_automata_0.3.6_gpu.sif"
```

If you have a working Docker daemon (often **not** available inside a RunPod
container), you can instead:

```bash
docker build -t causal_automata:0.3.6-gpu -f Dockerfile.gpu .
apptainer build causal_automata_0.3.6_gpu.sif docker-daemon://causal_automata:0.3.6-gpu
```

### Option B — keep the GHCR tag

Only do this if that tag already contains JAX CUDA wheels and you have
confirmed `jax.devices()` lists a GPU under `apptainer exec --nv`.

## 6. Smoke test (optional but recommended)

```bash
cd /workspace/benchpress   # repo root
snakemake --cores 4 --resources gpu=1 --use-singularity \
  --singularity-args="--nv" \
  --configfile config/codespaces_smoke_test.json
```

Confirm `causal_automata` finishes and adjmat / time files appear under
`results/`.

## 7. Full matrix (`runpod_full`)

```bash
cd /workspace/benchpress
snakemake --cores 8 --resources gpu=1 --use-singularity \
  --singularity-args="--nv" \
  --configfile config/runpod_full.json
```

Notes:

- `--resources gpu=1` matches `resources: gpu=1` in
  `causal_automata/rule.smk` so only one GPU job runs at a time.
- Other algorithms in `runpod_full.json` use their own containers; they
  typically run on CPU unless those modules declare GPU resources.
- Shape-matched JAX warmup in `script.py` excludes compile time from the
  recorded wall clock.

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
| `jax.devices()` is CPU-only | Rebuild/use `Dockerfile.gpu`; pass `--nv` |
| GHCR `403` on pull | `apptainer registry logout docker://ghcr.io`; empty `DOCKER_CONFIG` |
| Apptainer mount / userns errors | Install `apptainer-suid`; ensure fuse packages present |
| Pod preempted (Spot) | Switch to On-Demand; keep outputs on a network volume |
| Disk full | Grow container disk; prune old SIFs under `~/.apptainer` |

## Related files

- `config/runpod_full.json` — full benchmark config
- `config/codespaces_smoke_test.json` — small smoke config
- `workflow/rules/structure_learning_algorithms/causal_automata/Dockerfile.gpu`
- `workflow/rules/structure_learning_algorithms/causal_automata/causal_automata_gpu.def`
- `workflow/rules/structure_learning_algorithms/causal_automata/rule.smk`
- `workflow/rules/structure_learning_algorithms/causal_automata/script.py`
