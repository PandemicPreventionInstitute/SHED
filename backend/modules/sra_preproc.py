#!/bin/env python3

'''
Writen by Devon Gregory
This script will check paired SRA fastq files for errors, correct them and merge the reads.
The merged reads or singlet reads with then be collapsed.  The SRA fastq files processed will be
samples listed in the supplied file.
Last edited on 4-14-22
todo: capture std out from program calls
    add testing for empty files
'''

import os
import sys
sys.path.insert(0, os.getcwd().split('SHED')[0]+'SHED/backend/modlules/' )
from sra_file_parse import find_fastqs

# def get_fastq_stat(base_path, sra_acc, file_list):

def bbtools_process(base_path, sra_acc):
    '''
    Called to merge, and if needed repair the paired end files provicded.

    Parameters:
    base_path - path of directory where repaired files will be written in the ./processing/ subfolder
    sra_acc - accession for the SRA sample

    Functionality:
    Uses BBTools bbmerge.sh to merge, and if needed repair.sh to repair, paired end fastqs.

    Logic path -  If merging has already been succesfully completed -> return success
                  elif repairs were previously attempted but not completed -> retry repair and merge, return success state
                  elif repairs were previoulsy successful, but not merging -> merge, return success state
                  else -> attempt initial merge, repair if needed, return success state
                  self calls when possible

    Relies on BBTools to handle its own functionality and erros for the most part.
    0 indicates success, 256 for any errors

    Returns a status code, 0 for success
    '''
    if (os.path.isfile(f"{base_path}processing/{sra_acc}.merged.fq") and os.path.isfile(f"{base_path}processing/{sra_acc}.un1.fq") \
        and os.path.isfile(f"{base_path}processing/{sra_acc}.un2.fq")) and not os.path.isfile(f"{base_path}processing/{sra_acc}.merge.started"):
        bbtools_return_code = 0
    elif os.path.isfile(f"{base_path}processing/{sra_acc}.repair.started"):
        # try repair, merge if successful
        # check for raw fastqs
        file_pair = find_fastqs(base_path, sra_acc)
        if isinstance(file_pair, tuple) and len(file_pair) == 2:
            repair_code = os.system(f"bash repair.sh overwrite=true in={file_pair[0]} in2={file_pair[1]} \
                out={base_path}processing/{sra_acc}_1.rep.fq out2={base_path}processing/{sra_acc}_2.rep.fq outs={base_path}processing/{sra_acc}_sing.rep.fq")
            if repair_code == 0:
                os.remove(f"{base_path}processing/{sra_acc}.repair.started")
                # re-attempting merge
                merge_code = bbtools_process(base_path, sra_acc)
                bbtools_return_code = merge_code
            else:
                bbtools_return_code = repair_code
        else:
            bbtools_return_code = -1
    elif (os.path.isfile(f"{base_path}processing/{sra_acc}_1.rep.fq") and os.path.isfile(f"{base_path}processing/{sra_acc}_2.rep.fq") \
        and os.path.isfile(f"{base_path}processing/{sra_acc}_sing.rep.fq")):
        # repiar already done, merge
            # re-attempting merge
            open(f"{base_path}processing/{sra_acc}.merge.started", 'w').close()
            merge_code = os.system(f"bash bbmerge.sh qtrim=t in1={base_path}processing/{sra_acc}_1.rep.fq in2={base_path}processing/{sra_acc}_2.rep.fq \
                out={base_path}processing/{sra_acc}.merged.fq outu1={base_path}processing/{sra_acc}.un1.fq outu2={base_path}processing/{sra_acc}.un2.fq")
            if merge_code == 0:
                os.remove(f"{base_path}processing/{sra_acc}.merge.started")
            bbtools_return_code = merge_code
    else:
        # initial merge attempt
        # check for raw fastqs
        file_pair = find_fastqs(base_path, sra_acc)
        if isinstance(file_pair, tuple) and len(file_pair) == 2:
            open(f"{base_path}processing/{sra_acc}.merge.started", 'w').close()
            merge_code = os.system(f"bash bbmerge.sh qtrim=t in1={file_pair[0]} in2={file_pair[1]}  \
                out={base_path}processing/{sra_acc}.merged.fq outu1={base_path}processing/{sra_acc}.un1.fq outu2={base_path}processing/{sra_acc}.un2.fq")
            if merge_code == 0:
                bbtools_return_code = merge_code
                os.remove(f"{base_path}processing/{sra_acc}.merge.started")
            else:
                open(f"{base_path}processing/{sra_acc}.repair.started", 'w').close()
                repair_remerge_code = bbtools_process(base_path, sra_acc)
                bbtools_return_code = repair_remerge_code
        else:
            bbtools_return_code = -1
    return(bbtools_return_code)

