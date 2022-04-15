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
import modules.sra_fetch as fetch

base_path = os.getcwd().split('SHED')[0]+'SHED/backend/tests/'

class TestFetching:
    '''Tests of get_fastqs function in sra_fetch.  All will fail if NCBI SRA can't be reached.'''
    def test_empty_filename_fetch(self):
    # empty filename
        assert fetch.get_fastqs(base_path, '') == -1

    def test_not_a_str_fetch(self):
    # not a string
        assert fetch.get_fastqs(base_path, 2) == -1

    def test_fake_sra_acc_fetch(self):
    # fake SRA accession, error handled by sra toolkit
        assert fetch.get_fastqs(base_path, 'SRR00000001') == (768, 768)
        os.remove(f"{base_path}fastqs/SRR00000001.fetch.started")

    def test_good_sra_acc_fetch(self):
    # good SRA accession
        assert fetch.get_fastqs(base_path, 'SRR17887900') == (0, 0)
        os.remove(f"{base_path}fastqs/SRR17887900_1.fastq.gz")
        os.remove(f"{base_path}fastqs/SRR17887900_2.fastq.gz")

    def test_already_fetched_sra_acc_fetch(self):
    # good SRA accession
        assert fetch.get_fastqs(base_path, 'paired.test') == (0, 0)