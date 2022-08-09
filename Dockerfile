FROM ubuntu:18.04 as builder

RUN apt-get update && apt-get install --yes \
    wget \
    libdigest-sha-perl \
    bzip2 \
    tar

# Download mambaforge and use it to install the mamba binary
RUN wget "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-pypy3-Linux-x86_64.sh" \
    # mamba must be installed at /databricks/mamba
    && /bin/bash Mambaforge-pypy3-Linux-x86_64.sh -b -p /databricks/mamba \
    && rm Mambaforge-pypy3-Linux-x86_64.sh

FROM databricksruntime/minimal:9.x

COPY --from=builder /databricks/mamba /databricks/mamba

COPY sratoolkit /databricks/sratoolkit

COPY env.yml /databricks/.mamba-env-def/env.yml

COPY backend /databricks/backend

COPY user-settings.mkfg /root/.ncbi

RUN /databricks/mamba/bin/mamba env create --file /databricks/.mamba-env-def/env.yml \
    # Source mamba.sh for all login shells.
    && ln -s /databricks/mamba/etc/profile.d/mamba.sh /etc/profile.d/mamba.sh \
    && ln -s /databricks/mamba/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# init conda
RUN /databricks/mamba/bin/conda init bash

## source sra tool kit commands
RUN  ln -s /databricks/sratoolkit/bin/prefetch /bin/prefetch \
    && ln -s /databricks/sratoolkit/bin/fasterq-dump /bin/fasterq-dump \
    && ln -s /databricks/mamba/bin/conda /bin/conda \
    && ln -s /databricks/mamba/bin/mamba /bin/mamba

# Conda recommends using strict channel priority speed up conda operations and reduce package incompatibility problems.
# Set always_yes to avoid needing -y flags, and improve conda experience in Databricks notebooks.
RUN /databricks/mamba/bin/conda config --system --set channel_priority strict \
    && /databricks/mamba/bin/conda config --system --set always_yes True

# This environment variable must be set to indicate the conda environment to activate.
# Note that currently, we have to set both of these environment variables. The first one is necessary to indicate that this runtime supports conda.
# The second one is necessary so that the python notebook/repl can be started (won't work without it)
ENV DEFAULT_DATABRICKS_ROOT_CONDA_ENV=shed-backend
ENV DATABRICKS_ROOT_CONDA_ENV=shed-backend
