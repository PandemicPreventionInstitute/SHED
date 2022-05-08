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
        
    # def test_lineage_agg
    
    
    # def test_covar_agg
    
    
    # def test_consensus_agg
    