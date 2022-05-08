#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_output_aggregate module using pytest
Last edited on 5-8-22
"""

import os
import sys
import pytest

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend")
import modules.sra_output_aggregate as aggy

TestPath = os.getcwd().split("SHED")[0] + "SHED/backend/tests"

class TestAggNTs:

    def test_bad_sra(self):
        # bad sra
        assert aggy.agg_nt_calls(TestPath, 2) == 1

    def test_no_file(self):
        # no file
        assert aggy.agg_nt_calls(TestPath, "NotAnSraAcc") == 1

    def test_finished(self):
        # already done
        assert aggy.agg_nt_calls(TestPath, "NoConsensus") == 0

    def test_empty_tsv(self):
        # empty file
        assert aggy.agg_nt_calls(TestPath, "EmptyTSV") == 2

    def test_good_calls(self):
        # all good
        assert aggy.agg_nt_calls(TestPath, "GoodTSV") == 0

    def test_agg_output(self):
        # agg output check
        with open(f"{TestPath}/CheckNTAgg.tsv", "r") as checked:
            with open(f"{TestPath}/NT_Calls.tsv", "r") as good:
                assert checked.read() ==  good.read()

class TestAggCovars:

    def test_bad_sra(self):
        # bad sra
        assert aggy.agg_vars(TestPath, 2) == 1

    def test_no_file(self):
        # no file
        assert aggy.agg_vars(TestPath, "NotAnSraAcc") == 1

    def test_finished(self):
        # already done
        assert aggy.agg_vars(TestPath, "FinishedAgg") == 0

    def test_empty_tsv(self):
        # empty file
        assert aggy.agg_vars(TestPath, "EmptyTSV") == 1

    def test_good_covars(self):
        # all good
        assert aggy.agg_vars(TestPath, "GoodTSV") == 0

    def test_agg_output(self):
        # agg output check
        with open(f"{TestPath}/CheckCovars.tsv", "r") as checked:
            with open(f"{TestPath}/Polymorphs.tsv", "r") as good:
                assert checked.read() ==  good.read()

