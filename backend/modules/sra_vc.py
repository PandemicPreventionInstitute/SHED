#!/bin/env python3

"""
Writen by Devon Gregory
This script will use SAM Refiner to call SARS-CoV-2 variants using the pre-existing
sams of the SRA accession provided in the file argument, 'SraRunTable.csv' or 'SraRunTable.txt'.
Last edited on 4-22-22
    add time out
    add no sam result check
"""
import os
import sys
import time

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend/modules/")
from sra_file_parse import get_accessions, arg_parse


def vc_sams(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to call variants using sam files for an SRA accession

    Parameters:
    f_base_path - path of directory where fastqs will be written in the ./fastqs/subfolder - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Uses SAM Refiner to perform the mapping and provide most errors

    Returns a status code. 0 for  success or pre-existing finished mapped sam
    """
    if f_sra_acc and isinstance(f_sra_acc, str):
        # check for pre-existing finished derep
        if (
            os.path.isfile(f"{f_base_path}tsvs/{f_sra_acc}_nt_calls.tsv")
            and os.path.isfile(f"{f_base_path}tsvs/{f_sra_acc}_covars.tsv")
            and not os.path.isfile(
                f"{f_base_path}tsvs/{f_sra_acc}.vcalling.started"
            )
        ):
            vc_code = 0
            print(f"Variant calling for {f_sra_acc} already completed")
        elif os.path.isfile(f"{f_base_path}sams/{f_sra_acc}.sam"):
            open(f"{f_base_path}tsvs/{f_sra_acc}.vcalling.started", "w").close()
            # currently uses threshholds of a min count of 5 and min abundance of .03 for variant reports
            # --max_covar can be increased to report cosegregating variations, at the cost of processing and storage
            vc_code = os.system(
                f"python3 {f_base_path}SAM_Refiner.py -r {f_base_path}data/SARS2.gb -S {f_base_path}sams/{f_sra_acc}.sam \
                    --wgs 1 --collect 0 --seq 0 --indel 0 --max_covar 1 --min_count 5 --min_samp_abund 0.03 \
                    --ntabund 0 --ntcover 1 --ntvar 1 --AAcentered 1"
            )
            if vc_code == 0:
                os.remove(f"{f_base_path}tsvs/{f_sra_acc}.vcalling.started")
            os.system(f"mv {f_base_path}sams/{f_sra_acc}*.tsv {f_base_path}/tsvs/")
        else:
            print(f"Can't find sam for {f_sra_acc}")
            vc_code = 1
    else:
        print("No SRA Accession provided for variant calling")
        vc_code = -1
    return vc_code


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
            if not os.path.isdir(f"{BASE_PATH}tsvs/"):
                os.mkdir(f"{BASE_PATH}tsvs/")
            for sra_acc in accession_list:
                print(vc_sams(BASE_PATH, sra_acc))
