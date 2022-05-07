# SHED Backend Pipeline

This folder contains the scripts and tests for the backend bioinformatics pipeline for SHED.  This pipeline will query NCBI's SRA to obtains sample metadata (not yet implemented) and then download and process the raw sequencing data.  To run the pipeline, several thrid party software packages must be installed.  See requirements.txt for the list of these.  The main script for the pipeline can be run with
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

## sra_query.py (not yet implemented)

## sra_file_parse.py

The module sra_file_parse.py is required for all of the other modules.  It has functions to parse an input file argument, to read a metadata table to get the SRA accessions and to find pre-existing raw fastq files for a SRA sample.

## sra_fetch.py

The module sra_fetch.py is a wrapper for NCBI's SRA Toolkit and will download the raw sequencing data from NCBI's SRA and write the sra and fastq files in the SRAs and fastqs subdirectories respectively.

## sra_preproc.py

The module sra_preproc.py is a wrapper for BBTools and fastx toolkit and will process the raw fastq files so that the reads can be easily mapped and processed for variant information.  Processing incules merging, and if necessary repair, of paired reads.  All reads are trimmed of adapaters and primers when possible and of low quality base calls (not yet implemented).  All reads are then dereplicated.

## sra_map.py

The module sra_map.py is a wrapper for minimap2 and will map samples' dereplicated reads to the SAR-CoV-2 reference genome (NC_045512.2).

## sra_vc.py

The module sra_vc.py is a wrapper for SAM Refiner and will collect variant information from the mapped reads.

## sra_consensus.py

The module sra_consensus.py will generate a consensus sequence for an SRA sample based on the NT calls output and write the consensus to a sample's consensus fasta (fasta subdirectory) and a collection of consensus sequences, Consensus.tsv (working directory).

## sra_lineage.py

The module sra_lineage.py will assign lineages to a SRA samples based on the NT calls and a refererence lineage dictionary in the data subfolder.  Results are written to sample lineage tsvs and to a collection tsv.  The lineage dictionary is a plain text file.  Each line holds the informatin for a variant lineage in a tab deliminated format.  The line must start with the __unique__ name of the lineage, with the following line entries representing at least six positional mutation that defines the lineage.  Examples of defining mutations: SNPs - C10029T, dels - 22194-22196del, insertions 22205-insertGAGCCAGAA.  These definitions should conform to the mapping and variant calling performed by minimap2 and SAM Refiner to properly match.   Definitions based on other mapping/vc methods may not match.  The assignment algorithm used is customized for the SAM Refiner output.  Other methods will likely require at least reformating of vc outputs.

## sra_output_aggregate.py

The module sra_output_aggregate.py will collect sample information for polymorphisms and NT calls and add them to the tsv collection Polymorphisms.tsv and NT_Calls.tsv.


## Testing

The pipeline and its modules are tested for using pytest.  The testing scripts can be found in the tests subdirectory.  To run the tests, run pytest in the backend directory.

```bash
path/to/SHED/backend:$ pytest
```
