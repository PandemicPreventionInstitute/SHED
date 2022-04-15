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
import modules.sra_file_parse as file_parse

base_path = os.getcwd().split('SHED')[0]+'SHED/backend/tests/'

class TestGetAccessions:
    '''Tests of get_accessions function in sra_file_parse'''

    def test_non_existing_file_get(self):
    # bad filename
        assert file_parse.get_accessions('probably.a.non-existing.file') == 1

    def test_empty_file_get(self):
    # empty file
        assert file_parse.get_accessions('./tests/TestEmptySraList.txt') == 2

    def test_bad_sra_acc_get(self):
    # no valid accessions
        assert file_parse.get_accessions('./tests/TestBadSraList.txt') == 2

    def test_fake_sra_acc_get(self):
    # no real accessions
        assert file_parse.get_accessions('./tests/TestBadSraList2.txt') == ['SRR00000001']

    def test_good_sra_acc_get(self):
    # good file, mix of good and bad SRAs
        assert file_parse.get_accessions('./tests/TestMixedSraList.txt') == ['ERR5019844', 'SRR15294802', 'SRR17888010', 'SRR15240439', 'SRR17887900']


class TestFindFastqs:
    ''' testing find_fastqs function in sra_file_parse'''


    def test_no_fastqs(self):
    # no fastqs
        assert file_parse.find_fastqs(base_path, 'not.an.sra') == ()

    def test_single_fastqs(self):
    # single fastqs
        single_tuple = tuple(['/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/single.test_1.fastq.gz'])
        assert file_parse.find_fastqs(base_path, 'single.test') == single_tuple

    def test_paired_fastqs(self):
    # paired fastqs
        assert file_parse.find_fastqs(base_path, 'paired.test') \
            == (('/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/paired.test_1.fastq.gz', '/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/paired.test_2.fastq.gz'))

    def test_mismatched_fastqs(self):
    # single and paired
        assert file_parse.find_fastqs(base_path, '3fastqtest') == (('/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/3fastqtest_1.fastq.gz', '/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/3fastqtest_2.fastq.gz', '/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/3fastqtest.fastq.gz'))
