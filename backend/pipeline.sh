#! /bin/bash

echo "Enter number of cores to use in running the pipeline"

read -r cores

run="snakemake -c${cores} --use-conda -k -F -s snakefile1"
if $run
then
echo "snakefile1 run successful"
else
echo "snakemake1 run failed"
exit 1
fi

run="snakemake -c${cores} --use-conda -k -F -s snakefile2"
if $run
then
echo "snakefile2 run successful"
else
echo "snakemake2 run failed"
exit 1
fi

run="snakemake -c${cores} --use-conda -k -F -s snakefile3"
if $run
then
echo "snakefile3 run successful"
else
echo "snakemake3 run failed"
exit 1
fi
