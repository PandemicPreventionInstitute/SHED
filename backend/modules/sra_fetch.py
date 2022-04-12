#!/bin/env python3

'''
Writen by Devon Gregory
This script will download fastq files from NCBI SRA for the samples listed a argument
provided file or in 'SraRunTable.csv' or 'SraRunTable.txt'.
The fastq files will allow further analysis by bioinformatics pipelines.
Last edited on 4-12-22
todo: capture std out from fetch
'''
import os
import sys
import time


def fetching(base_path, sra_acc):
    '''uses NCBI's SRA toolkit to download SRA sample fastq files for processing'''
    '''
    rely on SRA toolkit to handle their own functionality and erros for the most part
    codes: 0 - system call executed w/o error, 2 - run interuption, 32512 - program not found, 768 - prefetch can't connect or accession not found, 16384 dump can't connect,
    If connection is initially present but lost, there does not seem to be a timely timeout built into either prefetch or dump.
    '''
    open(f"{base_path}fastqs/{sra_acc}.fetch.started", 'w').close()
    prefetch_code = os.system(f"prefetch {sra_acc}")
    fastq_dump_code = os.system(f"fastq-dump {sra_acc} --split-files -O {base_path}fastqs/")
    if prefetch_code+fastq_dump_code == 0:
    # no errors reported by toolkit
        os.remove(f"{base_path}fastqs/{sra_acc}.fetch.started")
        print(f"{sra_acc} fastq files written to .../backend/fastqs/ ") # path might need updating at some point
    elif fastq_dump_code == 2:
    # only if processes are actually killed I think
        print('Fetching interupted.  Please restart')
        return(2)
    elif prefetch_code == 2 and fastq_dump_code == 0:
        print('prefetch interupted, but fastq dump was successful.  Continuing...')
    elif prefetch_code == 768:
        if fastq_dump_code == 768:
            print('SRA accession was not found by SRA Toolkit.  Please verify.  Continuing with remaining accessions')
        elif fastq_dump_code == 16384:
            print('Can not connect to NCBI SRA.  Please verify internet connection and restart.  If connection continues to fail, NCBI may be down, try again later.')
            return(4)
        elif fastq_dump_code == 0:
            print('prefetch failed, but fastq dump was successful.  Continuing...')
        else:
            print('unknown error for fastq_dump: '+fastq_dump_code)
            return(fastq_dump_code)
    elif prefetch_code == 32512 or fastq_dump_code == 32512:
        print('NCBI SRA Toolkit not properly installed.  Please run configure.sh')
        return(5)
    else:
        print('unknown errors: '+prefetch_code+' '+fastq_dump_code)
        return(fastq_dump_code)
    return(0)

if __name__ == "__main__":
    ''' Stand alone script.  Takes a filename with arguement '-i' that holds SRA accessions and downloads fastqs for those samples'''
    import sra_file_parse
    args = sra_file_parse.arg_parse()
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
    base_path = os.getcwd().split('SHED')[0]+'SHED/backend/'
    # downloads fastq files
    if filename:
        accession_list = sra_file_parse.get_accessions(args.file)
        if isinstance(accession_list, list):
            for sra_acc in accession_list:
                fetch_code = fetching(base_path, sra_acc)
                if fetch_code != 0:
                    print("Fetching failed.")
        else:
            print('Retrieval of SRA accessions from file failed')