#!/bin/env python3

"""
Writen by Devon Gregory
This script has a function to download fastq files from NCBI SRA for provided accessions.
The fastq files will allow further analysis by bioinformatics pipelines.
It can be loaded as a module or run as a stand alone script. As the latter,
it parses the file provided in the command argument,
or a metadata table in the cwd, for accessions and then calls its own function.
Last edited on 5-1-22
todo: capture std out from fetch
    add time out
"""
import os
import sys
import time

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend/modules/")
from sra_file_parse import find_fastqs, get_accessions, arg_parse


def get_fastqs(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to download fastq files for a SRA accession

    Parameters:
    f_base_path - path of directory where fastqs will be written in the ./fastqs/ subfolder - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Uses NCBI's SRA toolkit to download SRA sample fastq files for processing
    prefetch downloads a compressed SRA format
    fasterq-dump writes fastqs files

    Relies on SRA toolkit to handle their own functionality and erros for the most part.
    Toolkit error codes:
        0 - system call executed w/o error,
        2 - run interuption,
        768 - prefetch can't connect or accession not found,
        16384 dump can't connect,
        32512 - program not found,
        If connection is initially present but lost, there does not seem
        to be a timely timeout built into either prefetch or dump.

    Returns the two error codes on completion for the caller to decide how to handle
    after printing a statement regarding success or failure of fetching
    """
    if f_sra_acc and isinstance(f_sra_acc, str):
        fastq_files = find_fastqs(f_base_path, f_sra_acc)
        if (
            os.path.isfile(f"{f_base_path}fastqs/{f_sra_acc}.fetch.started")
            or (not fastq_files)
            or (not isinstance(fastq_files, tuple))
        ):
            open(f"{f_base_path}fastqs/{f_sra_acc}.fetch.started", "w").close()
            prefetch_code = os.system(
                f"prefetch {f_sra_acc} -O {f_base_path}SRAs/"
            )
            time.sleep(0.5)
            fastq_dump_code = os.system(
                f"fastq-dump {f_sra_acc} --gzip --split-3 -O {f_base_path}fastqs/"
            )
            if prefetch_code + fastq_dump_code == 0:
                # no errors reported by toolkit
                os.remove(f"{f_base_path}fastqs/{f_sra_acc}.fetch.started")
                print(f"{f_sra_acc} fastq files written to {f_base_path}/fastqs/ ")
            elif fastq_dump_code == 2:
                # only if processes are actually killed I think
                print("get_fastqs interupted.")
            elif prefetch_code == 2 and fastq_dump_code == 0:
                print("prefetch interupted, but fastq dump was successful.")
            elif prefetch_code == 768:
                if fastq_dump_code == 768:
                    print(
                        "SRA accession was not found by SRA Toolkit.  Please verify."
                    )
                elif fastq_dump_code == 16384:
                    print(
                        "Can not connect to NCBI SRA.  Please verify internet connection and \
                            restart.  If connection continues to fail,\
                            NCBI may be down, try again later."
                    )
                elif fastq_dump_code == 0:
                    print("prefetch failed, but fastq dump was successful.")
                else:
                    print(
                        "prefetch failed and unknown error for fastq_dump: "
                        + fastq_dump_code
                    )
            elif prefetch_code == 32512 or fastq_dump_code == 32512:
                print(
                    "NCBI SRA Toolkit not properly installed.  Please make sure it is installed and executable from the command line"
                )
            else:
                print(
                    "unknown errors: "
                    + str(prefetch_code)
                    + " "
                    + str(fastq_dump_code)
                )
            return (prefetch_code, fastq_dump_code)
        return (0, 0)
    print("No SRA Accession provided for fetching")
    return -1


if __name__ == "__main__":
    """
    Stand alone script.  Takes a filename with arguement '-i' that holds
    SRA accessions and downloads fastqs for those samples
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
            if not os.path.isdir(f"{BASE_PATH}fastqs/"):
                os.mkdir(f"{BASE_PATH}fastqs/")
            for sra_acc in accession_list:
                fetch_code = get_fastqs(BASE_PATH, sra_acc)
                if fetch_code != (0, 0):
                    print(f"get_fastqs failed for {sra_acc}. {fetch_code}")
                else:
                    print(f"Fastqs retrieved for {sra_acc}.")
        else:
            print("Retrieval of SRA accessions from file failed")
