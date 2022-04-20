#!/bin/env python3

"""
Writen by Devon Gregory
This script will read through a file to obtain SRA accessions and pass them to the caller
Last edited on 4-19-22
"""

import os
import argparse


def arg_parse():
    """parses file argument"""
    parser = argparse.ArgumentParser(
        description="File containing SRA accessions to be fetched.  Accessions to be at the start of a newline and separated from the remaining line with either a comma or tab"
    )
    parser.add_argument(
        "-i",
        "--file",
        type=str,
        dest="file",
        default="",
        help="SRA accession list or metadata table",
    )
    args = parser.parse_args()
    return args


def get_accessions(filename: str) -> list:
    """
    Called to get SRA accessions from the provided file and return them as a list to the caller

    Parameters:
    filename - name of the file to get the accessions from. - string

    Functionality:
        Goes through each line of the file and pulls the accession from the start.

    Returns a list of validly formated accessions, or an error code
    """
    try:
        run_list_fh = open(filename, "r")
    except Exception as e:
        print(e)
        return 1
    else:
        accession_list = []
        for line in run_list_fh:
            sra_acc = line.split(",")[0]
            try:
                # check if a validish accession was found
                # requires the format 'S/ERR#' as the first entry in a comma seperated line
                assert "," in line, "Not in comma separated format"
                assert sra_acc.startswith("SRR") or sra_acc.startswith(
                    "ERR"
                ), "Incorrect prefix"
                assert sra_acc.split("RR")[1].isnumeric(), "Non-numeric listing"
                assert len(sra_acc.split("RR")) == 2, "Bad format"
            except AssertionError as e:
                print(
                    sra_acc + " does not appear to be a valid SRA accession: " + str(e)
                )
            else:
                accession_list.append(sra_acc)
        run_list_fh.close()
        if not accession_list:
            print("No SRA Accessions were found.")
            return 2
        return accession_list


def find_fastqs(base_path: str, sra_acc: str) -> tuple:
    """
    Called to discover the pre-existing fastq files that have already been written for a SRA accession

    Parameters:
    base_path - path of directory where fastqs should have been written in the ./fastqs/ subfolder - string
    sra_acc - accession for the SRA sample - string

    Functionality:
        Checks the fastqs subfolder for single or paired fastq files for the accession in the specified directory.

    Returns a tuple of the found fastqs if the aren't a mismatch of single and paired reads, otherwise returns error code (1)
    """
    file_list = []
    if os.path.isfile(f"{base_path}fastqs/{sra_acc}_1.fastq.gz"):
        file_list.append(f"{base_path}fastqs/{sra_acc}_1.fastq.gz")
    if os.path.isfile(f"{base_path}fastqs/{sra_acc}_2.fastq.gz"):
        file_list.append(f"{base_path}fastqs/{sra_acc}_2.fastq.gz")
    if os.path.isfile(f"{base_path}fastqs/{sra_acc}.fastq.gz"):
        file_list.append(f"{base_path}fastqs/{sra_acc}.fastq.gz")
    if len(file_list) > 1:
        if not f"{sra_acc}_2.fastq" in file_list[1] or len(file_list) > 3:
            print(
                f"Mismatch of single and paired fastq files for {sra_acc}, please remove incorrect files."
            )
            return 1
    return tuple(file_list)


if __name__ == "__main__":
    """Stand alone script.  Takes a filename with arguement '-i' that holds SRA accessions and prints them, discovers raw fastqs and processing progress"""
    args = arg_parse()
    base_path = os.getcwd().split("SHED")[0] + "SHED/backend/"
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
    if filename:
        for sra_acc in get_accessions(filename):
            print(sra_acc)
            print(find_fastqs(base_path, sra_acc))
