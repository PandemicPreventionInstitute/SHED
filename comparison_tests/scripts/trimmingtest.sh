#! /bin/bash

# written by Devon Gregory
# script for running primmer trimming processes, ivar (https://github.com/andersen-lab/ivar) and cutadapt (https://github.com/marcelm/cutadapt),
# and tracking time for each program/input
# ivar reqires bam format to run, cutadapt fastq/a.  Paths for primers may need to be updated.
# for more detailed time/computational load info, comment out all but one block and run $ time bash trimmingtest.sh
# last edited on 3-31-22


Sampid=''
echo "starting ivar trim test on paired"
START="$(date +%s)"
for file in *
do
	if [[ $file == *.mm.pairs.sam ]]
		then
		Sampid=$(echo $file | cut -d "." -f 1 )
		echo $Sampid
		samtools sort -o $Sampid.mm.pairs.sorted.bam $file && samtools index $Sampid.mm.pairs.sorted.bam # ivar required sorted bam
		# primers provided in bed format, writes program stdout etc to file
		ivar trim -b ../data/nCoV-2019.primer.bed -p $Sampid.mm.pairs.trimmed -i $Sampid.mm.pairs.sorted.bam -e &>> mm.pairs.trimstats.txt 
	fi
done
END="$(date +%s)"
echo "ivar trim run time on paired reads: $[ ${END} - ${START} ]"

Sampid=''
echo "starting ivar trim test on merged col"
START="$(date +%s)"
for file in *
do
	if [[ $file == *.mm.col.sam ]]
		then
		Sampid=$(echo $file | cut -d "." -f 1 )
		echo $Sampid
		samtools sort -o $Sampid.mm.col.sorted.bam $file && samtools index $Sampid.mm.col.sorted.bam
		ivar trim -b ../data/nCoV-2019.primer.bed -p $Sampid.mm.col.trimmed -i $Sampid.mm.col.sorted.bam -e &>> mm.col.trimstats.txt
	fi
done
END="$(date +%s)"
echo "ivar trim run time on collapsed: $[ ${END} - ${START} ]"

Sampid=''
echo "starting cutadapt trim test on paired"
START="$(date +%s)"
for file in *
do
	if [[ $file == *_1.rep.fastq ]]
		then
		Sampid=$(echo $file | cut -d "_" -f 1 )
		echo $Sampid
		# primers in fasta with sequences anchored at 5', writes program stdout etc to file
		cutadapt -g file:../data/NEBArticv3_for_plus.fasta -o $Sampid.1.cut.fa $file &>> paired.CutInfo.txt 
		cutadapt -g file:../data/NEBArticv3_rev_minus.fasta -o $Sampid.2.cut.fa ${Sampid}_2.rep.fastq &>> paired.CutInfo.txt 
	fi
done
END="$(date +%s)"
echo "cutadapt run time on paired: $[ ${END} - ${START} ]"

Sampid=''
echo "starting cutadapt trim test on merged col"
START="$(date +%s)"
for file in *
do
	if [[ $file == *.collapsed.fa ]]
		then
		Sampid=$(echo $file | cut -d "." -f 1 )
		echo $Sampid
		cutadapt -g file:../data/NEBArticv3_for_plus.fasta -o $Sampid.col.cut1.fa $file &>> col.CutInfo.txt 
		# 3' anchored, can be run together, but I've had better results running them separatlye
		cutadapt -a file:../data/NEBArticv3_rev_plus.fasta -o $Sampid.col.cut.fa $Sampid.col.cut1.fa &>> col.CutInfo.txt 
	fi
done
END="$(date +%s)"
echo "cutadapt run time on collapsed: $[ ${END} - ${START} ]"