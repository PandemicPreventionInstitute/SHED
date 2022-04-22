#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 4-22-22
"""

import os
import sys
import pytest

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend")
import modules.sra_preproc as preproc

TestPath = os.getcwd().split("SHED")[0] + "SHED/backend/tests/"


class TestBBToolsProcess:
    """Tests of merge and repair_files function in sra_preproc"""

    def test_sra_bbtools(self):
        # bad sra (no fastqs)
        assert preproc.bbtools_process(TestPath, "sra_acc") == -1

    def test_bad_reads_bbtools(self):
        # bad reads (irrepairable)
        assert preproc.bbtools_process(TestPath, "bad_reads") == 256

    def test_repairable_reads_bbtools(self):
        # bad reads (repairable)
        assert preproc.bbtools_process(TestPath, "repairable_reads") == 0

    def test_good_reads_bbtools(self):
        # good files
        assert preproc.bbtools_process(TestPath, "good_reads") == 0


class TestConcatFiles:
    """Tests of concat_files function in sra_preproc"""

    def test_no_files_cat(self):
        # empty list
        assert preproc.concat_files(TestPath, "sra_acc") == -1

    def test_empty_file_cat(self):
        # empty/good file
        assert preproc.concat_files(TestPath, "empty_file_cat_test") == 0


class TestDereplicateReads:
    """Tests of dereplicate_reads function in sra_preproc"""

    def test_non_existing_file_derep(self):
        # bad filename
        assert preproc.dereplicate_reads(TestPath, "not.an.sra.acc") == -2

    def test_empty_file_derep(self):
        # empty file
        assert preproc.dereplicate_reads(TestPath, "cat.already.finished") == 0

    def test_bad_reads_derep(self):
        # bad reads
        assert preproc.dereplicate_reads(TestPath, "bad_reads_derep") == 256

    def test_qual_mismatch_derep(self):
        # qual. score lenght mismatch
        assert preproc.dereplicate_reads(TestPath, "qual_mismatch_derep") == 256

    def test_good_reads_derep(self):
        # good file
        assert preproc.dereplicate_reads(TestPath, "good_reads_derep") == 0
