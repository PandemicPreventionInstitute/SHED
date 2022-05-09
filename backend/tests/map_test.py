#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_map module using pytest
Last edited on 5-7-22
"""

import os
import sys
import pytest

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend")
from modules import sra_map

TestPath = os.getcwd().split("SHED")[0] + "SHED/backend/tests"

class TestMaping:
    """Tests for mapping module"""

    def  test_bad_acc(self):
        # no str accession passed
        assert sra_map.map_reads("", 2) == -1

    def  test_no_file_map(self):
        # no fasta / bad path / etc
        assert sra_map.map_reads("", "not.a.file") == 1

    def  test_preexisting_map(self):
        # pre-existing finished mapping
        assert sra_map.map_reads(TestPath, "FinishedMapping") == 0

    def  test_unfinished_map(self):
        # unfinished mapping
        assert sra_map.map_reads(TestPath, "UnfinishedMapping") == 0

    def  test_fresh_map(self):
        # fresh map
        assert sra_map.map_reads(TestPath, "FreshMapping") == 0

    def  test_outputs_map(self):
        # output check
        with open(f"{TestPath}/sams/TestCheck.sam", "r") as check:
            with open(f"{TestPath}/sams/FreshMapping.sam", "r") as fresh:
                assert check.read() == fresh.read()
