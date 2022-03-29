#! /bin/bash

# script for finding paired fastq files in the working directory then repairing, merging, cat'ing and collapsing reads

Sampid=''
for file in *
do
	if [[ $file == *_1.fastq ]]
		then
		Sampid=$(echo $file | cut -d "_" -f 1 )
		echo $Sampid
		## repair paired reads
		bash /mnt/d/Rockefeller/software/bbmap/repair.sh in=$file in2=${Sampid}_2.fastq out=${Sampid}_1.rep.fastq out2=${Sampid}_2.rep.fastq outs=${Sampid}_sing.rep.fastq > $Sampid.repstats.txt
		## merge paired reads
		bash /mnt/d/Rockefeller/software/bbmap/bbmerge.sh in1=${Sampid}_1.rep.fastq in2=${Sampid}_2.rep.fastq  out=$Sampid.merge.fq outu1=$Sampid.un1.fq outu2=$Sampid.un2.fastq > $Sampid.mergestats.txt
		## concatenate merged and unmerged reads
		cat $Sampid.merge.fq $Sampid.un1.fq $Sampid.un2.fastq ${Sampid}_sing.rep.fastq > $Sampid.all.fq
		## collapse repeated sequences in reads
		fastx_collapser -i $Sampid.all.fq -o $Sampid.collapsed.fa > $Sampid.colstats.txt
	fi
done