#!/bin/env python3

'''
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 4-14-22
'''

import os
import sys
import pytest
sys.path.insert(0, os.getcwd().split('SHED')[0]+'SHED/backend' )
import modules.sra_preproc as preproc

base_path = os.getcwd().split('SHED')[0]+'SHED/backend/tests/'

class TestBBToolsProcess:
    '''Tests of merge and repair_files function in sra_preproc'''

    def test_sra_bbtools(self):
    # bad sra (no fastqs)
        assert preproc.bbtools_process(base_path, 'sra_acc') == -1

    def test_bad_reads_bbtools(self):
    # bad reads (irrepairable)
        assert preproc.bbtools_process(base_path, 'bad_reads') == 256
        os.remove(f"{base_path}processing/bad_reads_1.rep.fq")
        os.remove(f"{base_path}processing/bad_reads_2.rep.fq")
        os.remove(f"{base_path}processing/bad_reads_sing.rep.fq")
        os.remove(f"{base_path}processing/bad_reads.merge.started")
        os.remove(f"{base_path}processing/bad_reads.repair.started")
        os.remove(f"{base_path}processing/bad_reads.merged.fq")
        os.remove(f"{base_path}processing/bad_reads.un1.fq")
        os.remove(f"{base_path}processing/bad_reads.un2.fq")
        
    def test_repairable_reads_bbtools(self):
    # bad reads (repairable)
        assert preproc.bbtools_process(base_path, 'repairable_reads') == 0
        os.remove(f"{base_path}processing/repairable_reads_1.rep.fq")
        os.remove(f"{base_path}processing/repairable_reads_2.rep.fq")
        os.remove(f"{base_path}processing/repairable_reads_sing.rep.fq")
        os.remove(f"{base_path}processing/repairable_reads.merged.fq")
        os.remove(f"{base_path}processing/repairable_reads.un1.fq")
        os.remove(f"{base_path}processing/repairable_reads.un2.fq")

    def test_good_reads_bbtools(self):
    # good files
        assert preproc.bbtools_process(base_path, 'good_reads') == 0
        os.remove(f"{base_path}processing/good_reads.merged.fq")
        os.remove(f"{base_path}processing/good_reads.un1.fq")
        os.remove(f"{base_path}processing/good_reads.un2.fq")

class TestConcatFiles:
    '''Tests of concat_files function in sra_preproc'''

    def test_no_files_cat(self):
    # empty list
        assert preproc.concat_files(base_path, 'sra_acc') == -1

    def test_empty_file_cat(self):
    # empty/good file
        assert preproc.concat_files(base_path, 'empty_file_cat_test') == 0
        os.remove(f"{base_path}processing/empty_file_cat_test.all.fq")



class TestDereplicateReads:
    '''Tests of dereplicate_reads function in sra_preproc'''

    def test_non_existing_file_derep(self):
    # bad filename
        assert preproc.dereplicate_reads(base_path, 'not.an.sra.acc') == -2

    def test_empty_file_derep(self):
    # empty file
        assert preproc.dereplicate_reads(base_path, 'cat.already.finished') == 0

    def test_bad_reads_derep(self):
    # bad reads
        assert preproc.dereplicate_reads(base_path, 'bad_reads_derep') == 256
        os.remove(f"{base_path}fastas/bad_reads_derep.col.started")
        os.remove(f"{base_path}fastas/bad_reads_derep.collapsed.fa")

    def test_qual_mismatch_derep(self):
    # qual. score lenght mismatch
        assert preproc.dereplicate_reads(base_path, 'qual_mismatch_derep') == 256
        os.remove(f"{base_path}fastas/qual_mismatch_derep.col.started")
        os.remove(f"{base_path}fastas/qual_mismatch_derep.collapsed.fa")

    def test_good_reads_derep(self):
    # good file
        assert preproc.dereplicate_reads(base_path, 'good_reads_derep') == 0
        os.remove(f"{base_path}fastas/good_reads_derep.collapsed.fa")
