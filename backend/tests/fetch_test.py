#!/bin/env python3

'''
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 4-7-22
'''

import os
import sys
import pytest
sys.path.insert(0, os.getcwd().split('SHED')[0]+'SHED/backend' )
import modules.sra_fetch as fetch

class TestGetAccessions:
    '''Tests of get_accessions function in sra_fetch'''

    def test_non_existing_file_get(self):
    # bad filename
        assert fetch.get_accessions('probably.a.non-existing.file') == 1

    def test_empty_file_get(self):
    # empty file
        assert fetch.get_accessions('./tests/TestEmptySraList.txt') == 2

    def test_bad_sra_acc_get(self):
    # no valid accessions
        assert fetch.get_accessions('./tests/TestBadSraList.txt') == 2

    def test_fake_sra_acc_get(self):
    # no real accessions
        assert fetch.get_accessions('./tests/TestBadSraList2.txt') == ['SRR00000001']

    def test_good_sra_acc_get(self):
    # good file, mix of good and bad SRAs
        assert fetch.get_accessions('./tests/TestMixedSraList.txt') == ['ERR5019844', 'SRR15294802', 'SRR17888010', 'SRR15240439', 'SRR17887900']

class TestFetching:
    '''Tests of fetching function in sra_fetch'''

    def test_empty_list_fetch(self):
    # empty list
        assert fetch.fetching([]) == 1

    def test_not_a_list_fetch(self):
    # not a list
        assert fetch.fetching(2) == 1

    def test_non_string_list_fetch(self):
    # list of non strings, error handled by sra toolkit
        assert fetch.fetching([2, ['a']]) == 0

    def test_fake_sra_acc_fetch(self):
    # fake SRA accession, error handled by sra toolkit
        assert fetch.fetching(['SRR00000001']) == 0

    def test_good_sra_acc_fetch(self):
    # good SRA accession
        assert fetch.fetching(['SRR17887900']) == 0