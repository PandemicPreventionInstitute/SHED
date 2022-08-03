FROM ubuntu:18.04 as builder

RUN apt-get update && apt-get install --yes \
    wget \
    libdigest-sha-perl \
    bzip2 \
    tar

# Download miniconda and use it to install the conda binary
RUN wget -q https://repo.continuum.io/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh -O miniconda.sh \
    # Conda must be installed at /databricks/conda
    && /bin/bash miniconda.sh -b -p /databricks/conda \
    && rm miniconda.sh

FROM databricksruntime/minimal:9.x

COPY --from=builder /databricks/conda /databricks/conda

COPY env.yml /databricks/.conda-env-def/env.yml

RUN /databricks/conda/bin/conda env create --file /databricks/.conda-env-def/env.yml \
    # Source conda.sh for all login shells.
    && ln -s /databricks/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# Conda recommends using strict channel priority speed up conda operations and reduce package incompatibility problems.
# Set always_yes to avoid needing -y flags, and improve conda experience in Databricks notebooks.
RUN /databricks/conda/bin/conda config --system --set channel_priority strict \
    && /databricks/conda/bin/conda config --system --set always_yes True

# This environment variable must be set to indicate the conda environment to activate.
# Note that currently, we have to set both of these environment variables. The first one is necessary to indicate that this runtime supports conda.
# The second one is necessary so that the python notebook/repl can be started (won't work without it)
ENV DEFAULT_DATABRICKS_ROOT_CONDA_ENV=shed-backend
ENV DATABRICKS_ROOT_CONDA_ENV=shed-backend

# install NCBI's SRA Toolkit.
RUN wget -q https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.0.0/sratoolkit.3.0.0-ubuntu64.tar.gz -O sratoolkit.3.0.0-ubuntu64.tar.gz \
    && tar xf /bin/sratoolkit.3.0.0-ubuntu64.tar.gz /databricks/ \
    && ln -s /databricks/sratoolkit.3.0.0-ubuntu64/bin/prefetch /etc/profile.d/prefetch \
    && ln -s /databricks/sratoolkit.3.0.0-ubuntu64/bin/fasterq-dump /etc/profile.d/fasterq-dump
