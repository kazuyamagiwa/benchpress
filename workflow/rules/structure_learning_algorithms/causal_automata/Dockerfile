# syntax=docker/dockerfile:1
#
# Benchpress image for the causal-automata structure-learning module.
# Build:  docker build -t causal_automata:0.3.5 \
#           -f workflow/rules/structure_learning_algorithms/causal_automata/Dockerfile .
# Push:   docker tag causal_automata:0.3.5 <registry>/causal_automata:0.3.5
#         docker push <registry>/causal_automata:0.3.5
#
# Uses CPU JAX for portable Singularity/Apptainer runs. For GPU hosts,
# rebuild from a CUDA base and install causal-automata[cuda].

FROM python:3.10-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pandas \
        "causal-automata[cpu]==0.3.5"
