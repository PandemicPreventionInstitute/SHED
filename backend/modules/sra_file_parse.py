#!/bin/env python3

'''
Writen by Devon Gregory
This script will read through a file to obtain SRA accessions and pass them to the caller
Last edited on 4-10-22
'''

import os
import sys
import argparse

def arg_parse():
    ''' parses file argument'''
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

    return(args)

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
            # assumes SRA accessions are listed first on a new line with the possibility of file being tab, space or comma separated
            # file will have been generated either manually or by the yet to be implimented query module
            sra_acc = line.split(',')[0].split(' ')[0].split('\t')[0].strip('\n\r').upper()
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

def find_fastqs(base_path, sra_acc):
    '''takes a sra accession and discovers the fastq files that have been fetched for it'''
    file_list = []
    if os.path.isfile(f'{base_path}fastqs/{sra_acc}.fastq'):
        file_list.append(f'{base_path}fastqs/{sra_acc}.fastq')
    elif os.path.isfile(f'{base_path}fastqs/{sra_acc}.fastq.gz'):
        file_list.append(f'{base_path}fastqs/{sra_acc}.fastq.gz')
    if os.path.isfile(f'{base_path}fastqs/{sra_acc}_1.fastq'):
        file_list.append(f'{base_path}fastqs/{sra_acc}_1.fastq')
    elif os.path.isfile(f'{base_path}fastqs/{sra_acc}_1.fastq.gz'):
        file_list.append(f'{base_path}fastqs/{sra_acc}_1.fastq.gz')
    if os.path.isfile(f'{base_path}fastqs/{sra_acc}_2.fastq'):
        file_list.append(f'{base_path}fastqs/{sra_acc}_2.fastq')
    elif os.path.isfile(f'{base_path}fastqs/{sra_acc}_2.fastq.gz'):
        file_list.append(f'{base_path}fastqs/{sra_acc}_2.fastq.gz')
    return(file_list)

def find_progess(base_path, sra_acc):
    '''takes a sra accession and discovers where in the preprocessing to (re)start and with what files'''
    if os.path.isfile(f"{base_path}fastas/{sra_acc}.collapsed.fa") and not os.path.isfile(f"{base_path}fastas/{sra_acc}.col.started"):
        return('map', [f"{base_path}fastas/{sra_acc}.collapsed.fa"])
    elif os.path.isfile(f"{base_path}processing/{sra_acc}.all.fq") and not os.path.isfile(f"{base_path}processing/{sra_acc}.cat.started"):
        return('derep', [f"{base_path}processing/{sra_acc}.all.fq"])
    elif os.path.isfile(f"{base_path}processing/{sra_acc}.merged.fq") and os.path.isfile(f"{base_path}processing/{sra_acc}.un1.fq") \
        and os.path.isfile(f"{base_path}processing/{sra_acc}.un2.fq") and not os.path.isfile(f"{base_path}processing/{sra_acc}.merge.started"):
        return('cat', [f"{base_path}processing/{sra_acc}.merged.fq", \
            f"{base_path}processing/{sra_acc}.un1.fq", f"{base_path}processing/{sra_acc}.un2.fq"])
    elif os.path.isfile(f"{base_path}processing/{sra_acc}_1.rep.fq") and os.path.isfile(f"{base_path}processing/{sra_acc}_2.rep.fq") \
        and os.path.isfile(f"{base_path}processing/{sra_acc}_sing.rep.fq") and not os.path.isfile(f"{base_path}processing/{sra_acc}.repair.started"):
        return('merge', [f"{base_path}processing/{sra_acc}_1.rep.fq", \
            f"{base_path}processing/{sra_acc}_2.rep.fq", f"{base_path}processing/{sra_acc}_sing.rep.fq"])
    elif os.path.isfile(f"{base_path}fastqs/{sra_acc}.repair.started"):
        return('repair', find_fastqs(base_path, sra_acc))
    elif os.path.isfile(f"{base_path}fastqs/{sra_acc}.fetch.started"):
        return('fetch', [])
    else:
        file_list = find_fastqs(base_path, sra_acc)
        if file_list:
            return('preproc' , file_list)

    return('fetch', [])

if __name__ == "__main__":
    ''' Stand alone script.  Takes a filename with arguement '-i' that holds SRA accessions and prints them'''


    args = arg_parse()

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

    if filename:
        for sra_acc in get_accessions(filename):
            print(sra_acc)