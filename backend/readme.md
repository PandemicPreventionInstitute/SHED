# SHED Backend Pipeline

This folder contains the scripts and tests for the backend bioinformatics pipeline for SHED.  This pipeline will query NCBI's SRA to obtains sample metadata (saved with a timestamp tag) and then download and process the raw sequencing data.  The pipeline uses snakemake.  Please make sure [snakemake 7.8+](https://snakemake.readthedocs.io/en/stable/) and [Miniconda](https://docs.conda.io/en/latest/miniconda.html) are installed.  To run the pipeline use the command:
```bash
$ bash pipeline.sh
```
The first run may require significant additional processing time for snakemake to download and build environments for the pipeline's dependancies.  The pipeline requires and will install:
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
To insure the correct query pattern, you may wish to run the query with [NCBI's web interface](https://www.ncbi.nlm.nih.gov/sra) and copy the string from the resulting url.  SRA samples that have already been downloaded and processing will not be reprocessed.  To reprocess sample from a new query, change the config.yaml:
```
    reprocess:
        True
```
Any samples that aren't found by NCBI's SRA Tools prefetch aren't processed further and a file is written to the SRAs/ directory indicating a bad accession.


## Testing
## not yet implimented
The pipeline and its modules are tested for using pytest.  The testing scripts can be found in the tests subdirectory.  To run the tests, run pytest in the backend directory.

```bash
path/to/SHED/backend:$ pytest
```
