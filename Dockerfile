FROM mambaorg/micromamba:1.4.4

USER root

## Install git
RUN apt-get update -y && apt-get install -y git

## Install dependencies with mamba
USER $MAMBA_USER
WORKDIR /home/$MAMBA_USER

RUN micromamba install --yes --name base --channel conda-forge --channel bioconda --channel defaults \
    tower-cli=0.8.0  \
    python=3.10.4 \
    pyyaml=6.0.0 && \
    micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN pip install --no-deps git+https://github.com/ejseqera/tw-pywrap.git@main

ENV PATH="$PATH:/opt/conda/bin"