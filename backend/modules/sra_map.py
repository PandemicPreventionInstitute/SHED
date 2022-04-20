#!/bin/env python3

"""
Writen by Devon Gregory
This script will use minimap2 to map pre-existing collapsed reads of the SRA accession provided in
the file argument, 'SraRunTable.csv' or 'SraRunTable.txt' against the full genome of SARS-CoV-2.
Last edited on 4-20-22
todo: capture std out from mapping
    add time out
"""
import os
import sys
import time
sys.path.insert(0, os.getcwd().split("SHED")[0] + "SHED/backend/modules/")
from sra_file_parse import get_accessions, arg_parse

def map_reads(base_path: str, sra_acc: str) -> int:
    """
    Called to map collapsed fasta files for an SRA accession

    Parameters:
    base_path - path of directory where fastqs will be written in the ./fastqs/subfolder - string
    sra_acc - accession for the SRA sample - string

    Functionality:
    Uses minimap2 to perform the mapping and provide most errors

    Returns a status code. 0 for  success or pre-existing finished mapped sam
    """
    if sra_acc and isinstance(sra_acc, str):
        # check for pre-existing finished derep
        if os.path.isfile(f"{base_path}sams/{sra_acc}.sam") and not os.path.isfile(
            f"{base_path}sams/{sra_acc}.mapping.started"
        ):
            mapped_code = 0
            print(f"Mapping for {sra_acc} already completed")
        elif os.path.isfile(f"{base_path}fastas/{sra_acc}.collapsed.fa"):
            open(f"{base_path}sams/{sra_acc}.mapping.started", "w").close()
            mapped_code = os.system(
                f"conda run -n shed-back-pipe minimap2 -a {base_path}data/SARS2.fasta {base_path}fastas/{sra_acc}.collapsed.fa \
                -o {base_path}sams/{sra_acc}.sam --sam-hit-only --secondary=no"
            )
            if mapped_code == 0:
                os.remove(f"{base_path}sams/{sra_acc}.mapping.started")
        else:
            print(f"Can't find collapsed fasta for {sra_acc}")
            mapped_code = 1

    else:
        print("No SRA Accession provided for mapping")
        mapped_code = -1
    return mapped_code


if __name__ == "__main__":
    """
    Stand alone script.  Takes a filename with arguement '-i' that holds
    SRA accessions and maps pre-existing collapsed fastas for those samples
    """

    args = arg_parse()
    # check to see if files with SRA accession or meta data exist before pulling accession list
    filename = ""
    if args.file:
        filename = args.file
    elif os.path.isfile("SraRunTable.csv"):
        filename = "SraRunTable.csv"
    elif os.path.isfile("SraRunTable.txt"):
        filename = "SraRunTable.txt"
    else:
        print("No SRA accession list or metadata files found.")
    base_path = os.getcwd().split("SHED")[0] + "SHED/backend/"
    # downloads fastq files
    if filename:
        accession_list = get_accessions(args.file)
        if isinstance(accession_list, list):
            if not os.path.isdir(f"{base_path}sams/"):
                os.mkdir(f"{base_path}sams/")
            for sra_acc in accession_list:
                print(map_reads(base_path, sra_acc))
