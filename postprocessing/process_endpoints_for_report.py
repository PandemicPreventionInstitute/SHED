"""
Three functions to process the lineage.tsv, the json and the trim.logs files
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def generate_lineage_abundance(path, folder_ext, sra_id):
    """
    Takes the lineages tsv file and outputs the abundance per lineage in a csv.
        folder_ext for this function is ".lineages.tsv"
    """

    lin_dt = []
    with open(path + "endpoints/" + sra_id + folder_ext, encoding="utf-8") as file:
        for line in file:

            one_line = line.split("\t")
            lin_dt.append(one_line)

    lineage = [x.split(" ") for x in lin_dt[2]][1]
    abundance_ = [x.split(" ") for x in lin_dt[3]][1]
    abundance = [float(x) for x in abundance_]
    lin_abun = pd.DataFrame(
        np.column_stack((lineage, abundance)), columns=("lineage", "abundance")
    )
    lin_abun["lineage"] = lin_abun["lineage"].apply(lambda row_str: row_str.strip("\n"))

    plt.figure(figsize=(7, 7))
    plt.barh(lineage, abundance)
    plt.title("Lineage abundance breakdowns for SRA_ID " + str(sra_id))
    plt.xlabel("abundance")
    plt.ylabel("lineages")

    return lin_abun.to_csv(path + sra_id + "_lin_abun.csv", index=False), plt.savefig(
        path + sra_id + "_lin_abun.png"
    )


def generate_primer_readcnt(path, folder_ext, sra_id):
    """

    Takes a trim log of a SRA and returns the primer name for each read and the count of that read.
    In the trim.log file there are other messages preceeding the actual data
    which is trimmed by this function. It is also converting the data into a
    more manageable dataframe with the two columns: primer_name, read_count

    The default folder extention for input file, folder_ext, is ".trim.
    """

    infile = path + "trim_logs/" + sra_id + folder_ext
    with open(infile, encoding="utf-8") as file:
        file = file.readlines()

    primer_read_cnts = []
    i = 0
    start = 0
    for line in file:

        ## In this file there are some other texts before the primer names and read count appears.
        ## After the appearance of the phrase "Results: \n" our required data lies.
        ## The start variable is just tracking that and stopping the iteration
        ## when black row shows up

        if start == 1:
            i += 1
            primer_read_cnts.append(line)
        if line == "Results: \n":
            start = +1
        if (line == "\n") & (len(primer_read_cnts) > 1):
            start = -1

    primer_read_list = pd.DataFrame(
        [x.split("\t") for x in primer_read_cnts][1:-1],
        columns=("primer_name", "read_count"),
    )
    primer_read_list["read_count"] = primer_read_list["read_count"].apply(
        lambda row_str: row_str.strip("\n")
    )

    plt.figure(figsize=(30, 12))
    plt.plot(primer_read_list["primer_name"], primer_read_list["read_count"])
    plt.xticks(rotation=80)
    plt.show()

    return primer_read_list.to_csv(
        path + sra_id + "_primer_readcnt.csv", index=False
    ), plt.savefig(path + sra_id + "_readdist.png")


def read_cnt_after_filter(path, folder_ext, sra_id):
    """
    Take SRA id as a string and from the .pe.json or .se.json
    outputs the number of good quality reads in that sample
    folder_ext for this function is either ".pe.json" or ".se.json"
    """

    with open(path + "qc_jsons.zip/" + sra_id + folder_ext, encoding="utf-8") as file:
        data = json.load(file)

    return data["summary"]["after_filtering"]["total_reads"]