def concat_files(base_path, sra_acc):
    '''
    Called to concatenate merged and unmergable reads

    Parameters:
    base_path - path of directory where repaired files will be written in the ./processing/ subfolder
    sra_acc - accession for the SRA sample

    Functionality:
    find read files from previous processing and uses system cat command to concatenate them

    Returns a status code from command call, 0 for success, -1 if files form previous processing can't all be found
    '''
    if os.path.isfile(f"{base_path}processing/{sra_acc}.all.fq") and not os.path.isfile(f"{base_path}processing/{sra_acc}.cat.started"):
        cat_code = 0
    else:
        file_list = []
        if os.path.isfile(f"{base_path}processing/{sra_acc}.merged.fq") and os.path.isfile(f"{base_path}processing/{sra_acc}.un1.fq") \
            and os.path.isfile(f"{base_path}processing/{sra_acc}.un2.fq"):
            file_list = [f"{base_path}processing/{sra_acc}.merged.fq", f"{base_path}processing/{sra_acc}.un1.fq", \
                f"{base_path}processing/{sra_acc}.un2.fq"]
            if os.path.isfile(f"{base_path}processing/{sra_acc}_sing.rep.fq"):
                file_list.append(f"{base_path}processing/{sra_acc}_sing.rep.fq")

        if file_list:
            open(f"{base_path}processing/{sra_acc}.cat.started", 'w').close()
            cat_code = os.system(f"cat {' '.join(file_list)} > {base_path}processing/{sra_acc}.all.fq")
            if cat_code == 0:
                os.remove(f"{base_path}processing/{sra_acc}.cat.started")
        else:
            print(f"can't file all files to concatenate for {sra_acc}")
            cat_code = -1
    return(cat_code)

def dereplicate_reads(base_path, sra_acc, read_type):

    # codes: None - file not found 0 - success 256 - bad file format, can't create new file
    if os.path.isfile(f"{base_path}fastas/{sra_acc}.collapsed.fa") and not os.path.isfile(f"{base_path}fastas/{sra_acc}.col.started"):
        collapse_code = 0
    else:
        open(f"{base_path}fastas/{sra_acc}.col.started", 'w').close()
        if read_type == 1:
            fastq_file = find_fastqs(base_path, sra_acc)
            if isinstance(fastq_file, tuple) and len(fastq_file) == 1:
                os.system(f"gzip -d -k {fastq_file[0]}")
                collapse_code = os.system(f"fastx_collapser -i {fastq_file[0][:-3]} -o {base_path}fastas/{sra_acc}.collapsed.fa")
                if collapse_code == 0:
                    os.remove(f"{base_path}fastas/{sra_acc}.col.started")
                os.remove(fastq_file[0][:-3])
            else:
                print(f"Error finding single read fastq to collapse for {sra_acc}")
                collapse_code = -2
        elif read_type == 2:
            collapse_code = os.system(f"fastx_collapser -v -i {base_path}processing/{sra_acc}.all.fq -o {base_path}fastas/{sra_acc}.collapsed.fa")
            if collapse_code == 0:
                os.remove(f"{base_path}fastas/{sra_acc}.col.started")
        else:
            print(f"invalid read type {read_type}\n Should be either 1 or 2 for single or paired reads respectively")
            collapse_code = -1
    return(collapse_code)

def preprocess_sra(base_path, sra_acc, read_type):
    '''takes a SRA accession and processes the files from it starting from provided progress point and with provided file'''
    if (not isinstance(read_type, int)) or not (read_type == 1 or read_type == 2):
        print(f"Unknown read types found: {read_type}\n Should be either 1 or 2 for single or paired reads respectively")
        preproc_code = -1
        print(type(read_type))
    elif read_type == 2:
        merge_code = bbtools_process(base_path, sra_acc)
        if merge_code == 0:
            concat_code = concat_files(base_path, sra_acc)
            if concat_code == 0:
                collapse_code = dereplicate_reads(base_path, sra_acc, read_type)
                if collapse_code == 0:
                    preproc_code = 0
                else:
                    preproc_code = 3
            else:
                preproc_code = 2
        else:
            preproc_code = 1
    elif read_type == 1:
        collapse_code = dereplicate_reads(base_path, sra_acc, read_type)
        if collapse_code == 0:
            preproc_code = 0
        else:
            preproc_code = 3
    return(preproc_code)


if __name__ == "__main__":
    ''' Stand alone script.  Takes a filename with arguement '-i' that holds SRA accessions and pre-processes fastq files of those accessions'''


    args = sra_file_parse.arg_parse()
    base_path = os.getcwd().split('SHED')[0]+'SHED/backend/'
    if args.file:
        accession_list = sra_file_parse.get_accessions(args.file)
        if isinstance(accession_list, list):
            if not os.path.isdir(f"{base_path}fastas/"):
                os.mkdir(f"{base_path}fastas/")
            if not os.path.isdir(f"{base_path}processing/"):
                os.mkdir(f"{base_path}processing/")
            for sra_acc in accession_list:
                print(sra_acc)
                current_progress, file_list = sra_file_parse.find_progess(base_path, sra_acc)
                print(current_progress)
                if current_progress != 'map' and current_progress != 'vc' and current_progress != 'fetch':
                    preproc_code = preprocess_sra(base_path, sra_acc, current_progress, file_list)
                    print(preproc_code)

