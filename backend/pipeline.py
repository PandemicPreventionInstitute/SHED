#!/bin/env python3

'''
Writen by Devon Gregory
This is the wrapper script for the pipeline modules.
Last edited on 4-14-22
todo:  add remaining modules
        add arguments for ignoring progress, passing file for SRA data, setting paths and ...
'''
import os
import sys
import argparse # will use
# import modules.sra_query as sra_query# we need to decide on the method for handling queries
import modules.sra_file_parse as sra_file_parse
import modules.sra_fetch as sra_fetch
import modules.sra_preproc as sra_preproc
# import modules.sra_map as sra_map
# import modules.sra_vc as sra_vc
# import modules.sra_postproc as sra_postproc

# sra_query.querying()
# get accession based on file from eventual query function
accession_list = sra_file_parse.get_accessions('TestSraList.txt')
if not (isinstance(accession_list, list) and accession_list):
    print(f"failure at accession list aquisition ({accession_list})")
    exit()
base_path = os.getcwd().split('SHED')[0]+'SHED/backend/' # eventually make changable by argument
# make some necessary directories if they don't already exist
if not os.path.isdir(f"{base_path}fastqs/"):
    os.mkdir(f"{base_path}fastqs/")
if not os.path.isdir(f"{base_path}fastas/"):
    os.mkdir(f"{base_path}fastas/")
if not os.path.isdir(f"{base_path}processing/"):
    os.mkdir(f"{base_path}processing/")
#  process each SRA
for sra_acc in accession_list:
    print(f"starting processing for {sra_acc}")
    # download fastqs
    sra_fetch_code = sra_fetch.get_fastqs(base_path, sra_acc)
    if not sra_fetch_code in ((0,0), (2, 0), (768, 0), (768, 768)):
        print(f"critical failure at fetch ({sra_fetch_code})")
        print("discontinuing pipeline execution")
        exit(1)
    file_tuple = sra_file_parse.find_fastqs(base_path, sra_acc)
    read_type = len(file_tuple)
    if (not isinstance(file_tuple, tuple)) or (not file_tuple) or (not (read_type == 1 or read_type == 2 or read_type == 3)):
        print(f"fastq mismatch (file_tuple)")
        print("skipping to next SRA Accession")
        continue
    # process fastqs reads down to collapsed fasta
    elif read_type == 2 or read_type == 3:
        preproc_error_code = sra_preproc.bbtools_process(base_path, sra_acc)
        if preproc_error_code == 0:
            preproc_error_code = sra_preproc.concat_files(base_path, sra_acc)
            if preproc_error_code == 0:
                preproc_error_code = sra_preproc.dereplicate_reads(base_path, sra_acc, read_type)
                if preproc_error_code == 0:
                    preproc_code = 0
                else:
                    preproc_code = 3
            else:
                preproc_code = 2
        else:
            preproc_code = 1
    elif read_type == 1:
        preproc_error_code = sra_preproc.dereplicate_reads(base_path, sra_acc, read_type)
        if preproc_error_code == 0:
            preproc_code = 0
        else:
            preproc_code = 3
    preproc_code_dict = {1:'BBTools', 2: 'cat', 3: 'Fastx Toolkit'}
    if preproc_code != 0:
        print(f"Preprocessing failed during {preproc_code_dict[preproc_code]} processing")
        if preproc_error_code == 32512:
            print(f"{preproc_code_dict[preproc_code]} does not appear to be installed.  Please run configure.sh")
            exit(1)
        else:
            print(f"Error is not fatal, proceeding with next accession")
            continue
    # map
    # variant call
    # post-processing
    # clean up


print('End Pipeline')