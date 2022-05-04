## SHED Backend Pipeline

This folder contains the scripts and tests for the backend bioinformatics pipeline for SHED.  This pipeline will query NCBI's SRA to obtains sample metadata (not yet implimented) and then download and process the raw sequencing data.  To run the pipeline, several thrid party software packages must be installed.  See requirements.txt for the list of these.  The main script for the pipeline can be run with
```bash
$ python3 pipeline.py
```
Currently the pipeline uses a metadata table to determine which SRA accessions to process.  Either SraRunTable.csv or SraRunTable.txt in the working directory or a metadata file given as a argument will used.
```bash
$ python3 pipeline.py -i SRAMetaDataTable.txt
```
The working directory, where the pipeline will look for and write files is defaulted as the directory where the command is called, but can be changed by arguemnt as well.
```bash
$ python3 pipeline.py -d /path/to/working/directory
```
The pipeline relies on several modules to perform specific tasks.  These modules can be run as stand alone scripts to perform their specific tasks.

# sra_query.py (not yet implimented)

# sra_file_parse.py

The module sra_file_parse.py is required for all of the other modules.  It has functions to parse an input file argument, to read a metadata table to get the SRA accessions and to find pre-existing raw fastq files for a SRA sample.

# sra_fetch.py

The module sra_fetch.py is a wrapper for NCBI's SRA Toolkit and will download the raw sequencing data from NCBI's SRA and write the sra and fastq files in the SRAs and fastqs subdirectories respectively.

# sra_preproc.py

The module sra_preproc.py is a wrapper for BBTools and fastx toolkit and will process the raw fastq files so that the reads can be easily mapped and processed for variant information.  Processing incules merging, and if necessary repair, of paired reads.  All reads are trimmed of adapaters and primers when possible and of low quality base calls (not yet implimented).  All reads are then dereplicated.

# sra_map.py

The module sra_map.py is a wrapper for minimap2 and will map samples' dereplicated reads to the SAR-CoV-2 reference genome (NC_045512.2).

# sra_vc.py

The module sra_vc.py is a wrapper for SAM Refiner and will collect variant information from the mapped reads.

# sra_consensus.py

The module sra_consensus.py will generate a consensus sequence for an SRA sample based on the NT calls output and write the consenes to a sample's consenses fasta (fasta subdirectory) and a collection of consenssus sequences, Consensus.tsv (working directory).

# sra_output_aggregate.py

The module sra_output_aggregate.py will collect sample information for polymorphisms and NT calls and add them to the tsv collection Polymorphisms.tsv and NT_Calls.tsv.


# Testing

The pipeline and its modules can be tested for proper function using pytest.  The testing scripts can be found in the tests subdirectory.  To run the tests, run pytest in the backend directory.

```bash
path/to/SHED/backend:$ pytest
```