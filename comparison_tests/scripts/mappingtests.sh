#! /bin/bash

# script for running mapping programs, bwa-mem or minimap2, on collapsed singleton or paired reads and reporting time elapse of the run
# for more detailed time/computational load info, comment out all but one block and run $ time bash mappingtests.sh

Sampid=''
echo "starting bwa mem test on collapsed"
START="$(date +%s)"
for file in *
do
	if [[ $file == *.collapsed.fa ]] # searches current directory for collapsed read files
		then
		Sampid=$(echo $file | cut -d "." -f 1 )
		echo $Sampid
		bwa mem SARS2.fasta $file -t 3 > $Sampid.bwamem.col.sam ## run bwa mem mapping
		
	fi
	
done
END="$(date +%s)"
echo "bwamem run time on collapsed: $[ ${END} - ${START} ]"


Sampid=''
echo "starting minimap2 test on collapsed"
START="$(date +%s)"
for file in *
do
	if [[ $file == *.collapsed.fa ]]
		then
		Sampid=$(echo $file | cut -d "." -f 1 )
		echo $Sampid
		minimap2 -a SARS2.fasta $file -o $Sampid.mm.col.sam
		
	fi
	
done
END="$(date +%s)"
echo "minimap2 run time on collapsed: $[ ${END} - ${START} ]"


Sampid=''
echo "starting bwa mem test on repaired pairs"
START="$(date +%s)"
for file in *
do
	if [[ $file == *_1.rep.fastq ]]
		then
		Sampid=$(echo $file | cut -d "_" -f 1 )
		echo $Sampid
		bwa mem SARS2.fasta $file ${Sampid}_2.rep.fastq -t 3 > $Sampid.bwamem.pairs.sam
		
	fi
	
done
END="$(date +%s)"
echo "bwamem run time on paired: $[ ${END} - ${START} ]"


Sampid=''
echo "starting minimap2 test on repaired pairs"
START="$(date +%s)"
for file in *
do
	if [[ $file == *_1.rep.fastq ]]
		then
		Sampid=$(echo $file | cut -d "_" -f 1 )
		echo $Sampid
		minimap2 -a SARS2.fasta $file ${Sampid}_2.rep.fastq -o $Sampid.mm.pairs.sam
		
	fi
	
done
END="$(date +%s)"
echo "minimap2 run time on paired: $[ ${END} - ${START} ]"

