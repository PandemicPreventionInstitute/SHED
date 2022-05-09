#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_vc module using pytest
Last edited on 5-7-22
"""

import os
import sys
import pytest

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend")
from modules import sra_vc

TestPath = os.getcwd().split("SHED")[0] + "SHED/backend/tests"


class TestVC:
    """Tests for mapping module"""

    def  test_bad_acc(self):
        # bad sra
        assert sra_vc.vc_sams("", 2) == -1

    def  test_no_file_vc(self):
        # no file
        assert sra_vc.vc_sams("", "not.a.SRA") == 1

    def  test_empty_sam(self):
        # empty file
        assert sra_vc.vc_sams(TestPath, "Empty") == -2

    def  test_unfinished_vc(self):
        # unfinished vc
        assert sra_vc.vc_sams(TestPath, "UnfinishedVC") == 0

    def  test_finished_vc(self):
        # finished vc
        assert sra_vc.vc_sams(TestPath, "FinishedVC") == 0

    def  test_fresh_vc(self):
        # fresh good vc
        assert sra_vc.vc_sams(TestPath, "FreshVC") == 0

    def  test_vc_output(self):
        # output check
        with open(f"{TestPath}/tsvs/CheckVC_AA_covars.tsv", "r") as check:
            with open(f"{TestPath}/tsvs/FreshVC_AA_covars.tsv", "r") as fresh:
                assert check.readlines()[1:] == fresh.readlines()[1:]
