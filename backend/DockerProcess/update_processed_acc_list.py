"""
Written by Devon Gregory
This script collects which SRA accessions have been processed and writes them to a file
Last edited on 7-28-23
"""

import os

processed_sra_list = []

# gets accessions that failed qc
if os.path.isdir("sams"):
    for file in os.listdir("sams"):
        if file.endswith(".qc.failed"):
            processed_sra_list.append(file)

# gets successfully processed accessions
if os.path.isdir("endpoints"):
    for file in os.listdir("endpoints"):
        if file.endswith(".finished"):
            processed_sra_list.append(file)

if processed_sra_list:

    with open("processed_SRA_Accessions.txt", "a") as list_fh:
        for acc in processed_sra_list:
            list_fh.write(f"{acc}\n")