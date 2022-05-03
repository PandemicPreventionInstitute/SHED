#!/bin/env python3

"""
Writen by Devon Gregory
This is the wrapper script for the pipeline modules.
Last edited on 5-2-22
todo:  add remaining modules
        add arguments for ignoring progress, passing file for SRA data, setting paths and ...
"""
import os
import sys
import argparse
# import sra_query
from modules import sra_file_parse
from modules import sra_fetch
from modules import sra_preproc
from modules import sra_map
from modules import sra_vc
from modules import sra_consensus
# import sra_postproc

def arg_parse():
    """parses command arguments"""
    parser = argparse.ArgumentParser(
        description="This pipeline will download and process reads from NCBI's SRA samples"
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        dest="work_path",
        default=os.getcwd(),
        help="Path to directory for processing and storing files",
    )
    parser.add_argument(
        "-i",
        "--file",
        type=str,
        dest="file",
        help="SRA accession list or metadata table.  Accessions to be at the start of a newline and separated from the remaining line with a comma.",
    )
    return parser.parse_args()

def main():
    '''Main pipeline logic'''
    args = arg_parse()
    BASE_PATH = os.path.normpath(args.work_path)
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_PATH)
    # sra_query.querying() # will be using aws athena
    # get accession based on file from eventual query function
    if args.file:
        accession_list = sra_file_parse.get_accessions(args.file)
    elif os.path.isfile(f"{BASE_PATH}/SraRunTable.csv"):
        accession_list = sra_file_parse.get_accessions(f"{BASE_PATH}/SraRunTable.csv")
    elif os.path.isfile(f"{BASE_PATH}/SraRunTable.txt"):
        accession_list = sra_file_parse.get_accessions(f"{BASE_PATH}/SraRunTable.txt")
    else:
        print("No SRA accession list or metadata files found.")
        sys.exit(1)
    if not (isinstance(accession_list, list) and accession_list):
        print("Failure at accession list aquisition")
        sys.exit(1)
    # make some necessary directories if they don't already exist
    if not os.path.isdir(f"{BASE_PATH}/fastqs"):
        os.mkdir(f"{BASE_PATH}/fastqs")
    if not os.path.isdir(f"{BASE_PATH}/fastas"):
        os.mkdir(f"{BASE_PATH}/fastas")
    if not os.path.isdir(f"{BASE_PATH}/processing"):
        os.mkdir(f"{BASE_PATH}/processing")
    if not os.path.isdir(f"{BASE_PATH}/sams"):
        os.mkdir(f"{BASE_PATH}/sams")
    if not os.path.isdir(f"{BASE_PATH}/tsvs"):
        os.mkdir(f"{BASE_PATH}/tsvs")
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
                    f"{preproc_code_dict[preproc_code]} does not appear to be installed.  \
                        Please make sure it is installed and executable directly from the command line"
                )
                sys.exit(1)
            else:
                print("Error is not fatal, proceeding with next accession")
                continue
        # map reads to SARS2 with minimap2
        mapping_code = sra_map.map_reads(BASE_PATH, sra_acc)
        if mapping_code != 0:
            print(f"Mapping failed for {sra_acc} ({mapping_code}).  ")
            if mapping_code == 32512:
                print("Minimap not found.  Please make sure it is installed an executable from the command line '$ minimap2 -h'")
                sys.exit(1)
            continue
        # get variants and nt calls from sam with SAM Refiner
        vc_code = sra_vc.vc_sams(BASE_PATH, sra_acc)
        if vc_code != 0:
            print(f"Variant calling failed for {sra_acc} ({mapping_code}).  ")
            continue
        consensus_code = sra_consensus.gen_consensus(BASE_PATH, sra_acc)
        if consensus_code != 0:
            print(f"Consensus generation failed for {sra_acc} ({consensus_code}).  ")
            continue

        # post-processing
        # clean up


    print("End Pipeline")

if __name__ == '__main__':
    main()
