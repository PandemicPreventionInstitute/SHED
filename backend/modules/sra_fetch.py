#!/bin/env python3

'''
Writen by Devon Gregory
This script will download fastq files from NCBI SRA for the samples listed a argument
provided file or in 'SraRunTable.csv' or 'SraRunTable.txt'.
The fastq files will allow further analysis by bioinformatics pipelines.
Last edited on 4-7-22
'''
import os
import sys
import argparse
import time

def get_accessions(filename):
    '''get and return SRA accessions from provided file'''
    try:
        run_list_fh = open(filename, 'r')
    except Exception as e:
        print(e)
        return(1)
    else:
        accession_list = []
        for line in run_list_fh:
            # assumes SRA accessions are listed first on a new line with the possibility of file being tab or comma separated
            # file will have been generated either manually or by the yet to be implimented query module
            sra_acc = line.split(',')[0].split('\t')[0].strip('\n\r').upper()
            try:
                assert (sra_acc.startswith('SRR') or sra_acc.startswith('ERR')), "Incorrect prefix"
                assert sra_acc.split('RR')[1].isnumeric(), "Non-numeric listing"
            except AssertionError as e:
                print(sra_acc+' does not appear to be a valid SRA accession: '+str(e))
            else:
                accession_list.append(sra_acc)

        run_list_fh.close()
        if not accession_list:
            print('No SRA Accessions were found.')
            return(2)
        return(accession_list)

def fetching(accession_list):
    '''uses NCBI's SRA toolkit to download SRA sample fastq files for processing'''
    if isinstance(accession_list, list) and accession_list:
        for sra_acc in accession_list:
            '''
            rely on SRA toolkit to handle their own functionality and erros for the most part
            codes: 0 - system call executed w/o error, 2 - run interuption, 32512 - program not found, 768 - prefetch can't connect or accession not found, 16384 dump can't connect,
            If connection is initially present but lost, there does not seem to be a timely timeout built into either prefetch or dump.
            '''
            prefetch_code = os.system(f"prefetch {sra_acc}")
            fastq_dump_code = os.system(f"fastq-dump {sra_acc} --split-files -O ./fastqs/")
            if prefetch_code+fastq_dump_code == 0:
            # no errors
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
    else:
        print('No SRA Accessions')
        return(1)

if __name__ == "__main__":
    ''' Stand alone script.  Takes a filename with arguement '-i' that holds SRA accessions and downloads fastqs for those samples'''
    parser = argparse.ArgumentParser(
            description='File containing SRA accessions to be fetched.  Accessions to be at the start of a newline and separated from the remaining line with either a comma or tab '
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
        accession_list = get_accessions(filename)
        if isinstance(accession_list, list):
            fetch_code = fetching(accession_list)
            if fetch_code != 0:
                print("Fetching failed.")
        else:
            print('Retrieval of SRA accessions from file failed')