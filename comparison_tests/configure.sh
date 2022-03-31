#! /bin/bash

# written by Devon Gregory
# install dependencies and set up $PATHs
# uses conda to install most of the programs
# last edited on 3-31-22

check to see if conda is installed, install if not
#installed=$(command -v conda)
echo $installed
if [ $installed ]
	then
	echo miniconda installed
	else
	# getting versino of python installed
	pythonversion=$(python -V)
	echo $pythonversion
	if [[ $pythonversion == Python*3.*.* && ! $pythonversion == Python*3.1.* ]]
		then
		version=$(echo $pythonversion | cut -d " " -f 2 | cut -d "." -f -2 )
		echo $version 
		versionnodot=$(echo $version | cut -d "." -f 1)$(echo $version | cut -d "." -f 2)
		echo $versionnodot
		echo Installing Miniconda
		wget https://repo.anaconda.com/miniconda/Miniconda3-py${versionnodot}_4.11.0-Linux-x86_64.sh
		bash Miniconda3-py${versionnodot}_4.11.0-Linux-x86_64.sh
		else
		echo Please install python 3.7+ and rerun.
	fi
fi

# set up conda channels
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge

# install programs
# iVar https://github.com/andersen-lab/ivar
# cut_adapt https://github.com/marcelm/cutadapt
# fastx tools http://hannonlab.cshl.edu/fastx_toolkit/license.html
# minimap2 https://github.com/lh3/minimap2
# bwa https://github.com/lh3/bwa
# samtools https://github.com/samtools/samtools
conda install -c bioconda samtools
conda install -c bioconda ivar
conda install -c bioconda cutadapt
conda install -c bioconda fastx_toolkit
conda install -c bioconda minimap2
conda install -c bioconda bwa

# set up paths for 