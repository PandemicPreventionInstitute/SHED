#!/bin/env python3

'''
Writen by Devon Gregory
This is the wrapper script for the pipeline modules.
Last edited on 4-12-22
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
    current_progress, file_list = sra_file_parse.find_progess(base_path, sra_acc)
    if current_progress == 'fetch':
        # download fastqs
        sra_fetch_code = sra_fetch.fetching(base_path, sra_acc)
        if sra_fetch_code != 0:
            print(f"critical failure at fetch ({sra_fetch_code})")
            print("discontinuing pipeline execution")
            exit
        file_list = sra_file_parse.find_fastqs(base_path, sra_acc)
        current_progress = 'preproc'
    if current_progress != 'map' and current_progress != 'vc':
        # process fastqs reads down to collapsed fasta
        preproc_code = sra_preproc.preprocess_sra(base_path, sra_acc, current_progress, file_list)
        print(preproc_code)
    # clean up:  what files are to be kept?  compressed?
    # map
    # variant call


print('End Pipeline')