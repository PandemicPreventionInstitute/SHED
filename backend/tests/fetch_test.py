#!/bin/env python3

'''
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 4-6-22
'''

import os
import sys
import pytest
sys.path.insert(0, os.getcwd().split('SHED')[0]+'SHED/backend' )
import modules.sra_fetch as fetch

def test_get_accessions():
# testing get_accessions function
# bad filename
    assert fetch.get_accessions('probably.a.non-existing.file') == 1

# empty file
    assert fetch.get_accessions('./tests/TestEmptySraList.txt') == 2

# no valid accessions
    assert fetch.get_accessions('./tests/TestBadSraList.txt') == 2

# no real accessions
    assert fetch.get_accessions('./tests/TestBadSraList2.txt') == ['SRR00000001']

# good file
    assert fetch.get_accessions('./tests/TestMixedSraList.txt') == ['ERR5019844', 'SRR15294802', 'SRR17888010', 'SRR15240439', 'SRR17887900']

def test_fetching():
# testing fetching function
# empty list
    assert fetch.fetching([]) == 1
# not a list
    assert fetch.fetching(2) == 1
# list of non strings, error handled by sra toolkit
    assert fetch.fetching([2, ['a']]) == 0
# fake SRA accession, error handled by sra toolkit
    assert fetch.fetching(['SRR00000001']) == 0
# good SRA accession
    assert fetch.fetching(['SRR17887900']) == 0


