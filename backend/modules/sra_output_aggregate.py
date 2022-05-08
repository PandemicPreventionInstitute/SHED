#!/bin/env python3

"""
Writen by Devon Gregory
This script has functions to aggregate the information in individual samples
tsvs into a single tsv in the base path directory.
It can be loaded as a module or run as a stand alone script. As the latter,
it parses the file provided in the command argument,
or a metadata table in the cwd, for accessions and then calls its own function.
Last edited on 5-8-22
    add time out
"""

import os
import sys

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend/modules")
from sra_file_parse import get_accessions, arg_parse

def agg_nt_calls(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to add nt call info for an SRA accession to the collection tsv

    Parameters:
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Writes nt call info to the NT_Calls.tsv if it doesn't already hold that accession's info

    Returns a status code. 0 for success
    """
    nt_calls = []
    nt_agg_code = 0
    try:
        with open(f"{f_base_path}/NT_Calls.tsv", "r") as sra_check:
            if f"{f_sra_acc}(" in sra_check.read():
                print(f"{f_sra_acc} already in NT_Calls.tsv.  Not overwriting")
                return(0)
    except FileNotFoundError:
        pass
    try:
        with open(
            f"{f_base_path}/tsvs/{f_sra_acc}_nt_calls.tsv", "r"
        ) as in_file:
            samp_info = in_file.readline().split("/")[-1]
            if samp_info:
                nt_calls.append(samp_info)
            for line in in_file:
                split_line = line.split("\t")
                nt_calls.append(split_line[0]+"\t"+"\t".join(split_line[3:11])+"\n")
    except Exception as e:
        print(f"Error reading {f_sra_acc} nt call file for aggregationg: {e}")
        nt_agg_code = 1
    else:
        if nt_calls:
            try:
                with open(f"{f_base_path}/NT_Calls.tsv", "a") as out_file:
                    out_file.writelines(nt_calls)
                    out_file.writelines("\n")
            except Exception as e:
                print(f"Error writing {f_sra_acc} nt calls to aggregate: {e}")
                nt_agg_code = 3
        else:
            print(f"No NT Call data in nt call file for {f_sra_acc}")
            nt_agg_code = 2
    return nt_agg_code

def agg_vars(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to add covariant info for an SRA accession to the collection tsv

    Parameters:
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Writes covariant info to the Polymorphs.tsv if it doesn't already hold that accession's info

    Returns a status code. 0 for success
    """
    variations = []
    var_agg_code = 0
    try:
        with open(f"{f_base_path}/Polymorphs.tsv", "r") as sra_check:
            if f"{f_sra_acc}(" in sra_check.read():
                print(f"{f_sra_acc} already in Polymorphs tsv.  Not overwriting")
                return(0)
    except FileNotFoundError:
        pass
    try:
        with open(
            f"{f_base_path}/tsvs/{f_sra_acc}_AA_covars.tsv", "r"
        ) as in_file:
            samp_info = in_file.readline().split("/")[-1]
            if samp_info:
                variations.append(samp_info)
            for line in in_file:
                split_line = line.split("\t")
                if split_line[1].isnumeric():
                    variations.append(line)
    except Exception as e:
        print(f"Error reading {f_sra_acc} covars file for aggregationg: {e}")
        var_agg_code = 1
    else:
        try:
            with open(f"{f_base_path}/Polymorphs.tsv", "a") as out_file:
                out_file.writelines(variations)
                out_file.writelines("\n")
        except Exception as e:
            print(f"Error writing {f_sra_acc} polymorphisms to aggregate: {e}")
            var_agg_code = 2
    return var_agg_code


if __name__ == "__main__":
    """
    Stand alone script.  Takes a file name with arguement '-i' that holds
    SRA accessions and aggregates data from those sample's tsvs
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
            for sra_acc in accession_list:
                print(agg_nt_calls(BASE_PATH, sra_acc))
                print(agg_vars(BASE_PATH, sra_acc))
