#!/bin/env python3

'''
Writen by Devon Gregory
This is the wrapper script for the pipeline modules.
Last edited on 4-6-22
'''
# import os
# import sys
# import argparse # may ultimately end up using
# import modules.sra_query as sra_query# we need to decide on the method for handling queries
import modules.sra_fetch as sra_fetch
# modules to potentially be implimented
# import modules.sra_fetch as sra_fetch
# import modules.sra_preproc as sra_preproc
# import modules.sra_map as sra_map
# import modules.sra_vc as sra_vc
# import modules.sra_postproc as sra_postproc

# sra_query.querying() 
accession_list = sra_fetch.get_accessions('TestSraList.txt')
if not (isinstance(accession_list, list) and accession_list):
    print(f"failure at accession list aquisition ({accession_list})")
    exit()
sra_fetch_code = sra_fetch.fetching(accession_list) # currently just passes test SRA accession list, will be updated based on querying decisions
if sra_fetch_code != 0:
    print(f"failure at fetch ({sra_fetch_code})")
    exit()


print('End Pipeline')