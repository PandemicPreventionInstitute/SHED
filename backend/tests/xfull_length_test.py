#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_output_aggregate module using pytest
Last edited on 5-9-22
"""

import os
import sys
import pytest

TestPath = os.getcwd().split("SHED")[0] + "SHED/backend/tests"
class TestFullPipeline:

    def test_full_run(self):
        assert os.system(f"python3 {TestPath[:-5]}pipeline.py -d {TestPath} -i {TestPath}/lists/FullTestList.txt") == 0

    def check_output_finishes(self):
        assert (
            os.path.isfile(f"{TestPath}/fastas/SRR18539183.consensus.fasta") and
            os.path.isfile(f"{TestPath}/fastas/SRR18543413.consensus.fasta") and
            os.path.isfile(f"{TestPath}/fastas/SRR15240636.consensus.fasta") and
            os.path.isfile(f"{TestPath}/fastas/SRR18543439.consensus.fasta") and
            os.path.isfile(f"{TestPath}/fastas/SRR18539299.consensus.fasta") and
            os.path.isfile(f"{TestPath}/fastas/SRR18541018.consensus.fasta") and
            os.path.isfile(f"{TestPath}/fastas/SRR18543570.consensus.fasta") and
            os.path.isfile(f"{TestPath}/fastas/SRR18115715.consensus.fasta") and
            os.path.isfile(f"{TestPath}/fastas/SRR18543378.consensus.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR18539183.lineages.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR18543413.lineages.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR15240636.lineages.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR18543439.lineages.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR18539299.lineages.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR18541018.lineages.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR18543570.lineages.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR18115715.lineages.fasta") and
            os.path.isfile(f"{TestPath}/tsvs/SRR18543378.lineages.fasta")
        )

