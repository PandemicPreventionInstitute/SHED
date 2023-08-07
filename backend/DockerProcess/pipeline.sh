#! /bin/bash

# Writen by Devon Gregory
# bash pipeline.sh to execute the backend pipeline
# Last edited on 7-28-23

# set logging
exec 1>pipe.log 2>&1

# get meta data for sra accessions to be processed
aws s3 cp s3://ppi-dev/shed/task_metadata_files/sra_meta_collect_${timestamp}_${count}.tsv sra_meta_collect_current.tsv

# get how many cores can be used to run the workflow
availcores=$(nproc)
echo "${availcores} cores detected"
cores=$(nproc)

workingdir=$( dirname -- "$( readlink -f -- "$0"; )"; )

starttime=$(date +'%Y-%m-%d.%T')
echo Pipeline run starting at "${starttime}"
echo Start time: "$starttime" > Pipeline.times

mkdir SRAs

# downloads the sra formated sample file for each match
# Writes fastq files based on the sra files and runs a quality check
# and trims if no primers are identified, then maps
# primer trimming if applicable
# variants are called, consensus sequences generated and lineages assigned
run="snakemake -c${cores} --use-conda -s $workingdir/snakefile --resources download_streams=20 --stats snakemake.stats"
if $run
then
echo "snakemake run successful"
else
echo "snakemake run failed"
# exit 1
fi

endtime=$(date +'%Y-%m-%d.%T')
echo Pipeline run ending at "${endtime}"
echo End time: "$endtime" >> Pipeline.times

python "${workingdir}"/update_processed_acc_list.py

echo Running s3 write
python "${workingdir}"/insert_to_db.py > db.log 2>&1

if [[ -f processed_SRA_Accessions.txt ]]
then
aws s3 cp processed_SRA_Accessions.txt s3://ppi-dev/shed/Processed_Accessions/${timestamp}_${count}_processed_SRA_Accessions.txt
fi

aws s3 cp snakemake.stats s3://ppi-dev/shed/logs/${timestamp}_${count}_sm.stats
aws s3 cp db.log s3://ppi-dev/shed/logs/${timestamp}_${count}_db.log
aws s3 cp Pipeline.times s3://ppi-dev/shed/logs/${timestamp}_${count}.times
aws s3 cp pipe.log s3://ppi-dev/shed/logs/${timestamp}_${count}_pipe.log
