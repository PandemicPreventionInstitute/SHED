#! /bin/bash

# script for running variant calling with ivar and tracking time for each program/input
# ivar reqires bam format to run
# for more detailed time/computational load info, comment out all but one block and run $ time bash variantcallingtest.sh
# SAM Refiner command is commented at end.  Should be run from command line in folder with just targed sams for timing info

Sampid=''
echo "starting ivar var test on paired"
START="$(date +%s)"
for file in *
do
	if [[ $file == *.mm.pairs.sam ]]
		then
		Sampid=$(echo $file | cut -d "." -f 1 )
		echo $Sampid
		samtools sort -o $Sampid.mm.pairs.sorted.bam $file && samtools index $Sampid.mm.pairs.sorted.bam # sort and index in bam
		# ivar needs reference fasta to call variants and gff for aa codon reporting
		samtools mpileup -aa -A -d 0 -B -Q 0 $Sampid.mm.pairs.sorted.bam | ivar variants -p $Sampid.mm.pairs -t 0.03 -r SARS2.fasta -g NC_045512.2.gff3
	fi
done
END="$(date +%s)"
echo "ivar run time on paired reads: $[ ${END} - ${START} ]"

Sampid=''
echo "starting ivar var test on col"
START="$(date +%s)"
for file in *
do
	if [[ $file == *.mm.col.sam ]]
		then
		Sampid=$(echo $file | cut -d "." -f 1 )
		echo $Sampid
		samtools sort -o $Sampid.mm.col.sorted.bam $file && samtools index $Sampid.mm.col.sorted.bam
		samtools mpileup -aa -A -d 0 -B -Q 0 $Sampid.mm.col.sorted.bam | ivar variants -p $Sampid.mm.col -t 0.03 -r SARS2.fasta -g NC_045512.2.gff3
	fi
done
END="$(date +%s)"
echo "ivar run time on collapsed reads: $[ ${END} - ${START} ]"

Sampid=''
echo "starting ivar var test on merged"
START="$(date +%s)"
for file in *
do
	if [[ $file == *mm.all.sam ]]
		then
		Sampid=$(echo $file | cut -d "." -f 1 )
		echo $Sampid
		samtools sort -o $Sampid.mm.all.sorted.bam $file && samtools index $Sampid.mm.all.sorted.bam
		samtools mpileup -aa -A -d 0 -B -Q 0 $Sampid.mm.all.sorted.bam | ivar variants -p $Sampid.mm.all -t 0.03 -r SARS2.fasta -g NC_045512.2.gff3
	fi
done
END="$(date +%s)"
echo "ivar run time on merged reads: $[ ${END} - ${START} ]"

## run in a folder with just the sams to be processed.  Provides 3 outputs, nt_call, nt_var and covars.  nt_var is most equivelent to ivar output. 
# time python /mnt/d/Rockefeller/software/SAM_Refiner.py -r /mnt/g/MU_WW/SARS2/SARS2.gb --wgs 1 --collect 0 --seq 0 --indel 0 --covar 1 --max_covar 1 --nt_call 1 --ntvar 1 --read 0 --min_count 1 --min_samp_abund 0.03 --min_col_abund 0 --ntabund 0 --ntcover 1 --AAreport 1 --chim_rm 0 --deconv 0