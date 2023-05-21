#! /bin/bash

# Writen by Devon Gregory
# bash pipeline.sh to execute the backend pipeline
# Last edited on 5-21-23

aws configure set aws_access_key_id "${s3_access_key_id}"
aws configure set aws_secret_access_key "${s3_secret_access_key}"
aws configure set default.region us-east-1

aws s3 cp s3://ppi-dev/shed/processed_SRA_Accessions.txt processed_SRA_Accessions.txt

echo "Enter number of cores to use in running the pipeline"
# get how many cores should be used to run the workflow
availcores=$(nproc)
echo "${availcores} cores detected"
# read -r cores
# cores=1
# if [[ -z $cores ]]
# then
cores=$(nproc)
# fi
workingdir=$( dirname -- "$( readlink -f -- "$0"; )"; )

starttime=$(date +'%Y-%m-%d.%T')
echo Pipeline run starting at "${starttime}"
echo Start time: "$starttime" > Pipeline.times

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

endtime=$(date +'%Y-%m-%d.%T')
echo Pipeline run ending at "${endtime}"
echo End time: "$endtime" >> Pipeline.times

python "${workingdir}"/update_processed_acc_list.py

echo Running s3 write
python "${workingdir}"/insert_to_db.py
if [[ -f processed_SRA_Accessions.txt ]]
then
aws s3 cp processed_SRA_Accessions.txt s3://ppi-dev/shed/processed_SRA_Accessions.txt
fi
