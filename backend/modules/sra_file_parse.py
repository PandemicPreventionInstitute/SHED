#!/bin/env python3

"""
Writen by Devon Gregory
This script has functions to parse command line arguments,
read through a file to obtain SRA accessions and pass them to the caller
and find pre-existing fastq for an SRA accession, returning them as a tuple.
It can be loaded as a module or run as a stand alone script. As the latter,
it parses the file provided in the command argument,
or a metadata table in the cwd, for accessions and then calls its own functions.
Last edited on 5-2-22
"""

import os
import argparse


def arg_parse():
    """parses command arguments"""
    parser = argparse.ArgumentParser(
        description="SRA accession processing."
    )
    parser.add_argument(
        "-i",
        "--file",
        type=str,
        dest="file",
        default="",
        help="SRA accession list or metadata table.  Accessions to be at the start of a newline and separated from the remaining line with a comma",
    )
    
    return parser.parse_args()


def get_accessions(f_file_name: str) -> list:
    """
    Called to get SRA accessions from the provided file and return them as a list to the caller

    Parameters:
    f_file_name - name of the file to get the accessions from. - string

    Functionality:
        Goes through each line of the file and pulls the accession from the start.

    Returns a list of validly formated accessions, or an error code
    """
    try:
        run_list_fh = open(f_file_name, "r")
    except Exception as e:
        print(e)
        return 1
    else:
        accession_list = []
        for line in run_list_fh:
            check_sra_acc = line.split(",")[0]
            try:
                # check if a validish accession was found
                # requires the format 'S/ERR#' as the first entry in a comma seperated line
                assert "," in line, "Not in comma separated format"
                assert check_sra_acc.startswith("SRR") or check_sra_acc.startswith(
                    "ERR"
                ), "Incorrect prefix"
                assert check_sra_acc.split("RR")[1].isnumeric(), "Non-numeric listing"
                assert len(check_sra_acc.split("RR")) == 2, "Bad format"
            except AssertionError as e:
                print(
                    check_sra_acc
                    + " does not appear to be a valid SRA accession: "
                    + str(e)
                )
            else:
                accession_list.append(check_sra_acc)
        run_list_fh.close()
        if not accession_list:
            print("No SRA Accessions were found.")
            return 2
        return accession_list


def find_fastqs(f_base_path: str, f_sra_acc: str) -> tuple:
    """
    Called to discover the pre-existing fastq files that have already been written for a SRA accession

    Parameters:
    f_base_path - path of directory where fastqs should have been written in the ./fastqs/ subfolder - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
        Checks the fastqs subfolder for single or paired fastq files for the accession in the specified directory.

    Returns a tuple of the found fastqs if the aren't a mismatch of single and paired reads, otherwise returns error code (1)
    """
    file_list = []
    if os.path.isfile(f"{f_base_path}/fastqs/{f_sra_acc}_1.fastq.gz"):
        file_list.append(f"{f_base_path}/fastqs/{f_sra_acc}_1.fastq.gz")
    if os.path.isfile(f"{f_base_path}/fastqs/{f_sra_acc}_2.fastq.gz"):
        file_list.append(f"{f_base_path}/fastqs/{f_sra_acc}_2.fastq.gz")
    if os.path.isfile(f"{f_base_path}fastqs/{f_sra_acc}.fastq.gz"):
        file_list.append(f"{f_base_path}/fastqs/{f_sra_acc}.fastq.gz")
    if len(file_list) > 1:
        if not f"{f_sra_acc}_2.fastq" in file_list[1] or len(file_list) > 3:
            print(
                f"Mismatch of single and paired fastq files for {f_sra_acc}, please remove incorrect files."
            )
            return 1
    return tuple(file_list)


if __name__ == "__main__":
    """Stand alone script.  Takes a file name with arguement '-i' that holds SRA accessions and prints them, discovers raw fastqs"""
    args = arg_parse()
    BASE_PATH = os.getcwd()
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
    if file_name:
        for sra_acc in get_accessions(file_name):
            print(sra_acc)
            print(find_fastqs(BASE_PATH, sra_acc))
