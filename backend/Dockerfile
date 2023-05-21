FROM snakemake/snakemake:v7.18.2
COPY . .
RUN /bin/bash -c "conda config --set channel_priority flexible"
# RUN wget --output-document sratoolkit.tar.gz https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-ubuntu64.tar.gz
RUN tar -vxzf sratoolkit.tar.gz
ENV PATH="$PATH:/tmp/repo/sratoolkit.3.0.0-ubuntu64/bin"
RUN mkdir /root/.ncbi/
COPY  ./user-settings.mkfg /root/.ncbi/user-settings.mkfg

RUN mkdir -p /var/bind/
RUN touch /var/bind/intermediates
VOLUME ["/var/bind"]

RUN /bin/bash -c "apt-get update"
RUN /bin/bash -c "apt-get install nano"

RUN /bin/bash -c "install_packages unzip"

# install awscli
# RUN wget "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -O "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install -i /usr/local/aws-cli -b /usr/local/bin
RUN rm "awscliv2.zip"

# RUN wget https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/debian_amd64/amazon-ssm-agent.deb
# RUN apt-get install ./amazon-ssm-agent.deb -y

RUN /bin/bash -c "pip install duckdb"
