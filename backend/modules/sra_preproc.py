#!/bin/env python3

'''
Writen by Devon Gregory
This script will check paired SRA fastq files for errors, correct them and merge the reads.
The merged reads or singlet reads with then be collapsed.  The SRA fastq files processed will be
samples listed in the supplied file.
Last edited on 4-10-22
'''

import os
import sys

def repair_files(base_path, sra_acc, file_list):
    '''takes a list(pair) of paired end read files, repairs them, and then returns the names of the repaired files'''
    open(f"{base_path}processing/{sra_acc}.repair.started", 'w').close()
    repair_code = os.system(f"bash repair.sh in={file_list[0]} in2={file_list[1]} out={base_path}processing/{sra_acc}_1.rep.fq out2={base_path}processing/{sra_acc}_2.rep.fq outs={base_path}processing/{sra_acc}_sing.rep.fq")
    if repair_code == 0:
        os.remove(f"{base_path}processing/{sra_acc}.repair.started")
        return([f"{base_path}processing/{sra_acc}_1.rep.fq", f"{base_path}processing/{sra_acc}_2.rep.fq", f"{base_path}processing/{sra_acc}_sing.rep.fq"])
    return(repair_code)

def merge_files(base_path, sra_acc, file_list):
    '''takes a list(pair) of paired end read files, merges them, and then returns the names of the files for the merged and unmerged reads'''
    open(f"{base_path}processing/{sra_acc}.merge.started", 'w').close()
    merge_code = os.system(f"bash bbmerge.sh in1={file_list[0]} in2={file_list[1]}  out={base_path}processing/{sra_acc}.merged.fq outu1={base_path}processing/{sra_acc}.un1.fq outu2={base_path}processing/{sra_acc}.un2.fq")
    # codes: 0 - success, 256 - error
    if merge_code == 0:
        os.remove(f"{base_path}processing/{sra_acc}.merge.started")
        return([f"{base_path}processing/{sra_acc}.merged.fq", f"{base_path}processing/{sra_acc}.un1.fq", f"{base_path}processing/{sra_acc}.un2.fq"])
    return(merge_code)

def concat_files(base_path, sra_acc, file_list):
    '''takes a list of fastq files, concatenates them, and then returns the name of the new file'''
    open(f"{base_path}processing/{sra_acc}.cat.started", 'w').close()
    cat_code = os.system(f"cat {' '.join(file_list)} > {base_path}processing/{sra_acc}.all.fq")
    if cat_code == 0:
        os.remove(f"{base_path}processing/{sra_acc}.cat.started")
        return(f"{base_path}processing/{sra_acc}.all.fq")
    return(cat_code)

def dereplicate_reads(base_path, sra_acc, file_name):
    '''takes the name of a fastq file, collapses the reads in it, and then returns the name of the new file'''
    open(f"{base_path}fastas/{sra_acc}.col.started", 'w').close()
    collapse_code = os.system(f"fastx_collapser -i {file_name} -o {base_path}fastas/{sra_acc}.collapsed.fa")
    # codes: None - file not found 0 - success 256 - bad file format, can't create new file
    if collapse_code == 0:
        os.remove(f"{base_path}fastas/{sra_acc}.col.started")
        return(f"{base_path}fastas/{sra_acc}.collapsed.fa")
    return(collapse_code)

def preprocess_sra(base_path, sra_acc, current_progress, file_list):
    '''takes a SRA accession and processes the files from it starting from provided progress point and with provided file'''
    if not (current_progress or file_list):
        print(f"Start point or files not provided for preprocessing {sra_acc}")
        return(1)
    if current_progress == 'preproc':
        read_types = len(file_list)
        if read_types == 0:
            print(f"No fastq files for {sra_acc} found in {base_path}fastqs/")
            return(1)
        elif read_types > 2:
            print(f"Too many fastq files for {sra_acc} found, please check files and remove extra, then rerun")
            return(2)
        elif read_types == 1:
            current_progress = 'derep'
        elif read_types == 2:
            current_progress = 'merge'
    if current_progress == 'merge':
        merge_code = merge_files(base_path, sra_acc, file_list)
        if isinstance(merge_code, int):
            print("merging of {sra_acc} files failed, attempting repair and merge")
            current_progress = 'repair'
        else:
            file_list = merge_code
            current_progress = 'cat'
    if current_progress == 'repair':
            repair_code = repair_files(base_path, sra_acc, file_list)
            if isinstance(repair_code, int):
                print(f"repair of {sra_acc} failed")
                return(3)
            merge_code = merge_files(base_path, sra_acc, repair_code)
            if isinstance(merge_code, int):
                print(f"Mergeing failed after repair for {sra_acc}")
                return(4)
            file_list = merge_code
            file_list.append(repair_code[-1])
            current_progress = 'cat'
    if current_progress == 'cat':
        cat_code = concat_files(base_path, sra_acc, file_list)
        if isinstance(cat_code, int):
            print(f"concatenting failed for {sra_acc}")
            return(5)
        file_list = [cat_code]
        current_progress = 'derep'
    if current_progress == 'derep':
        collapse_code = dereplicate_reads(base_path, sra_acc, file_list[0])
        if isinstance(collapse_code, int):
            print(f"collapsing failed for {sra_acc} ({collapse_code})")
            return(6)
        return('ok')
    else:
        print('Unknown error occured for '+sra_acc )
        return(7)





if __name__ == "__main__":
    ''' Stand alone script.  Takes a filename with arguement '-i' that holds SRA accessions and processes fastq files of those accessions'''
    import sra_file_parse

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
                preprocess_sra(sra_acc)

