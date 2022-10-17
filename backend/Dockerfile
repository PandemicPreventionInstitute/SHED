FROM snakemake/snakemake
# Switch to git pull and put on ECR
COPY . .
RUN /bin/bash -c "conda config --set channel_priority strict"
RUN conda env create -f docker_environment.yml
RUN /bin/bash -c "source activate test-docker"
RUN /bin/bash -c "conda install -c conda-forge curl"
RUN wget --output-document sratoolkit.tar.gz https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-ubuntu64.tar.gz
RUN tar -vxzf sratoolkit.tar.gz
ENV PATH="$PATH:/tmp/repo/sratoolkit.3.0.0-ubuntu64/bin"
RUN mkdir /root/.ncbi/
COPY  ./user-settings.mkfg /root/.ncbi/user-settings.mkfg
RUN /bin/bash -c "bash pipeline.sh"
RUN /bin/bash -c "pip install duckdb"
RUN /bin/bash -c "python insert_to_db.py"
