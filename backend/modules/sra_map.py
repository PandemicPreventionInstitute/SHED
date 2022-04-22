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

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend/modules/")
from sra_file_parse import get_accessions, arg_parse


def map_reads(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to map collapsed fasta files for an SRA accession

    Parameters:
    f_base_path - path of directory where fastqs will be written in the ./fastqs/subfolder - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Uses minimap2 to perform the mapping and provide most errors

    Returns a status code. 0 for  success or pre-existing finished mapped sam
    """
    if f_sra_acc and isinstance(f_sra_acc, str):
        # check for pre-existing finished derep
        if os.path.isfile(
            f"{f_base_path}sams/{f_sra_acc}.sam"
        ) and not os.path.isfile(f"{f_base_path}sams/{f_sra_acc}.mapping.started"):
            mapped_code = 0
            print(f"Mapping for {f_sra_acc} already completed")
        elif os.path.isfile(f"{f_base_path}fastas/{f_sra_acc}.collapsed.fa"):
            open(f"{f_base_path}sams/{f_sra_acc}.mapping.started", "w").close()
            mapped_code = os.system(
                f"conda run -n shed-back-pipe minimap2 -a {f_base_path}data/SARS2.fasta {f_base_path}fastas/{f_sra_acc}.collapsed.fa \
                -o {f_base_path}sams/{f_sra_acc}.sam --sam-hit-only --secondary=no"
            )
            if mapped_code == 0:
                os.remove(f"{f_base_path}sams/{f_sra_acc}.mapping.started")
        else:
            print(f"Can't find collapsed fasta for {f_sra_acc}")
            mapped_code = 1

    else:
        print("No SRA Accession provided for mapping")
        mapped_code = -1
    return mapped_code


if __name__ == "__main__":
    """
    Stand alone script.  Takes a file name with arguement '-i' that holds
    SRA accessions and maps pre-existing collapsed fastas for those samples
    """

    args = arg_parse()
    # check to see if files with SRA accession or meta data exist before pulling accession list
    file_name = ""
    if args.file:
        file_name = args.file
    elif os.path.isfile("SraRunTable.csv"):
        file_name = "SraRunTable.csv"
    elif os.path.isfile("SraRunTable.txt"):
        file_name = "SraRunTable.txt"
    else:
        print("No SRA accession list or metadata files found.")
    BASE_PATH = os.getcwd().split("SHED")[0] + "SHED/backend/"
    # downloads fastq files
    if file_name:
        accession_list = get_accessions(args.file)
        if isinstance(accession_list, list):
            if not os.path.isdir(f"{BASE_PATH}sams/"):
                os.mkdir(f"{BASE_PATH}sams/")
            for sra_acc in accession_list:
                print(map_reads(BASE_PATH, sra_acc))
