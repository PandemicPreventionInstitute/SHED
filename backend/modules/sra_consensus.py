#!/bin/env python3

"""
Writen by Devon Gregory
This script has a function to generate a consensus sequence in a fasta file based
 on the nt call output from sam refiner for a SRA accession
It can be loaded as a module or run as a stand alone script. As the latter,
it parses the file provided in the command argument,
or a metadata table in the cwd, for accessions and then calls its own function.
Last edited on 5-1-22
    add time out
"""

import os
import sys

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend/modules/")
from sra_file_parse import get_accessions, arg_parse

def gen_consensus(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to generate a consensus for an SRA accession based on the nt call output of sam refiner

    Parameters:
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Parses an nt_call file to gather a consensus based on >= 10 coverage and >= .6 abundance.
    Writen to a fasta in the fastas sub directory

    Returns a status code. 0 for success or pre-existing finished consensus fasta
    """
    if f_sra_acc and isinstance(f_sra_acc, str):
        # check for pre-existing finished consensus
        if os.path.isfile(f"{f_base_path}fastas/{f_sra_acc}.consensus.fasta"):
            consensus_code = 0
            print(f"Consensus generation for {f_sra_acc} already completed")
        elif os.path.isfile(f"{f_base_path}tsvs/{f_sra_acc}_nt_calls.tsv"):
            consensus = {}
            with open(f"{f_base_path}tsvs/{f_sra_acc}_nt_calls.tsv", "r") as in_file:
                for line in in_file:
                    splitline = line.strip("\n\r").split("\t")
                    if splitline[0].isnumeric():
                        if (int(splitline[9]) >= 10) and ( float(splitline[12]) >= .6):
                            position = int(splitline[0])
                            if splitline[1] == "-":
                                consensus[position - .5] = splitline[10]
                            else:
                                consensus[position] = splitline[10]
            if consensus:
                with open(f"{f_base_path}fastas/{f_sra_acc}.consensus.fasta", "w") as out_file:
                    out_file.write(f">{f_sra_acc}_consensus\n")
                    last_position = 0
                    # sorted_positions = sort(consensus.keys())
                    for position in consensus:
                        if last_position != 0 and (position-last_position > 1):
                            while position-last_position > 1:
                                out_file.write("N")
                                last_position += 1
                        if consensus[position] != '-':
                            out_file.write(f"{consensus[position]}")
                        last_position = position
                    out_file.write("\n")
                consensus_code = 0
            else:
                print(f"Consensus could not be generated for {f_sra_acc}. No positions with >= 10 coverage and a nt at >= 60% of calls")
                consensus_code = 2
        else:
            print(f"Can't find nt call file for {f_sra_acc}")
            consensus_code = 1

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
    BASE_PATH = os.getcwd().split("SHED")[0] + "SHED/backend/"
    # downloads fastq files
    if file_name:
        accession_list = get_accessions(args.file)
        if isinstance(accession_list, list):
            if not os.path.isdir(f"{BASE_PATH}fastas/"):
                os.mkdir(f"{BASE_PATH}fastas/")
            for sra_acc in accession_list:
                print(gen_consensus(BASE_PATH, sra_acc))
