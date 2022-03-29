#! /bin/bash

# script for running primmer trimming processes, ivar and cutadapt, and tracking time for each program/input
# ivar reqires bam format to run, cutadapt fastq/a
# for more detailed time/computational load info, comment out all but one block and run $ time bash trimmingtest.sh


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
		ivar trim -b nCoV-2019.primer.bed -p $Sampid.mm.pairs.trimmed -i $Sampid.mm.pairs.sorted.bam -e &>> mm.pairs.trimstats.txt # primers proved in bed format
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
		ivar trim -b nCoV-2019.primer.bed -p $Sampid.mm.col.trimmed -i $Sampid.mm.col.sorted.bam -e &>> mm.col.trimstats.txt
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
		cutadapt -g file:NEBArticv3_for_plus.fasta -o $Sampid.1.cut.fa $file &>> paired.CutInfo.txt # primers in fasta with sequences anchored at 5'
		cutadapt -g file:NEBArticv3_rev_minus.fasta -o $Sampid.2.cut.fa ${Sampid}_2.rep.fastq &>> paired.CutInfo.txt 
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
		cutadapt -g file:NEBArticv3_for_plus.fasta -o $Sampid.col.cut1.fa $file &>> col.CutInfo.txt 
		# 3' anchored, can be run together, but I've had better results running them separatlye
		cutadapt -a file:NEBArticv3_rev_plus.fasta -o $Sampid.col.cut.fa $Sampid.col.cut1.fa &>> col.CutInfo.txt 
	fi
done
END="$(date +%s)"
echo "cutadapt run time on collapsed: $[ ${END} - ${START} ]"