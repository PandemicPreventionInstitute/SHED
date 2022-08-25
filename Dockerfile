FROM ubuntu:18.04 as builder

RUN apt-get update && apt-get install --yes \
    wget \
    libdigest-sha-perl \
    bzip2

# Download miniconda and use it to install the conda binary
RUN wget -q https://repo.continuum.io/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh -O miniconda.sh \
    # Conda must be installed at /databricks/conda
    && /bin/bash miniconda.sh -b -p /databricks/conda \
    && rm miniconda.sh

FROM databricksruntime/minimal:9.x

COPY --from=builder /databricks/conda /databricks/conda

COPY env.yml /databricks/.conda-env-def/env.yml

COPY sratoolkit /databricks/sratoolkit

COPY backend /databricks/backend

COPY user-settings.mkfg /root/.ncbi

# source sra tool kit commands
RUN  ln -s /databricks/sratoolkit/bin/prefetch /bin/prefetch \
    && ln -s /databricks/sratoolkit/bin/fasterq-dump /bin/fasterq-dump

# install mamba via conda and init
RUN /databricks/conda/bin/conda install -c conda-forge mamba \
    && /databricks/conda/bin/conda init bash \
    && ln -s /databricks/conda/bin/conda /bin/conda \
    && ln -s /databricks/conda/bin/mamba /bin/mamba

RUN /databricks/conda/bin/mamba env create --file /databricks/.conda-env-def/env.yml \
    # Source conda.sh for all login shells.
    && ln -s /databricks/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# Conda recommends using strict channel priority speed up conda operations and reduce package incompatibility problems.
# Set always_yes to avoid needing -y flags, and improve conda experience in Databricks notebooks.
RUN /databricks/conda/bin/conda config --system --set channel_priority strict \
    && /databricks/conda/bin/conda config --system --set always_yes True

# This environment variable must be set to indicate the conda environment to activate.
# Note that currently, we have to set both of these environment variables. The first one is necessary to indicate that this runtime supports conda.
# The second one is necessary so that the python notebook/repl can be started (won't work without it)
ENV DEFAULT_DATABRICKS_ROOT_CONDA_ENV=dcs-minimal
ENV DATABRICKS_ROOT_CONDA_ENV=dcs-minimal
