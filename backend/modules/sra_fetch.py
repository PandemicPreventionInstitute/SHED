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
import pytest

# uses NCBI's SRA toolkit to download SRA sample fastq files for processing
def fetching(filename):
    try:
        run_list_fh = open(filename, 'r')
    except:
        print("unable to open "+filename)
        return(1)
    else:
        for line in run_list_fh:
            # assumes SRA accessions are listed first on a new line with the possibility of file being tab or comma separated
            # file will have been generated either manually or by the yet to be implimented query module
            # may ultimately be chaned to be a list of accessions
            sra_acc = line.split(',')[0].split('\t')[0].strip('\n\r').upper()
            try:
                assert (sra_acc.startswith('SRR') or sra_acc.startswith('ERR'))
                assert sra_acc.split('RR')[1].isnumeric()
                
                time.sleep(1)
            except AssertionError:
                print(sra_acc+' does not appear to be a valid SRA accession')
            else:
                # codes: 0 - system call executed w/o error, 2 - run interuption, 32512 - program not found, 768 - prefetch can't connect or accession not found, 16384 dump can't connect, 
                # if connection is lost, there does not seem to be a timely timeout built into either prefetch or dump.  May want to add one here.
                prefetch_code = os.system(f"prefetch {sra_acc}")
                fastq_dump_code = os.system(f"fastq-dump {sra_acc} --split-files -O ./fastqs/")
                if prefetch_code+fastq_dump_code == 0:
                    pass
                elif fastq_dump_code == 2:
                    print('Interuption of fetching.  Please restart')
                    return(2)
                elif prefetch_code == 2 and fastq_dump_code == 0:
                    print('prefetch interupted, but fastq dump was successful.  Continuing...')
                elif prefetch_code == 768 and fastq_dump_code == 768:
                    print('SRA accesion was not found by SRA Toolkit.  Please verify.  Continuing with remaining accessions')
                elif prefetch_code == 768 and fastq_dump_code == 16384:
                    print('Can not connect to NCBI SRA.  Please verify internet connection and restart.  If connection continues to fail, NCBI may be down, try again later.')
                    return(4)
                
    return(0)

    
    run_list_fh.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='File containing SRA accessions to be fetched.  Accesions to be at the start of a newline and separated from the remaining line with either a comma or tab '
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