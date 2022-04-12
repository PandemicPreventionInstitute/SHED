#!/bin/env python3

'''
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 4-12-22
'''

import os
import sys
import pytest
sys.path.insert(0, os.getcwd().split('SHED')[0]+'SHED/backend' )
import modules.sra_preproc as preproc

base_path = os.getcwd().split('SHED')[0]+'SHED/backend/tests/'

class TestRepairFiles:
    '''Tests of repair_files function in sra_preproc'''

    def test_empty_file_list_repair(self):
    # empty list
        assert preproc.repair_files(base_path, 'sra_acc', []) == -1

    def test_bad_filename_repair(self):
    # bad file names
        assert preproc.repair_files(base_path, 'sra_acc', [base_path+'fastqs/paired.test_1.fastq', \
            'probably.a.non-existing.file']) == 256

    def test_bad_reads_repair(self):
    # bad reads
        assert preproc.repair_files(base_path, 'bad_read_repair_test', [base_path+'fastqs/bad_reads_1.fastq', \
            base_path+'fastqs/bad_reads_2.fastq']) == 256

    def test_good_file_list_repair(self):
    # good files
        assert preproc.repair_files(base_path, 'SRR17887900', [base_path+'fastqs/SRR17887900_1.fastq', base_path+'fastqs/SRR17887900_2.fastq']) == \
            [f"{base_path}processing/SRR17887900_1.rep.fq", f"{base_path}processing/SRR17887900_2.rep.fq", \
                f"{base_path}processing/SRR17887900_sing.rep.fq"]

class TestMergeFiles:
    '''Tests of merge_files function in sra_preproc'''

    def test_empty_file_list_merge(self):
    # empty list
        assert preproc.merge_files(base_path, 'sra_acc', []) == -1

    def test_bad_filename_merge(self):
    # bad file names
        assert preproc.merge_files(base_path, 'sra_acc', [base_path+'fastqs/paired.test_1.fastq', \
            'probably.a.non-existing.file']) == 256

    def test_bad_reads_merge(self):
    # bad reads
        assert preproc.merge_files(base_path, 'bad_read_merge_test', [base_path+'fastqs/bad_reads_1.fastq', \
            base_path+'fastqs/bad_reads_2.fastq']) == 256

    def test_good_file_list_merge(self):
    # good files
        assert preproc.merge_files(base_path, 'SRR17887900', [base_path+'fastqs/SRR17887900_1.fastq', base_path+'fastqs/SRR17887900_2.fastq']) == \
            [f"{base_path}processing/SRR17887900.merged.fq", f"{base_path}processing/SRR17887900.un1.fq", \
                f"{base_path}processing/SRR17887900.un2.fq"]

class TestConcatFiles:
    '''Tests of concat_files function in sra_preproc'''

    def test_empty_file_list_cat(self):
    # empty list
        assert preproc.concat_files(base_path, 'sra_acc', []) == -1

    def test_empty_file_cat(self):
    # empty file
        assert preproc.concat_files(base_path, 'mergerep', [base_path+'processing/mergerep.finished.merged.fq', \
            base_path+'processing/mergerep.finished.un1.fq']) == '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/mergerep.all.fq'

    def test_bad_filename_cat(self):
    # bad file names
        assert preproc.concat_files(base_path, 'sra_acc', ['probably.a.non-existing.file']) == 256

    def test_good_file_list_cat(self):
    # good files
        assert preproc.concat_files(base_path, 'good_file_cat_test', [base_path+'processing/good_file_cat_test.merged.fq']) == \
            '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/good_file_cat_test.all.fq'



class TestDereplicateReads:
    '''Tests of dereplicate_reads function in sra_preproc'''

    def test_non_existing_file_derep(self):
    # bad filename
        assert preproc.dereplicate_reads(base_path, 'SRAtest', 'probably.a.non-existing.file') == 256

    def test_empty_file_derep(self):
    # empty file
        assert preproc.dereplicate_reads(base_path, 'cat.finished', base_path+'processing/cat.finished.all.fq') == 256

    def test_bad_reads_derep(self):
    # bad reads
        assert preproc.dereplicate_reads(base_path, 'bad_reads', base_path+'processing/bad_reads.all.fq') == 256

    def test_qual_mismatch_derep(self):
    # qual. score lenght mismatch
        assert preproc.dereplicate_reads(base_path, 'qual_mismatch', base_path+'processing/qual_mismatch.all.fq') == 256

    def test_good_reads_derep(self):
    # good file
        assert preproc.dereplicate_reads(base_path, 'good_reads', base_path+'processing/good_reads.all.fq') == base_path+'fastas/good_reads.collapsed.fa'


# # class TestPreprocessSra:

# no progress

# at repair_files

# at merge_files

# at concat_files

# at dereplicate_reads

