#!/bin/env python3

"""
Writen by Devon Gregory
This is the wrapper script for the pipeline modules.
Last edited on 4-22-22
todo:  add remaining modules
        add arguments for ignoring progress, passing file for SRA data, setting paths and ...
"""
import os
import sys
# import argparse  # will use

# import modules.sra_query as sra_query# we need to decide on the method for handling queries
from modules import sra_file_parse
from modules import sra_fetch
from modules import sra_preproc
from modules import sra_map
from modules import sra_vc
# import modules.sra_postproc as sra_postproc

# sra_query.querying()
# get accession based on file from eventual query function
accession_list = sra_file_parse.get_accessions("TestSraList.txt")
if not (isinstance(accession_list, list) and accession_list):
    print(f"failure at accession list aquisition ({accession_list})")
    sys.exit()
BASE_PATH = (
    os.getcwd().split("SHED")[0] + "SHED/backend/"
)  # eventually set by argument or default to cwd
# make some necessary directories if they don't already exist
if not os.path.isdir(f"{BASE_PATH}fastqs/"):
    os.mkdir(f"{BASE_PATH}fastqs/")
if not os.path.isdir(f"{BASE_PATH}fastas/"):
    os.mkdir(f"{BASE_PATH}fastas/")
if not os.path.isdir(f"{BASE_PATH}processing/"):
    os.mkdir(f"{BASE_PATH}processing/")
if not os.path.isdir(f"{BASE_PATH}sams/"):
    os.mkdir(f"{BASE_PATH}sams/")
if not os.path.isdir(f"{BASE_PATH}tsvs/"):
    os.mkdir(f"{BASE_PATH}tsvs/")
#  process each SRA
for sra_acc in accession_list:
    print(f"starting processing for {sra_acc}")
    # download fastqs
    sra_fetch_code = sra_fetch.get_fastqs(BASE_PATH, sra_acc)
    if sra_fetch_code not in ((0, 0), (2, 0), (768, 0), (768, 768)):
        print(f"critical failure at fetch ({sra_fetch_code})")
        print("discontinuing pipeline execution")
        sys.exit(1)
    file_tuple = sra_file_parse.find_fastqs(BASE_PATH, sra_acc)
    read_type = len(file_tuple)
    if (
        (not isinstance(file_tuple, tuple))
        or (not file_tuple)
        or read_type not in (1, 2, 3)
    ):
        print(f"fastq mismatch {file_tuple}")
        print("skipping to next SRA Accession")
        continue
    # process fastqs reads down to collapsed fasta
    if read_type in (2, 3):
        preproc_error_code = sra_preproc.bbtools_process(BASE_PATH, sra_acc)
        if preproc_error_code == 0:
            preproc_error_code = sra_preproc.concat_files(BASE_PATH, sra_acc)
            if preproc_error_code == 0:
                preproc_error_code = sra_preproc.dereplicate_reads(BASE_PATH, sra_acc)
                if preproc_error_code == 0:
                    preproc_code = 0
                else:
                    preproc_code = 3
            else:
                preproc_code = 2
        else:
            preproc_code = 1
    elif read_type == 1:
        preproc_error_code = sra_preproc.dereplicate_reads(BASE_PATH, sra_acc)
        if preproc_error_code == 0:
            preproc_code = 0
        else:
            preproc_code = 3
    preproc_code_dict = {1: "BBTools", 2: "cat", 3: "Fastx Toolkit"}
    if preproc_code != 0:
        print(
            f"Preprocessing failed during {preproc_code_dict[preproc_code]} processing"
        )
        if preproc_error_code == 32512:
            print(
                f"{preproc_code_dict[preproc_code]} does not appear to be installed.  Please run configure.sh"
            )
            sys.exit(1)
        else:
            print("Error is not fatal, proceeding with next accession")
            continue
    mapping_code = sra_map.map_reads(BASE_PATH, sra_acc)
    if mapping_code != 0:
        print(f"Mapping failed for {sra_acc} ({mapping_code}).  ")
        continue
    vc_code = sra_vc.vc_sams(BASE_PATH, sra_acc)
    if vc_code != 0:
        print(f"Variant calling failed for {sra_acc} ({mapping_code}).  ")
        continue

    # post-processing
    # clean up


print("End Pipeline")
