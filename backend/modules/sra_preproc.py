#!/bin/env python3

"""
Writen by Devon Gregory
This script has functions to merge paired SRA fastq files, repair the files if needed,
concatonate merged and unmergable reads, and dereplicate the concatenated or single read file.
It can be loaded as a module or run as a stand alone script. As the latter,
it parses the file provided in the command argument,
or a metadata table in the cwd, for accessions and then calls its own functions.
Last edited on 5-1-22
todo: capture std out from program calls
    add timeouts
"""

import os
import sys
sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend/modlules/")
from sra_file_parse import find_fastqs, get_accessions, arg_parse

# def get_fastq_stat(f_base_path, f_sra_acc):


def bbmerge_files(f_base_path: str, f_sra_acc: str, file_pair: tuple) -> int:
    """
    Called to merge the raw paired fastq files or repaired paired fastq files.

    Parameters:
    f_base_path - path of directory where repaired files will be written in the ./processing/ subfolder - string
    f_sra_acc - accession for the SRA sample - string
    file_pair - forward and reverse paired read fastqs, raw or repaired

    Uses BBTools bbmerge.sh to merge files

    Relies on BBTools to handle its own functionality and errors.
    0 indicates success, 256 for any errors

    Returns a status code
    """
    open(f"{f_base_path}processing/{f_sra_acc}.merge.started", "w").close()
    merge_code = os.system(
        f"bbmerge.sh qtrim=t in1={file_pair[0]} in2={file_pair[1]}  \
        out={f_base_path}processing/{f_sra_acc}.merged.fq outu1={f_base_path}processing/{f_sra_acc}.un1.fq outu2={f_base_path}processing/{f_sra_acc}.un2.fq"
    )
    if merge_code == 0:
        os.remove(f"{f_base_path}processing/{f_sra_acc}.merge.started")
    return merge_code


def repair_files(f_base_path: str, f_sra_acc: str, file_pair: tuple) -> int:
    """
    Called to repair the raw paired fastq files.

    Parameters:
    f_base_path - path of directory where repaired files will be written in the ./processing/ subfolder - string
    f_sra_acc - accession for the SRA sample - string
    file_pair - forward and reverse paired read fastqs, and leftover singles if any (ignored by function)

    Uses BBTools repair.sh to merge files

    Relies on BBTools to handle its own functionality and errors.
    0 indicates success, 256 for any errors

    Returns a status code
    """
    open(f"{f_base_path}processing/{f_sra_acc}.repair.started", "w").close()
    repair_code = os.system(
        f"repair.sh overwrite=true in={file_pair[0]} in2={file_pair[1]} \
        out={f_base_path}processing/{f_sra_acc}_1.rep.fq out2={f_base_path}processing/{f_sra_acc}_2.rep.fq outs={f_base_path}processing/{f_sra_acc}_sing.rep.fq"
    )
    if repair_code == 0:
        os.remove(f"{f_base_path}processing/{f_sra_acc}.repair.started")
    return repair_code


