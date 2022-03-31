Camparison testing of different programs that might be incorporated into the final backend pipeline.
Currently tested are:
iVar - variant calling and primer trimming
SAM Refienr - variant calling
BWA - mapping
minimap2 - mapping
cutadapt - primer trimming

aditional required programs:
SRA Toolkit - used to download fastq of SRA samples to run tests with
samtools - required for iVar
BBTools - repair and merger of paired reads, potentially necessary for all and benificial for SAM Refiner respectively
fastx toolkit - benificial for SAM Refiner

Preprocessing:
paired reads were repaired (2 samples required repair), merged and collapsed. (./scripts/joinandcol.sh)

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
