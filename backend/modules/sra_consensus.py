#!/bin/env python3

"""
Writen by Devon Gregory
This script has a functions to generate a consensus sequence based on a sample's
nt call output and write it to a fasta file and a collection tsv.
It can be loaded as a module or run as a stand alone script. As the latter,
it parses the file provided in the command argument,
or a metadata table in the cwd, for accessions and then calls its own function.
Last edited on 5-7-22
    add time out
"""

import os
import sys

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend/modules")
from sra_file_parse import get_accessions, arg_parse


def write_consensus(consensus: str, f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to write the consensus for an SRA accession

    Parameters:
    consensus - consensus sequence - str
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Writes consensus to a fasta in the fastas sub directory and aggregating tsv in base path

    Returns a status code. 0 for success, 3 for fasta write failure, 4 for tsv write failure
    7 for both failing
    """
    con_write_code = 0
    try:
        with open(
            f"{f_base_path}/fastas/{f_sra_acc}.consensus.fasta", "w"
        ) as out_file:
            out_file.write(f">{f_sra_acc}_consensus\n")
            out_file.write(consensus)
            out_file.write("\n")
    except Exception as e:
        print(f"Failed to write consensus fasta for {f_sra_acc}: {e}")
        con_write_code += 3
    try:
        with open(f"{f_base_path}/Consensus.tsv", "a+") as ag_file:
            ag_file.seek(0)
            if f"{f_sra_acc}\t" in ag_file.read():
                print(
                    f"Consensus for {f_sra_acc} already in aggregate file. Not duplicating."
                )
            else:
                ag_file.write(f"{f_sra_acc}\t{consensus}\n")
    except Exception as e:
        print(
            f"Failed to write consensus to aggregate file for {f_sra_acc}: {e}"
        )
        con_write_code += 4
    return con_write_code


def gen_consensus(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to generate a consensus for an SRA accession based on the nt call output of sam refiner

    Parameters:
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Parses an nt_call file to gather a consensus based on >= 10 coverage and >= .6 abundance.
    Calls function to write consensus to a fasta in the fastas sub directory and aggregating tsv in base path

    Returns a status code. 0 for success or pre-existing finished consensus fasta
    """
    if f_sra_acc and isinstance(f_sra_acc, str):
        # check for pre-existing finished consensus
        if os.path.isfile(f"{f_base_path}/fastas/{f_sra_acc}.consensus.fasta"):
            consensus_code = 0
            print(f"Consensus generation for {f_sra_acc} already completed")
        else:
            consensus = ""
            try:
                with open(
                    f"{f_base_path}/tsvs/{f_sra_acc}_nt_calls.tsv", "r"
                ) as in_file:
                    in_file.readline()
                    second_line = in_file.readline().split("\t")
                    try:
                        assert (
                            second_line[0] == "Position"
                            and second_line[9] == "Total"
                            and second_line[3] == "A"
                        ), "NT calls tsv has incorrect headers. Likely in incorrect format."

                    except AssertionError as e:
                        print(e)
                        return 5

                    for line in in_file:
                        splitline = line.strip("\n\r").split("\t")
                        last_position = 0
                        if (
                            splitline[0].isnumeric()
                            and splitline[9].isnumeric()
                        ):
                            position = int(splitline[0])
                            if last_position != 0 and (
                                position - last_position > 1
                            ):
                                # filling gaps with Ns
                                while position - last_position > 1:
                                    consensus += "N"
                                    last_position += 1
                            if (int(splitline[9]) >= 10) and (
                                float(splitline[12]) >= 0.6
                            ):
                                if splitline[1] == "-":
                                    # catching insertions
                                    consensus += splitline[10]
                                elif not splitline[10] == "-":
                                    # catching consensus non-dels
                                    consensus += splitline[10]
                            elif not splitline[1] == "-":
                                consensus += "N"
                            last_position = position
            except Exception as e:
                print(f"Error reading nt calls file for {f_sra_acc}: {e}")
                consensus_code = 1
            else:
                if consensus and consensus.strip("N"):
                    consensus_code = write_consensus(
                        consensus, f_base_path, f_sra_acc
                    )
                else:
                    print(
                        f"Consensus could not be generated for {f_sra_acc}. No positions with >= 10 coverage and a nt at >= 60% of calls"
                    )
                    consensus_code = 2

    else:
        print("No SRA Accession provided for consensus generation")
        consensus_code = -1

    return consensus_code


if __name__ == "__main__":
    """
    Stand alone script.  Takes a file name with arguement '-i' that holds
    SRA accessions and makes a consensus based on the nt call for those samples
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
    BASE_PATH = os.getcwd()
    # downloads fastq files
    if file_name:
        accession_list = get_accessions(args.file)
        if isinstance(accession_list, list):
            if not os.path.isdir(f"{BASE_PATH}/fastas"):
                os.mkdir(f"{BASE_PATH}/fastas")
            for sra_acc in accession_list:
                print(gen_consensus(BASE_PATH, sra_acc))
