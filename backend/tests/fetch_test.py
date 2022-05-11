#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 5-11-22
"""

import os
import sys
import pytest

sys.path.insert(1, os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir, os.pardir)))
import modules.sra_fetch as fetch

TestPath = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))


class TestFetching:
    """Tests of get_fastqs function in sra_fetch.  All will fail if NCBI SRA can't be reached."""

    def test_empty_filename_fetch(self):
        # empty filename
        assert fetch.get_fastqs(TestPath, "") == -1

    def test_not_a_str_fetch(self):
        # not a string
        assert fetch.get_fastqs(TestPath, 2) == -1

    def test_fake_sra_acc_fetch(self):
        # fake SRA accession, error handled by sra toolkit
        assert fetch.get_fastqs(TestPath, "SRR00000001") == (768, 768)

    def test_good_sra_acc_fetch(self):
        # good SRA accession
        assert fetch.get_fastqs(TestPath, "SRR17887900") == (0, 0)

    def test_already_fetched_sra_acc_fetch(self):
        # good SRA accession
        assert fetch.get_fastqs(TestPath, "paired.test") == (0, 0)
