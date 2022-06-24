# Sequencing Hub for Environmental Data

This repository will hold the bioinformatic pipeline and basic analyses
validating  the Sequencing Hub for Environmental Data (SHED).

## Installation instructions

Installing the required programs on a PPI machine is a little bit
complicated. The following software is *required*:
- Anaconda (Miniconda is fine)
- [sra-tools](https://github.com/ncbi/sra-tools/wiki/02.-Installing-SRA-Toolkit)
- [FASTX-Toolkit](http://hannonlab.cshl.edu/fastx_toolkit/)

First, set up a clean conda environment (i.e., with no other programs
installed):
`conda create --name myenv python --no-default-packages`

Then, activate this environment and, in your home directory, run the following
command to download a compressed version of the SRA toolkit:
`curl -R --output sratoolkit.tar.gz
http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-mac64.tar.gz`
Note, this command is similar to the suggested tar fetch from the install
instructions on the SRA install instructions website but the `-R` flag is added to allow for redirects.
Otherwise the generated file is not actually a zipped version of the required
files, rather it is an empty file that will cause subsequent steps to fail.

Next, as the SRA install instructions suggest, unzip the file:
`tar -vxzf sratoolkit.tar.gz`

And append it to your path:
`export PATH=$PATH:$PWD/sratoolkit.2.11.2-mac64/bin`

*BE SURE* that this path points correctly to the unpacked version of the SRA
toolkit. The version of the SRA toolkit should be at least 2.11.2 to ensure
that the required functionality is available. Packages managers like Homebrew
are currently installing versions below 2.11, necessitating manual install.

Running this `export` command will work until the shell is closed, but to cause
the export to automatically occur when activating the environment in the future, it should be added to the Anaconda
environment startup files.
This can be accomplished by doing the following:

- Locate the directory for the conda environment by (in the activated
  environment) running `echo $CONDA_PREFIX`.
- Move to the directory by the same name as the conda directory (`cd
  $CONDA_PREFIX`) and create the following folders and files:
```
mkdir -p ./etc/conda/activate.d
mkdir -p ./etc/conda/deactivate.d
touch ./etc/conda/activate.d/env_vars.sh
touch ./etc/conda/deactivate.d/env_vars.sh
```
- Edit the ` ./etc/conda/activate.d/env_vars.sh` so that it looks like the
  following:
```
#!/bin/sh

export PATH="$PATH:/Users/zsusswein/sratoolkit.2.11.2-mac64/bin"
```
But replace `zsusswein` in the path with your own username.

Then, install `pytest` with `conda install pytest`.

Install the FASTX-toolkit with `conda install -c bioconda
fastx_toolkit`. I was getting issues with slightly different versions of
packages needed than were installed with `pytest`. If this occurs, it can be
solved with `conda config --set channel_priority false` and then rerunning the
installation of fastx toolkit.

Then, `cd` to the folder in which the `pipeline.py` script is running and
install `SAM refiner` with `curl
https://raw.githubusercontent.com/degregory/SAM_Refiner/main/SAM_Refiner.py -o
SAM_Refiner.py`. Do not use conda/bioconda because the version it installs is
not the latest and will not have all of the required features.

To set up [pre-commit hooks](https://pre-commit.com/), install the
`pre-commmit` package manager.
