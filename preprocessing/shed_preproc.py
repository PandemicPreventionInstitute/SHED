"""
Three functions to process the lineage.tsv, the json and the trim.logs files
"""

import json
import pandas as pd
import numpy as np


def generate_lineage_abundance(path, folder_ext, sra_id):
    """
    Takes the lineages tsv file and outputs the abundance per lineage in a csv
        folder_ext for this function is ".lineages.tsv"
    """
    lin_dt = []
    with open(path + "endpoints/" + sra_id + folder_ext, encoding="utf-8") as file:
        for line in file:

            one_line = line.split("\t")
            lin_dt.append(one_line)

    lineage = [x.split(" ") for x in lin_dt[2]][1]
    abundance = [x.split(" ") for x in lin_dt[3]][1]
    lin_abun = pd.DataFrame(
        np.column_stack((lineage, abundance)), columns=("lineage", "abundance")
    )
    lin_abun["lineage"] = lin_abun["lineage"].apply(lambda row_str: row_str.strip("\n"))

    return lin_abun.to_csv(path + sra_id + "_lin_abun.csv", index=False)


def generate_primer_readcnt(path, folder_ext, sra_id):
    """

    Takes a trim log of a SRA and returns the primer name for each read and the count of that read
    folder_ext for this function is ".trim.log"
    """

    infile = path + "trim_logs/" + sra_id + folder_ext  ## need to change
    with open(infile, encoding="utf-8") as file:
        file = file.readlines()

    primer_read_cnts = []
    i = 0
    start = 0
    for line in file:

        if start == 1:
            i += 1
            primer_read_cnts.append(line)
        if line == "Results: \n":
            start = start + 1
        if (line == "\n") & (len(primer_read_cnts) > 1):
            start = start - 1

    primer_read_list = pd.DataFrame(
        [x.split("\t") for x in primer_read_cnts][1:-1],
        columns=("Primer name", "Read count"),
    )
    primer_read_list["Read count"] = primer_read_list["Read count"].apply(
        lambda row_str: row_str.strip("\n")
    )

    return primer_read_list.to_csv(path + sra_id + "_primer_readcnt.csv", index=False)


def read_cnt_after_filter(path, folder_ext, sra_id):
    """
    Take SRA id as a string and from the .pe.json or .se.json
    outputs the number of good quality reads in that sample
    folder_ext for this function is either ".pe.json" or ".se.json"
    """

    with open(path + "qc_jsons.zip/" + sra_id + folder_ext, encoding="utf-8") as file:
        data = json.load(file)

    return data["summary"]["after_filtering"]["total_reads"]
