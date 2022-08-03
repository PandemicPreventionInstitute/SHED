#! /bin/bash

# Writen by Devon Gregory
# bash to execute the 3 snakefiles in turn
# Last edited on 8-3-22

cores=$1

workingdir=$( dirname -- "$( readlink -f -- "$0"; )"; )

# Queries NCBI's SRA for matches to the config.yaml query string
# downloads the sra formated sample file for each match
run="snakemake -c${cores} -k -F -s $workingdir/snakefile1"
if $run
then
echo "snakefile1 run successful"
else
echo "snakemake1 run failed"
exit 1
fi

# Checks to see what sra files were downloaded from the query results
# Writes fastq files based on the sra files and runs a quality check
# and trims if no primers are identified, then maps
run="snakemake -c${cores} -k -F -s $workingdir/snakefile2"
if $run
then
echo "snakefile2 run successful"
else
echo "snakemake2 run failed"
exit 1
fi

# checks which samples passed the quality check
# those that did are primer trimmed if applicable
# variants are called, consensus sequences generated and lineages assigned
run="snakemake -c${cores} -k -F -s $workingdir/snakefile3"
if $run
then
echo "snakefile3 run successful"
else
echo "snakemake3 run failed"
exit 1
fi
