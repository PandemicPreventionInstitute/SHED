#!/bin/env python3

'''
Writen by Devon Gregory
This script will download fastq files from NCBI SRA for the samples listed a argument 
provided file or in 'SraRunTable.csv' or 'SraRunTable.txt'.  
The fastq files will allow further analysis by bioinformatic pipelines.
Last edited on 3-30-22
todo: add check for sta toolkit config and config option for first time use
'''
import os
import sys
import argparse
import time

def fetching(filename):
    run_list_fh = open(filename, 'r')
    for line in run_list_fh:
        # assumes SRA accessions are listed first on a new line with the possibility of file being tab or comma seperated
        sra_acc = line.split(',')[0].split('\t')[0].strip('\n\r')
        # may need to be updated for paths
        os.system(f"prefetch {sra_acc}")
        os.system(f"fastq-dump {sra_acc} --split-files -O ./fastqs/")
        time.sleep(1)
    
    run_list_fh.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='x'
    )
    parser.add_argument(
        '-i', '--file',
        type=str,
        dest='file',
        default='',
        help='SRA accession list or metadata table'
    )

    args = parser.parse_args()

    # check to see if files with SRA accession or meta data exist before pulling accession list
    filename = ''
    if args.file:
        filename = args.file
    elif os.path.isfile('SraRunTable.csv'):
        filename = 'SraRunTable.csv'
    elif os.path.isfile('SraRunTable.txt'):
        filename = 'SraRunTable.txt'
    else:
        print('No SRA accession list or metadata files found.')

    # downloads fastq files
    if filename:
        fetching(filename)