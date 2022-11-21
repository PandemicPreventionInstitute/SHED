#! /bin/bash

# Writen by Devon Gregory
# bash to execute the 3 snakefiles in turn
# Last edited on 11-21-22

echo "Enter number of cores to use in running the pipeline"
# get how many cores should be used to run the workflow
availcores=$(nproc)
echo "${availcores} cores detected"
read -r cores
# cores=1
workingdir=$( dirname -- "$( readlink -f -- "$0"; )"; )

# Queries NCBI's SRA for matches to the config.yaml query string
# downloads the sra formated sample file for each match
# Writes fastq files based on the sra files and runs a quality check
# and trims if no primers are identified, then maps
run="snakemake -c${cores} --use-conda -k -F -s $workingdir/snakefile1 --resources download_streams=20"
if $run
then
echo "snakefile1 run successful"
else
echo "snakemake1 run failed"
exit 1
fi

# checks which samples passed the quality check
# those that did are primer trimmed if applicable
# variants are called, consensus sequences generated and lineages assigned
run="snakemake -c${cores} --use-conda -k -F -s $workingdir/snakefile2"
if $run
then
echo "snakefile2 run successful"
else
echo "snakemake2 run failed"
exit 1
fi
