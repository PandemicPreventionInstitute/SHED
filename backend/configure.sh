#!/usr/bin/env bash

# written by Devon Gregory
# install dependencies
# uses conda to install most of the programs
# last edited on 4-20-22

# commented out req installs for yet to be implimented parts of pipeline

# check to see if conda is installed, install if not
conda_installed=$(command -v conda)
echo "$conda_installed"
if [ "$conda_installed" ]
	then
	echo miniconda installed
	else
	# getting version of python installed
	python_version=$(python3 -V)
	if [[ $python_version == Python*3.7.* || $python_version == Python*3.8.* || $python_version == Python*3.9.* || $python_version == Python*3.10.* ]]
		then
		version=$(echo "$python_version" | cut -d " " -f 2 | cut -d "." -f -2 )
		versionnodot=$(echo "$version" | cut -d "." -f 1)$(echo "$version" | cut -d "." -f 2)
		if [[ $versionnodot == 310 ]]
			then
			versionnodot=39
		fi
		echo Installing Miniconda
		wget https://repo.anaconda.com/miniconda/Miniconda3-py${versionnodot}_4.11.0-Linux-x86_64.sh
		bash Miniconda3-py${versionnodot}_4.11.0-Linux-x86_64.sh
		rm Miniconda3-py${versionnodot}_4.11.0-Linux-x86_64.sh
		echo Please restart your shell and rerun configure.sh
		exit
		else
		echo Please install python 3.7+ and rerun.
		exit
	fi
fi

# create local conda environment where most dependencies will be installed
# # install programs 
# # todo: add install checks for packages to choose install or update
# # cut_adapt https://github.com/marcelm/cutadapt
# fastx tools http://hannonlab.cshl.edu/fastx_toolkit/license.html
# # minimap2 https://github.com/lh3/minimap2
# bbtools https://github.com/kbaseapps/BBTools
# # sam refiner https://github.com/degregory/SAM_Refiner
# pytest https://docs.pytest.org/en/7.1.x/contents.html
echo "Installing dependencies in local environment."
# vast overestimate of time and space (I hope)
echo "This may take a long time. (1h+ ) and may require at least 1.7 Gb of free space" 
conda config --set channel_priority strict
conda env create --file environment.yml

if ! test -f ./SAM_Refiner.py;	
then
	wget https://raw.githubusercontent.com/degregory/SAM_Refiner/main/SAM_Refiner.py
fi

