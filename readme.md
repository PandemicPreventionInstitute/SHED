# Sequencing Hub for Environmental Data

This repository holds the bioinformatic pipeline used by the Sequencing Hub
for Environmental Data (SHED).

## Installation instructions

Installing the required programs on a PPI machine is a little bit
complicated. There are pipeline-specific installation instructions in the
`readme.md` in the `backend/` directory. This `readme.md` contains
instructions for prerequisites for installation on a PPI machine.

The pipeline is designed to work with Conda and Mamba (a derivative of Conda).
Both need to be installed.

The pipeline will not work properly unless it's in a **Mamba** environment,
not a _Conda environment_. This should be accomplished by generating a clean
environment with nothing installed (i.e., no default installs).

```
conda create --name myenv --no-default-packages
```

Then, activate this environment and, in your home directory, run the following
command to download a compressed version of the SRA toolkit:
`curl -R --output sratoolkit.tar.gz
http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-mac64.tar.gz`
Note, this command is similar to the suggested tar fetch from the install
instructions on the SRA install instructions website but the `-R` flag is added to allow for redirects.
Otherwise the generated file is not actually a zipped version of the required
files, rather it is an empty file that will cause subsequent steps to fail.

You can also download a prebuilt binary from the [SRA
Github](https://github.com/ncbi/sra-tools/wiki/01.-Downloading-SRA-Toolkit)

Next, as the SRA install instructions suggest, unzip the file:
`tar -vxzf sratoolkit.tar.gz`

And append it to your path:
`export PATH=$PATH:$PWD/sratoolkit.3.0.0-mac64/bin`

*BE SURE* that this path points correctly to the unpacked version of the SRA
toolkit. The version of the SRA toolkit should be at least `3.0.0` to ensure
that the required functionality is available. Packages managers like Homebrew
and Anaconda/Bioconda are currently installing versions below 3.0,
necessitating manual install.

Running this `export` command will work until the shell is closed, but to cause
the export to automatically occur when activating the environment in the future,
it should be added to the Anaconda environment startup files.
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

export PATH="$PATH:/Users/zsusswein/sratoolkit.3.0.0-mac64/bin"
```
But replace `zsusswein` in the path with your own username.

Although some of the required packages will install automatically when running
the pipeline in `backend/` (e.g., `fastx_toolkit`), others will not. It's
safest to install everything in `backend/requirements.txt` manually to avoid
weird errors cropping up. These should be installed with the `mamba` package
manager, not conda. In addition, be sure to check that the correct versions
are being installed.

## Developer settings
If you're going to be working on the pipeline, please set up
[pre-commit hooks](https://pre-commit.com/). Install the
`pre-commmit` package manager and install pre-commit into the `SHED/`
directory after cloning a local copy of the repository. As usual, please work
on a branch off of `dev` and open a PR with any changes.
