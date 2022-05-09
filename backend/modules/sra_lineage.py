#!/bin/env python3

"""
Writen by Devon Gregory
This script has functions to assign an SRA sample to VOC lineages based
on the nt calls.
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


def get_lineage_dict(f_base_path: str):
    """
    Called to assemble a local dictionary for SARS-CoV-2 lineages.

    Parameters:
    f_base_path - path of directory where files will be read/written in subfolders - string

    Functionality:
    Assembles dictionary from the lineages.tsv file in the data subfolder to be used to assign
    an SRA sample lineages.

    Returns the dict or a failure code.
    """
    lin_dict = {"lineages" : []}
    try:
        with open(f"{f_base_path}/data/Lineage_dict.txt") as dict_file:
            for line in dict_file:
                split_line = line.strip("\n\r").split("\t")
                lineage = split_line[0]
                if lineage in lin_dict["lineages"]:
                    print(f"Repeat lineage name {lineage}.  Skipping definition gathering for the repeat    .  Please ensure all defined lineages have unique names.")
                    continue
                lin_dict["lineages"].append(lineage)
                for polymorphism in split_line[1:]:
                    if polymorphism.endswith("del"):
                        position = polymorphism.strip("del").split("-")
                        for i in range(int(position[0]), int(position[1]) + 1):
                            try:
                                lin_dict[i][lineage] = "-"
                            except KeyError:
                                lin_dict[i] = {lineage: "-"}
                    elif "insert" in polymorphism:
                        split_poly = polymorphism.split("-")
                        try:
                            lin_dict[int(split_poly[0])][lineage] = split_poly[1]
                        except KeyError:
                            lin_dict[int(split_poly[0])] = {lineage: split_poly[1]}
                    else:
                        try:
                            lin_dict[int(polymorphism.strip("ATCG"))][
                                lineage
                            ] = polymorphism[-1]
                        except KeyError:
                            lin_dict[int(polymorphism.strip("ATCG"))] = {
                                lineage: polymorphism[-1]
                            }
    except Exception as e:
        print(f"Reading of lineage dict failed: {e}")
        return 1
    if len(lin_dict["lineages"]) == 0:
        print("No lineage definitions in definition file")
        return 2
    return lin_dict

def print_lin_finds(matches_dict: dict, f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to write lineage assignments of an SRA sample

    Parameters:
    matches_dict - dict of lineage's polymorphism matches - dict
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Determines if lineages is present in sample based checks on the matches_dict and prints positive
    match information to sample and collection tsvs.

    Returns a status code. 0 for success
    """
    matches = []
    write_code = 0
    if matches_dict:
        try:
            for lineage in matches_dict:
                if isinstance(lineage, str):
                    # determine how many defined mutations were at covered positions
                    covered_positions = len(matches_dict[lineage]["values"])
                    # determine average positive hit abundance of the covered positions
                    mean = sum(matches_dict[lineage]["values"]) / covered_positions
                    if covered_positions > 5 and mean >= 0.05:
                        # requires at least 6 positions covered and a mean abundance of defining mutations to be at least .05
                        abund_fail = 0
                        for posit_val in matches_dict[lineage]["values"]:
                            # determine how many defining mutatins have an abudance < .05
                            if posit_val < 0.05:
                                abund_fail += 1
                        if abund_fail < (0.2 * covered_positions):
                            # match check fails if 1 in 5 or more are at less than .05 abundance
                            matches.append(f"{lineage} ({mean:.2f})")
                            for position in matches_dict[lineage]:
                                if not position == "values":
                                    # collect positional mutation information for writing to output files
                                    matches.append(
                                        f"{position}{matches_dict[lineage][position][0]}\t{matches_dict[lineage][position][1]}\t{matches_dict[lineage][position][2]:.2f}"
                                    )
        except Exception as e:
            print(f"Lineage matching calculations failed for {f_sra_acc}: {e}")
            write_code = 3
        else:
            try:
                # attempts to print the sample output
                with open(
                    f"{f_base_path}/tsvs/{f_sra_acc}.lineages.tsv", "w"
                ) as samp_out:
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
                # attempts to check the aggregate output for pre-existing aggregation
                # writes to aggregate if not already present
                with open(f"{f_base_path}/Lineages.tsv", "a+") as agg_out:
                    agg_out.seek(0)
                    if f"{f_sra_acc}\n" in agg_out.read():
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
            try:
                with open(f"{f_base_path}/tsvs/{f_sra_acc}_nt_calls.tsv", "r") as in_file:
                    in_file.readline()
                    # check for correct sam refiner output format
                    second_line = in_file.readline().split("\t")
                    try:
                        assert (
                            second_line[0] == "Position" and second_line[9] == "Total" and second_line[3] == "A"
                        ), "NT call tsv does not appear to have been generated with correct version of SAM refiner"
                    except AssertionError as e:
                        print(e)
                        return 2
                    lin_match_dict = {}
                    for lineage in lineage_defs["lineages"]:
                        lin_match_dict[lineage] = {"values" : []}
                    nt_line_pos_dict = {"A": 3, "T": 4, "C": 5, "G": 6, "-": 7}
                    for line in in_file:
                        splitline = line.strip("\n\r").split("\t")
                        if splitline[0].isnumeric() and splitline[9].isnumeric():
                            # makes sure line is a position line
                            position = int(splitline[0])
                            if position in lineage_defs:
                                # if position is lineage defining get info on that defining polymorphism
                                for lineage in lineage_defs[position]:
                                    if (
                                        "insert" in lineage_defs[position][lineage]
                                        and splitline[1] == "-"
                                        and lineage_defs[position][lineage].strip(
                                            "insert"
                                        )
                                        == splitline[10]
                                    ):
                                        # handles insertion line reports
                                        abund = float(splitline[12])
                                        lin_match_dict[lineage][position] = (
                                            lineage_defs[position][lineage],
                                            splitline[11],
                                            abund,
                                        )
                                        lin_match_dict[lineage]["values"].append(
                                            abund
                                        )
                                    elif not splitline[1] == "-":
                                        # handles regular poistional line reports
                                        if "insert" in lineage_defs[position][lineage]:
                                            if not position in lin_match_dict[lineage]:
                                                # gets insertion defining info if it wasn't present
                                                lin_match_dict[lineage][
                                                    position
                                                ] = (
                                                    lineage_defs[position][lineage],
                                                    "0",
                                                    0,
                                                )
                                                lin_match_dict[lineage][
                                                    "values"
                                                ].append(0)
                                            continue
                                        # get non-insertion defining info
                                        count = splitline[
                                            nt_line_pos_dict[
                                                lineage_defs[position][lineage]
                                            ]
                                        ]
                                        abund = float(count) / int(splitline[9])
                                        lin_match_dict[lineage][position] = (
                                            lineage_defs[position][lineage],
                                            count,
                                            abund
                                        )
                                        lin_match_dict[lineage]["values"].append(
                                            abund
                                        )
            except Exception as e:
                print(f"Unable to get lineage information for {f_sra_acc}: ({e})")
                lin_code = 1
            else:
                # print if lineage defining info parsing didn't fail
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
