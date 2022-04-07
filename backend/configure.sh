#! /bin/bash

# written by Devon Gregory
# install dependencies and set up $PATHs
# uses conda to install most of the programs
# last edited on 4-6-22

# commented out req installs for yet to be implimented parts of pipeline

# # check to see if conda is installed, install if not
# conda_installed=$(command -v conda)
# echo $conda_installed
# if [ $conda_installed ]
	# then
	# echo miniconda installed
	# else
	# # getting version of python installed
	# python_version=$(python -V)
	# if [[ $python_version == Python*3.7.* || $python_version == Python*3.8.* || $python_version == Python*3.9.* || $python_version == Python*3.10.* ]]
		# then
		# version=$(echo $pythonversion | cut -d " " -f 2 | cut -d "." -f -2 )
		# versionnodot=$(echo $version | cut -d "." -f 1)$(echo $version | cut -d "." -f 2)
		# echo Installing Miniconda
		# wget https://repo.anaconda.com/miniconda/Miniconda3-py${versionnodot}_4.11.0-Linux-x86_64.sh
		# bash Miniconda3-py${versionnodot}_4.11.0-Linux-x86_64.sh
		# rm Miniconda3-py${versionnodot}_4.11.0-Linux-x86_64.sh
		# else
		# echo Please install python 3.7+ and rerun.
	# fi
# fi

# # set up conda channels
# conda config --add channels defaults
# conda config --add channels bioconda
# conda config --add channels conda-forge

# # install programs
# # cut_adapt https://github.com/marcelm/cutadapt
# # fastx tools http://hannonlab.cshl.edu/fastx_toolkit/license.html
# # minimap2 https://github.com/lh3/minimap2
# # bbtools https://github.com/kbaseapps/BBTools
# # sam refiner https://github.com/degregory/SAM_Refiner
# # pytest https://docs.pytest.org/en/7.1.x/contents.html
# conda install -c bioconda cutadapt
# conda install -c bioconda fastx_toolkit
# conda install -c bioconda minimap2
# conda install -c agbiome bbtools
conda install -c conda-forge pytest
conda install -c bioconda sra-tools
# if [ ! -f ./SAM_Refiner.py]
	# then
	# wget https://github.com/degregory/SAM_Refiner/blob/main/SAM_Refiner.py
# fi

