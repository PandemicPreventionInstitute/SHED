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
import modules.sra_fetch as fetch

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