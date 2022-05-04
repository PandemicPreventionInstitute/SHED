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

The module sra_fetch.py will download the raw sequencing data from NCBI's SRA and write the sra and fastq files in the SRAs and fastqs subdirectories respectively.

# sra_preproc.py

The module sra_preproc.py wlll process the raw fastq files so that the reads can be easily mapped and processed for varient information.  Processing incules merging, and if necessary repair, of paired reads.  All reads are trimmed of adapaters and primers when possible and of low quality base calls (not yet implimented).  All reads are then dereplicated. 

# sra_map.py 