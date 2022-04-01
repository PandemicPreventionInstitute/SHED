Camparison testing of different programs that might be incorporated into the final backend pipeline for pulling read files from NCBI's SRA and processing them to pull relevent sequence information that can be programatically queried.
Seven SRA samples were chosen for testing: ERR5996055, ERR6008925, ERR7277155, ERR7395993, ERR7505063, SRR15128978, SRR15128983.  These represent both clinical and wastewater samples and different sequencing methods.  Programs were tested against each other for performing the same functions and compared for both speed of processing and similiarity of results.

Currently tested are:
BWA - mapping
minimap2 - mapping

cutadapt - primer trimming
iVar - variant calling and primer trimming
SAM Refienr - variant calling

aditional required programs:
SRA Toolkit - used to download fastq of SRA samples
samtools - required for iVar
BBTools - repair and merger of paired reads, potentially necessary for all and benificial for SAM Refiner respectively
fastx toolkit - benificial for SAM Refiner

All programs can be installed by running 'bash configure.sh'

Preprocessing:
Reads were downloaded with the SRA Toolkit commands 'prefetch <SRA_Accession>'and 'fastq-dump <SRA_Accession> --splitfiles'.
Then paired reads were repaired (2 samples required repair), merged and collapsed. (./scripts/joinandcol.sh)

Testing
tests were run programatically.  see scripts folder
mapping:
mapping of both paired reads and collapsed reads was done with BWA and minimap2 --> ./results/mappingtimes.txt
primer trimming:
trimming of arctic v3 primers was done with iVar or cutadapt on sam or fasta/q files respectively with collapsed or paired reads --> ./results/trimmingtimes.txt, mm.pairs.trimstats.txt, mm.col.trimstats.txt, paired.CutInfo.txt, col.CutInfo.txt
variant calling:
calling of variants was done with iVar or SAM Refiner on paired, merged (not collapsed) or collapsed mapped reads --> ./results/varcalltimes.txt

run times for each input-process were recorded
results were further compaired for similiarities/differences manually or programatically

samstats.py pulled general mapping stats from each sam --> ./results/SAM_stats.txt
samlinecompare.py generates a more detailed comparison of reads mapped differently between bwa and minimap2 --> ./results/x.sam_mismatches.tsv


results
see report.rtf
and results.gz.tar