def bbtools_process(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to do the logic for merging, and if needed repairing the raw paired fastq files.

    Parameters:
    f_base_path - path of directory where files are / will be written in fastq or processing subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    Calls functions to merge, and if needed, repair paired fastqs.

    Logic path -  If merging has already been succesfully completed -> return success
                  elif repairs were previously attempted but not completed -> retry repair and merge, return success state
                  elif repairs were previoulsy successful, but not merging -> merge, return success state
                  else -> attempt initial merge, repair if needed, return success state
                  self calls when possible

    Relies on BBTools to handle its own functionality and erros for the most part.
    0 indicates success, 256 for any errors

    Returns a status code, 0 for success or pre-existing finished merge, -1 for unable to find raw fastqs, 256 for bbtools errors
    """
    if (
        os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.merged.fq")
        and os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.un1.fq")
        and os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.un2.fq")
    ) and not os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.merge.started"):
        bbtools_return_code = 0
    elif os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.repair.started"):
        # retry repair, merge if successful
        # check for raw fastqs
        file_pair = find_fastqs(f_base_path, f_sra_acc)
        if isinstance(file_pair, tuple) and (
            len(file_pair) == 2 or len(file_pair) == 3
        ):
            repair_code = repair_files(f_base_path, f_sra_acc, file_pair)
            bbtools_return_code = repair_code
            if repair_code == 0:
                # re-attempting merge
                merge_code = bbtools_process(f_base_path, f_sra_acc)
                bbtools_return_code = merge_code
        else:
            bbtools_return_code = -1
    elif (
        os.path.isfile(f"{f_base_path}processing/{f_sra_acc}_1.rep.fq")
        and os.path.isfile(f"{f_base_path}processing/{f_sra_acc}_2.rep.fq")
        and os.path.isfile(f"{f_base_path}processing/{f_sra_acc}_sing.rep.fq")
    ):
        # repiar already done, retry merge
        merge_code = bbmerge_files(
            f_base_path,
            f_sra_acc,
            (
                f"{f_base_path}processing/{f_sra_acc}_1.rep.fq",
                f"{f_base_path}processing/{f_sra_acc}_2.rep.fq",
            ),
        )
        bbtools_return_code = merge_code
    else:
        # initial merge attempt
        # check for raw fastqs
        file_pair = find_fastqs(f_base_path, f_sra_acc)
        if isinstance(file_pair, tuple) and (len(file_pair) in (2, 3)):
            open(f"{f_base_path}processing/{f_sra_acc}.merge.started", "w").close()
            merge_code = bbmerge_files(f_base_path, f_sra_acc, file_pair)
            if merge_code == 0:
                bbtools_return_code = merge_code
            else:
                open(f"{f_base_path}processing/{f_sra_acc}.repair.started", "w").close()
                repair_remerge_code = bbtools_process(f_base_path, f_sra_acc)
                bbtools_return_code = repair_remerge_code
        else:
            bbtools_return_code = -1
    return bbtools_return_code


def concat_files(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to concatenate merged and unmergable reads

    Parameters:
    f_base_path - path of directory files will be read/written in the ./processing/ subfolder - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    find read files from previous processing and uses system cat command to concatenate them

    Returns a status code from command call, 0 for success or pre-existing finished cat, -1 if files form previous processing can't all be found,
    256 for cat errors (should never be returned)
    """
    # check for pre-existing finished cat
    if os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.all.fq") and not os.path.isfile(
        f"{f_base_path}processing/{f_sra_acc}.cat.started"
    ):
        cat_code = 0
    else:
        file_list = []
        # find the files from previous processing
        if (
            os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.merged.fq")
            and os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.un1.fq")
            and os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.un2.fq")
        ):
            file_list = [
                f"{f_base_path}processing/{f_sra_acc}.merged.fq",
                f"{f_base_path}processing/{f_sra_acc}.un1.fq",
                f"{f_base_path}processing/{f_sra_acc}.un2.fq",
            ]
            if os.path.isfile(f"{f_base_path}processing/{f_sra_acc}_sing.rep.fq"):
                file_list.append(f"{f_base_path}processing/{f_sra_acc}_sing.rep.fq")
            if os.path.isfile(f"{f_base_path}fastqs/{f_sra_acc}.fastq.gz"):
                os.system(f"gzip -d -k {f_base_path}fastqs/{f_sra_acc}.fastq.gz")
                file_list.append(f"{f_base_path}fastqs/{f_sra_acc}.fastq")

        if file_list:
            open(f"{f_base_path}processing/{f_sra_acc}.cat.started", "w").close()
            cat_code = os.system(
                f"cat {' '.join(file_list)} > {f_base_path}processing/{f_sra_acc}.all.fq"
            )
            if cat_code == 0:
                os.remove(f"{f_base_path}processing/{f_sra_acc}.cat.started")
            if os.path.isfile(f"{f_base_path}fastqs/{f_sra_acc}.fastq"):
                os.remove(f"{f_base_path}fastqs/{f_sra_acc}.fastq")
        else:
            print(f"can't file all files to concatenate for {f_sra_acc}")
            cat_code = -1
    return cat_code


def collapse_file(f_base_path: str, f_sra_acc: str, file: str) -> int:
    """
    Called to dereplicate reads

    Parameters:
    f_base_path - path of directory where files will be read/written in subfolders - string
    f_sra_acc - accession for the SRA sample - string
    file - full path for file to be collapsed

    Functionality:
    uses fastx toolkit's collapser to dereplicate reads
    writes output to fastas folder

    Returns a status code from command call, 0 for success

    """
    open(f"{f_base_path}fastas/{f_sra_acc}.col.started", "w").close()
    collapse_code = os.system(
        f"fastx_collapser -v -i {file} -o {f_base_path}fastas/{f_sra_acc}.collapsed.fa"
    )
    if collapse_code == 0:
        os.remove(f"{f_base_path}fastas/{f_sra_acc}.col.started")
    return collapse_code


