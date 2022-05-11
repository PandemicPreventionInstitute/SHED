#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 5-8-22
"""

import os
import sys
import pytest


@pytest.fixture(scope="session", autouse=True)
def necessary_files():
    # setup
    TestPath = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))
    os.system(f"tar -xzf {TestPath}/testfiles.tar.gz -C {TestPath}")

    yield
    # tear down
    os.system(f"rm -rf {TestPath}/lists")
    os.system(f"rm -rf {TestPath}/fastas")
    os.system(f"rm -rf {TestPath}/fastqs")
    os.system(f"rm -rf {TestPath}/SRAs")
    os.system(f"rm -rf {TestPath}/processing")
    os.system(f"rm -rf {TestPath}/data")
    os.system(f"rm -rf {TestPath}/sams")
    os.system(f"rm -rf {TestPath}/tsvs")
    os.system(f"rm -rf {TestPath}/Sam_refiner.py")
    os.system(f"rm -rf {TestPath}/*.tsv")
