"""
Three functions to process the lineage.tsv, the json and the trim.logs files
"""

import pandas as pd
import numpy as np


def generate_lineage_abundance(path, sra_id):
    """
    Takes the lineages tsv file and outputs the abundance per lineage in a csv
        folder_ext for this function is ".lineages.tsv"
    """

    lin_dt = []
    with open(path + sra_id + ".lineages.tsv", encoding="utf-8") as file:
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
    try:
        lin_abun.to_csv(path + sra_id + "_lin_abun.csv", index=False)
        return 0
    except OSError as error:
        print(error)
        return 1
