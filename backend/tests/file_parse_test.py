#!/bin/env python3

'''
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 4-9-22
'''

import os
import sys
import pytest
sys.path.insert(0, os.getcwd().split('SHED')[0]+'SHED/backend' )
import modules.sra_file_parse as file_parse

class TestGetAccessions:
    '''Tests of get_accessions function in sra_fetch'''

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