def dereplicate_reads(f_base_path: str, f_sra_acc: str) -> int:
    """
    Called to perform logic for dereplicating reads

    Parameters:
    f_base_path - path of directory where files will be read/written in the subfolders - string
    f_sra_acc - accession for the SRA sample - string

    Functionality:
    finds paired read concatenated file or raw single read fastq file and sends to collapsing function

    Returns a status code from command call, 0 for success or pre-existing finished collapse, -2 if input file can't all be found
    """
    # check for pre-existing finished derep
    if os.path.isfile(
        f"{f_base_path}fastas/{f_sra_acc}.collapsed.fa"
    ) and not os.path.isfile(f"{f_base_path}fastas/{f_sra_acc}.col.started"):
        derep_code = 0
    else:
        if os.path.isfile(f"{f_base_path}processing/{f_sra_acc}.all.fq"):
            derep_code = collapse_file(
                f_base_path, f_sra_acc, f"{f_base_path}processing/{f_sra_acc}.all.fq"
            )
        else:
            fastq_file = find_fastqs(f_base_path, f_sra_acc)
            if isinstance(fastq_file, tuple) and len(fastq_file) == 1:
                os.system(f"gzip -d -k {fastq_file[0]}")
                derep_code = collapse_file(f_base_path, f_sra_acc, fastq_file[0][:-3])
                os.remove(fastq_file[0][:-3])
            else:
                print(f"Error finding single read fastq to collapse for {f_sra_acc}")
                derep_code = -2
    return derep_code


def preprocess_sra(f_base_path: str, f_sra_acc: str, read_type: int) -> int:
    """
    Called to process raw read fastqs to be ready for mapping
    for the stand alone script

    Parameters:
    f_base_path - path of directory where repaired files will be read/ written in the subfolders - string
    f_sra_acc - accession for the SRA sample - string
    read_type - 1 or 2, for single or paired reads respectively - int

    Functionality:
    Calls through a series of functions to process reads and checks the success of them before proceeding
    Single reads go straight to being dereplicated
    Paired reads are repaired if necessisary, merged, concatenated then dereplicted

    Returns a status code, 0 for success, -1 if the read type is bad, 1 for merging/repair failure,
    2 for concatenation failure, 3 for dereplication failure
    """
    if (not isinstance(read_type, int)) or (not read_type in (1, 2, 3)):
        print(
            f"Unknown read types found: {read_type}\n Should be either 1, 2 or 3 for single, paired or mixed reads respectively"
        )
        preproc_code = -1
        print(type(read_type))
    elif read_type in (2, 3):
        merge_code = bbtools_process(f_base_path, f_sra_acc)
        if merge_code == 0:
            concat_code = concat_files(f_base_path, f_sra_acc)
            if concat_code == 0:
                collapse_code = dereplicate_reads(f_base_path, f_sra_acc)
                if collapse_code == 0:
                    preproc_code = 0
                else:
                    preproc_code = 3
            else:
                preproc_code = 2
        else:
            preproc_code = 1
    elif read_type == 1:
        collapse_code = dereplicate_reads(f_base_path, f_sra_acc)
        if collapse_code == 0:
            preproc_code = 0
        else:
            preproc_code = 3
    return preproc_code


if __name__ == "__main__":
    """Stand alone script.  Takes a filename with arguement '-i' that holds SRA accessions and pre-processes fastq files of those accessions"""

    args = arg_parse()
    BASE_PATH = os.getcwd().split("SHED")[0] + "SHED/backend/"
    # check to see if files with SRA accession or meta data exist before pulling accession list
    file_name = ""
    if args.file:
        file_name = args.file
    elif os.path.isfile("SraRunTable.csv"):
        file_name = "SraRunTable.csv"
    elif os.path.isfile("SraRunTable.txt"):
        file_name = "SraRunTable.txt"
    else:
        print("No SRA accession list or metadata files found.")
    if file_name:
        accession_list = get_accessions(args.file)
        if isinstance(accession_list, list):
            if not os.path.isdir(f"{BASE_PATH}fastas/"):
                os.mkdir(f"{BASE_PATH}fastas/")
            if not os.path.isdir(f"{BASE_PATH}processing/"):
                os.mkdir(f"{BASE_PATH}processing/")
            for sra_acc in accession_list:
                print(sra_acc)

                status_code = preprocess_sra(
                    BASE_PATH, sra_acc, len(find_fastqs(BASE_PATH, sra_acc))
                )
                print(status_code)
