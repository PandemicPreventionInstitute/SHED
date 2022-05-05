#!/bin/env python3

"""
Writen by Devon Gregory
This script has functions to assign variant lineages to an SRA sample based
on the nt calls.
It can be loaded as a module or run as a stand alone script. As the latter,
it parses the file provided in the command argument,
or a metadata table in the cwd, for accessions and then calls its own function.
Last edited on 5-4-22
    add time out
"""

import os
import sys

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend/modules")
from sra_file_parse import get_accessions, arg_parse


def get_lineage_dict(f_base_path: str) -> int:
    """
    Called to assemble a local dictionary for SARS-CoV-2 lineages.

    Parameters:
    f_base_path - path of directory where files will be read/written in subfolders - string

    Functionality:
    Assembles dictionary from the lineages.tsv file in the data subfolder to used to assign
    an SRA sample lineages.

    Returns the dict or a failure code.
    """
    lin_dict = {}
    try:
        with open(f"{f_base_path}/data/Lineage_dict.tsv") as dict_file:
            for line in dict_file:
                split_line = line.split("\t")
                lineage = split_line[0]
                for polymorphism in split_line[1:]:
                    if polymorphism.endswith("delATCG"):
                        positions = polymorphism.strip("del").split("-")
                        for i in range(int(position[0]), int(position[1])+1):
                            try:
                                lin_dict[i][lineage] = "-"
                            except KeyError:
                                lin_dict[i] = {lineage : "-"}
                    elif "insert" in polymorphism:
                        split_poly = polymorphism.split("-")
                        try:
                            lin_dict[int(split_poly[0])][lineage] = split_poly[1]
                        except KeyError:
                            lin_dict[int(split_poly[0])] = {lineage : split_poly[1]}
                    else:
                        try:
                            lin_dict[int(polymorphism.strip("ATCG"))][lineage] = polymorphism[-1]
                        except KeyError:
                            lin_dict[int(polymorphism.strip("ATCG"))] = {lineage : polymorphism[-1]}
    except Exception as e:
        print(f"Reading of lineage dict failed: {e}")
        return 1
    return(lin_dict)



def find_lineages(lineage_defs: dict, f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to assign lineages to an SRA sample based on the nt calls and the lineage dict passed

    Parameters:
    lineage_defs - dict of lineage's polymorphism - dict
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Parses an nt_call file to match against the defined polymorphism in the lineage dict and 
    writes the results to sample 
    
    Returns a status code. 0 for success or pre-existing finished sample lineage tsv
    """
    if f_sra_acc and isinstance(f_sra_acc, str):
        # check for pre-existing finished lineage assignments
        if os.path.isfile(f"{f_base_path}/tsvs/{f_sra_acc}.lineages.tsv"):
            lin_code = 0
            print(f"Lineage assignments for {f_sra_acc} ready completed")
        else:
            lin_match_dict = {}
            try:
                with open(
                    f"{f_base_path}/tsvs/{f_sra_acc}_nt_calls.tsv", "r"
                ) as in_file:
                    for line in in_file:
                        splitline = line.strip("\n\r").split("\t")
                        if splitline[0] == "Position":
                            try:
                                assert splitline[9] == "Total", "NT call tsv does not appear to have been generated with correct version of SAM refiner"
                            except AssertionError as e:
                                print(e)
                                return 5
                        if (
                            splitline[0].isnumeric()
                            and splitline[9].isnumeric()
                        ):
                            position = int(splitline[0])


    else:
        print("No SRA Accession provided for lineage assignment")
        lin_code = -1

    return lin_code


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
            lineage_dict = get_lineage_dict(BASE_PATH)
            for sra_acc in accession_list:
                print(find_lineages(lineage_dict, BASE_PATH, sra_acc))
