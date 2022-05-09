#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_output_aggregate module using pytest
Last edited on 5-8-22
"""

import os
import sys
import pytest

TestPath = os.getcwd().split("SHED")[0] + "SHED/backend/tests"
class TestFullPipeline:

    def test_full_run(self):
        assert os.system(f"python3 {TestPath[:-5]}pipeline.py -d {TestPath} -i {TestPath}/lists/FullTestList.txt") == 0

    # test aggregate outputs

    def test_lineage_agg(self):
        with open(f"{TestPath}/FullLins.tsv", "r") as checked:
            with open(f"{TestPath}/Lineages.tsv", "r") as good:
                with open(f"{TestPath}/SoloFullLins.tsv", "r") as solocheck:
                    good_read = good.read()
                    file_check1 = checked.read() ==  good_read
                    file_check2 = solocheck.read() == good_read
                    assert file_check1 or file_check2

    def test_covar_agg(self):
        with open(f"{TestPath}/FullNTs.tsv", "r") as checked:
            with open(f"{TestPath}/NT_Calls.tsv", "r") as good:
                with open(f"{TestPath}/SoloFullNTs.tsv", "r") as solocheck:
                    good_read = good.read()
                    file_check1 = checked.read() ==  good_read
                    file_check2 = solocheck.read() == good_read
                    assert file_check1 or file_check2

    def test_consensus_agg(self):
        with open(f"{TestPath}/FullCons.tsv", "r") as checked:
            with open(f"{TestPath}/Consensus.tsv", "r") as good:
                with open(f"{TestPath}/SoloFullCons.tsv", "r") as solocheck:
                    good_read = good.read()
                    file_check1 = checked.read() ==  good_read
                    file_check2 = solocheck.read() == good_read
                    assert file_check1 or file_check2
