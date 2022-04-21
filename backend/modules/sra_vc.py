#!/bin/env python3

"""
Writen by Devon Gregory
This script will use SAM Refiner to call SARS-CoV-2 variants using the pre-existing
sams of the SRA accession provided in the file argument, 'SraRunTable.csv' or 'SraRunTable.txt'.
Last edited on 4-20-22
    add time out
    add no sam result check
"""
import os
import sys
import time

sys.path.insert(0, os.getcwd().split("SHED")[0] + "SHED/backend/modules/")
from sra_file_parse import get_accessions, arg_parse


def vc_sams(base_path: str, sra_acc: str) -> int:
    """
    Called to call variants using sam files for an SRA accession

    Parameters:
    base_path - path of directory where fastqs will be written in the ./fastqs/subfolder - string
    sra_acc - accession for the SRA sample - string

    Functionality:
    Uses SAM Refiner to perform the mapping and provide most errors

    Returns a status code. 0 for  success or pre-existing finished mapped sam
    """
    if sra_acc and isinstance(sra_acc, str):
        # check for pre-existing finished derep
        if (
            os.path.isfile(f"{base_path}tsvs/{sra_acc}_nt_calls.tsv")
            and os.path.isfile(f"{base_path}tsvs/{sra_acc}_covars.tsv")
            and not os.path.isfile(
                f"{base_path}tsvs/{sra_acc}.vcalling.started"
            )
        ):
            vc_code = 0
            print(f"Variant calling for {sra_acc} already completed")
        elif os.path.isfile(f"{base_path}sams/{sra_acc}.sam"):
            open(f"{base_path}tsvs/{sra_acc}.vcalling.started", "w").close()
            # currently uses threshholds of a min count of 5 and min abundance of .03 for variant reports
            vc_code = os.system(
                f"python3 {base_path}SAM_Refiner.py -r {base_path}data/SARS2.gb -S {base_path}sams/{sra_acc}.sam \
                    --wgs 1 --collect 0 --seq 0 --indel 0 --max_covar 1 --min_count 5 --min_samp_abund 0.03 \
                    --ntabund 0 --ntcover 1 --ntvar 1 --AAcentered 1"
            )
            if vc_code == 0:
                os.remove(f"{base_path}tsvs/{sra_acc}.vcalling.started")
            os.system(f"mv {base_path}sams/{sra_acc}*.tsv {base_path}/tsvs/")
        else:
            print(f"Can't find sam for {sra_acc}")
            vc_code = 1
    else:
        print("No SRA Accession provided for variant calling")
        vc_code = -1
    return vc_code


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
            if not os.path.isdir(f"{base_path}tsvs/"):
                os.mkdir(f"{base_path}tsvs/")
            for sra_acc in accession_list:
                print(vc_sams(base_path, sra_acc))
