# Sequencing Hub for Environmental Data 

This repository will hold the bioinformatic pipeline and basic analyses 
validating  the Sequencing Hub for Environmental Data (SHED).

## Installation instructions

Installating the required programs on a PPI machine is a little bit
complicated. The following software is *required*:
- Anaconda (Miniconda is fine)
- [sra-tools](https://github.com/ncbi/sra-tools/wiki/02.-Installing-SRA-Toolkit)
- [FASTX-Toolkit](http://hannonlab.cshl.edu/fastx_toolkit/)

First, set up a clean conda environment (i.e. with no other programs
installed):
`conda create --name myenv python --no-default-packages`

Then, activate this environment and, in your home directory, run the following
command to download a compressed version of the SRA toolkit:
`curl -R --output sratoolkit.tar.gz
http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-mac64.tar.gz`
Note, that this command is similar to the suggested tar fetch from the install
instructions on the website but the `-R` flag is added to allow for redirects.
Otherwise the generated file is not actually a zipped version of the required
files, rather it is a an empty file that will cause subsequent steps to fail.

Next, as the SRA install instructions suggest, unzip the file:
`tar -vxzf sratoolkit.tar.gz`

And append it to your path:
`export PATH=$PATH:$PWD/sratoolkit.2.11.2-mac64/bin`

*BE SURE* that this path points correctly to the unpacked version of the SRA
toolkit.

Running this `export` command will work until the shell is closed, but to allow
it to be accessible in the future, it should be added to the `.zshrc` or
`.bashrc`.

Then, install `pytest` with `conda install pytest`.

Install the FASTX-toolkit with `conda install -c bioconda
fastx_toolkit`. I was getting issues with slightly different versions of
packages needed than were installed with `pytest`. If this occurs, it can be
solved with `conda config --set channel_priority false` and then rerunning the
installation of fastx toolkit.

Finally, install `SAM refiner` with `conda install -c bioconda samrefiner`.
 

 
