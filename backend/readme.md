# SHED Backend Pipeline

This folder contains the scripts and tests for the backend bioinformatics pipeline for SHED.  This pipeline will query NCBI's SRA with a string in the config.yaml (see below) to obtain sample metadata (saved with a timestamp tag) and then download and process the raw sequencing data.  The pipeline uses snakemake.  Please make sure [snakemake 7.8+](https://snakemake.readthedocs.io/en/stable/) and [Miniconda](https://docs.conda.io/en/latest/miniconda.html) are installed.  To run the pipeline, clone this repository and use the command:
```bash
path/to/SHED/backend:$ bash pipeline.sh
```
You will be asked to provide the number of processor cores to use in running the pipeline before starting.  The first run will require significant additional processing time for snakemake to download and build environments for the pipeline's dependancies.  The pipeline requires and will install:

[NCBI's SRA Tools](https://github.com/ncbi/sra-tools)

[fastp](https://github.com/OpenGene/fastp)

[minimap2](https://github.com/lh3/minimap2)

[ivar](https://github.com/andersen-lab/ivar)

[freyja](https://github.com/andersen-lab/Freyja)

To modify the NCBI SRA query string, edit the config.yaml file, ie:
```
    query:
        wastewater+SARS-CoV-2+USA
```
To insure the correct query pattern, you may wish to run the query with [NCBI's web interface](https://www.ncbi.nlm.nih.gov/sra) and copy the string from the resulting url.

SRA samples that have already been downloaded and processing will will be reprocessed if the flag in the the config.yaml is set to True
```
    reprocess:
        True
```
and will not be reprocessed if the flag is set to False
```
    reprocess:
        False
```
Any samples that aren't found by NCBI's SRA Tools prefetch aren't processed further and a file is written to the SRAs/ directory indicating a bad accession.

## Workflow Details
The pipeline is split into three snakefiles/sections and relies on python functions found in modules/snakefuncions.py.  Each snakefile may be run seperately, ie
```bash
path/to/SHED/backend:$ snakemake -cN --use-conda -k -F -s snakefile1
```
The first section, snakefile1, is responsible for calling functions to query NCBI's SRA and obtain/process the metadata for the search's results.  The query results will be saved as search_results_TIMESTAMP.html, with the TIMESTAMP based on the time of running.  Partial and complete metadata will be downloaded as sra_data_TIMESTAMP.csv sra_meta_TIMESTAMP.xml respectively.  The xml will be converted into a more readable format as sra_meta_TIMESTAMP.txt and select metadata (accession, collection date, location and primer.bed) writen to sra_meta_collect_TIMESTAMP.tsv.  For the current run, the latter will also be writen to sra_meta_collect_current.tsv.  With these results, a snakemake rule downloads sra files for each sample via NCBI SRA Tools' prefetch in the SRAs subdirectory.
The second section handles writing the fastq files with NCBI SRA Tools' fasterq-dump, checking the reads' qualities using fastp and mapping quality passed reads with minimap2.  For samples that don't have known primers, fastp also trims 25nts from the 5' end of the reads. The outputs for this section are writen in the fastqs subdirectory or the sams subdirectory for the mapping.  The final section continues to process samples that have over 500 reads that mapped to the reference SARS-CoV-2 genome (NC_045512.2).  This section trims primers, calls variants and generates consensus using ivar, and assignes lineages with freyja.  Trimmed mapped reads are written to the sams subdirectory in bam format.  For each sample processed fully, the endpoints subdirectory will contain the tsv files for the variants and lineages, depth and quality files, and fasta files for the consensus sequence.  Data for all processed samples are aggregated into VCs.tsv for variants, Lineages.tsv for lineages and Consensus.fa for consensus.


## Testing
## not yet implimented
The pipeline and its modules are tested with [pytest](https://docs.pytest.org/en/7.1.x/).  The testing scripts can be found in the .tests subdirectory.  To run the tests, run pytest in the backend directory.

```bash
path/to/SHED/backend:$ pytest
```
