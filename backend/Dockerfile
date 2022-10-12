FROM snakemake/snakemake
# Switch to git pull and put on ECR
COPY . .
RUN /bin/bash -c "conda config --set allow_conda_downgrades true"
RUN /bin/bash -c "conda config --set channel_priority false"
RUN conda env create -f docker_environment.yml
RUN /bin/bash -c "source activate test-docker"
RUN /bin/bash -c "conda install -c conda-forge curl"
RUN wget --output-document sratoolkit.tar.gz https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-ubuntu64.tar.gz
RUN tar -vxzf sratoolkit.tar.gz
ENV PATH="$PATH:/tmp/repo/sratoolkit.3.0.0-ubuntu64/bin"
RUN wget https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/debian_amd64/amazon-ssm-agent.deb
RUN apt install amazon-ssm-agent.deb -y
RUN mkdir /root/.ncbi/
COPY  ./user-settings.mkfg /root/.ncbi/user-settings.mkfg
RUN /bin/bash -c "bash pipeline.sh"
