#!/bin/env python3

'''
Writen by Devon Gregory
This script will read through a file to obtain SRA accessions and pass them to the caller
Last edited on 4-9-22
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