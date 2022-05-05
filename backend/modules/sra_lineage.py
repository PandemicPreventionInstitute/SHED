#!/bin/env python3

"""
Writen by Devon Gregory
This script has functions to assign variant lineages to an SRA sample based
on the nt calls.
It can be loaded as a module or run as a stand alone script. As the latter,
it parses the file provided in the command argument,
or a metadata table in the cwd, for accessions and then calls its own function.
Last edited on 5-5-22
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
                split_line = line.strip("\n\r").split("\t")
                lineage = split_line[0]
                for polymorphism in split_line[1:]:
                    if polymorphism.endswith("del"):
                        position = polymorphism.strip("del").split("-")
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
    return lin_dict

def print_lin_finds(matches_dict: dict, f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to write lineage assignments of an SRA sample based

    Parameters:
    matches_dict - dict of lineage's polymorphism matches - dict
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Determines if lineages is present in sample based on the matches_dict and prints positive
    match information to sample and collection tsvs.

    Returns a status code. 0 for success
    """
    matches = []
    write_code = 0
    if matches_dict:
        try:
            for lineage in matches_dict:
                if isinstance(lineage, str):
                    covered_positions = len(matches_dict[lineage]["values"])
                    if covered_positions > 5 and (sum(matches_dict[lineage]["values"]) / covered_positions) > .05:
                        abund_fail = 0
                        for posit_val in matches_dict[lineage]["values"]:
                            if posit_val < .05:
                                abund_fail += 1
                        if abund_fail < (.2 * covered_positions):
                            matches.append(lineage)
                            for position in matches_dict[lineage]:
                                if not position == "values":
                                    matches.append(f"{position}{matches_dict[lineage][position][0]}\t{matches_dict[lineage][position][1]}\t{matches_dict[lineage][position][2]}")
        except Exception as e:
            print(f"Lineage matching calculations failed for {f_sra_acc}: {e}")
            write_code = 3
    try:
        with open(f"{f_base_path}/tsvs/{f_sra_acc}.lineages.tsv", "w") as samp_out:
            if matches:
                for line in matches:
                    samp_out.write(line)
                    samp_out.write("\n")
            else:
                samp_out.write("No lineage matches made.")
    except Exception as e:
        print(f"Lineage match sample writing for {f_sra_acc} failed: {e}")
        write_code = 5
    try:
        with open(f"{f_base_path}/Lineages.tsv", "a+") as agg_out:
            agg_out.seek(0)
            if f"{f_sra_acc}\t" in agg_out.read():
                print(
                    f"Lineage assignment for {f_sra_acc} already in aggregate file. Not duplicating."
                )
            else:
                agg_out.write(f_sra_acc)
                agg_out.write("\n")
                if matches:
                    for line in matches:
                        agg_out.write("\t")
                        agg_out.write(line)
                        agg_out.write("\n")
                else:
                    agg_out.write("\tNo matches found")
                agg_out.write("\n")

    except Exception as e:
        print(f"Lineage match collection writing for {f_sra_acc} failed: {e}")
        write_code += 7
    return write_code

def find_lineages(lineage_defs: dict, f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to assign lineages to an SRA sample based on the nt calls and the lineage dict passed

    Parameters:
    lineage_defs - dict of lineage's polymorphism - dict
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Parses an nt_call file to match against the defined polymorphism in the lineage dict and
    calls function to write the results to sample tsv and a collection tsv

    Returns a status code. 0 for success or pre-existing finished sample lineage tsv
    """
    lin_code = 0
    if f_sra_acc and isinstance(f_sra_acc, str):
        # check for pre-existing finished lineage assignments
        if os.path.isfile(f"{f_base_path}/tsvs/{f_sra_acc}.lineages.tsv"):
            print(f"Lineage assignments for {f_sra_acc} already completed")
        else:
            lin_match_dict = {}
            try:
                with open(
                    f"{f_base_path}/tsvs/{f_sra_acc}_nt_calls.tsv", "r"
                ) as in_file:
                    nt_line_pos_dict = {"A" : 3, "T" : 4, "C" : 5, "G" : 6, "-" : 7}
                    for line in in_file:
                        splitline = line.strip("\n\r").split("\t")
                        if splitline[0] == "Position":
                            try:
                                assert splitline[9] == "Total" and splitline[3] == "A", "NT call tsv does not appear to have been generated with correct version of SAM refiner"
                            except AssertionError as e:
                                print(e)
                                return 5
                        if (
                            splitline[0].isnumeric()
                            and splitline[9].isnumeric()
                        ):
                            position = int(splitline[0])
                            if position in lineage_defs:
                                lin_match_dict[position] = splitline[9]
                                for lineage in lineage_defs[position]:
                                    if 'insert' in lineage_defs[position][lineage] and splitline[1] == "-" and lineage_defs[position][lineage].strip("insert") == splitline[10]:
                                        abund = float(splitline[12])
                                        try:
                                            lin_match_dict[lineage][position] = (lineage_defs[position][lineage], splitline[11], abund)
                                        except KeyError:
                                            lin_match_dict[lineage] = {position : (lineage_defs[position][lineage], splitline[11], abund)}
                                        try:
                                            lin_match_dict[lineage]["values"].append(abund)
                                        except KeyError:
                                            lin_match_dict[lineage]["values"] = [abund]
                                    elif not splitline[1] == "-":
                                        if 'insert' in lineage_defs[position][lineage]:
                                            try:
                                                lin_match_dict[lineage][position]
                                            except KeyError:
                                                try:
                                                    lin_match_dict[lineage][position] = (lineage_defs[position][lineage], "0", 0)
                                                except KeyError:
                                                    lin_match_dict[lineage] = {position : (lineage_defs[position][lineage], "0", 0)}
                                                try:
                                                    lin_match_dict[lineage]["values"].append(0)
                                                except KeyError:
                                                    lin_match_dict[lineage]["values"] = [0]
                                            continue
                                        count = splitline[nt_line_pos_dict[lineage_defs[position][lineage]]]
                                        abund = float(count) / int(splitline[9])
                                        try:
                                            lin_match_dict[lineage][position] = (lineage_defs[position][lineage], count, abund)
                                        except KeyError:
                                            lin_match_dict[lineage] = {position : (lineage_defs[position][lineage], count, abund)}
                                        try:
                                            lin_match_dict[lineage]["values"].append(abund)
                                        except KeyError:
                                            lin_match_dict[lineage]["values"] = [abund]
            except Exception as e:
                print(f"Unable to get lineage information for {f_sra_acc}: ({e})")
                lin_code = 1
            else:
                print_code = print_lin_finds(lin_match_dict, f_base_path, f_sra_acc)
                if not print_code == 0:
                    lin_code = print_code
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
