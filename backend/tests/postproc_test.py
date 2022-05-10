#!/bin/env python3

"""
Writen by Devon Gregory
This script tests the workings of the sra_consensus and sra_lineage module using pytest
Last edited on 5-7-22
"""

import os
import sys
import pytest

sys.path.insert(1, os.getcwd().split("SHED")[0] + "SHED/backend")
from modules import sra_consensus
from modules import sra_lineage

TestPath = os.getcwd().split("SHED")[0] + "SHED/backend/tests"

class TestConsensus:

    def test_bad_sra(self):
        # bad sra
        assert sra_consensus.gen_consensus(TestPath, 2) == -1

    def test_no_file(self):
        # no file
        assert sra_consensus.gen_consensus(TestPath, "NotAnSraAcc") == 1

    def test_finished(self):
        # already done
        assert sra_consensus.gen_consensus(TestPath, "FinishedCon") == 0

    def test_empty_tsv(self):
        # empty file
        assert sra_consensus.gen_consensus(TestPath, "EmptyTSV") == 5

    def test_bad_tsv(self):
        # bad nt call format
        assert sra_consensus.gen_consensus(TestPath, "BadFormat") == 5

    def test_no_consensus(self):
        # good format, no consensus
        assert sra_consensus.gen_consensus(TestPath, "NoConsensus") == 2

    def test_good_consensus(self):
        # all good
        assert sra_consensus.gen_consensus(TestPath, "GoodTSV") == 0

    def test_samp_output(self):
        # samp output check
        with open(f"{TestPath}/fastas/Check.consensus.fasta", "r") as checked:
            with open(f"{TestPath}/fastas/GoodTSV.consensus.fasta", "r") as good:
                assert checked.read() ==  good.read()

    def test_agg_output(self):
        # agg output check
        with open(f"{TestPath}/CheckCon.tsv", "r") as checked:
            with open(f"{TestPath}/Consensus.tsv", "r") as good:
                assert checked.read() ==  good.read()


test_lin_dict = {
    'lineages': ['Alpha', 'Beta', 'Gamma', 'Delta', 'OmicronBA.1', 'OmicronBA.2'],
    913: {'Alpha': 'T'},
    3267: {'Alpha': 'T'},
    5388: {'Alpha': 'A'},
    5986: {'Alpha': 'T'},
    6954: {'Alpha': 'C'},
    14676: {'Alpha': 'T'},
    15279: {'Alpha': 'T'},
    16176: {'Alpha': 'C'},
    21765: {'Alpha': '-', 'OmicronBA.1': '-'},
    21766: {'Alpha': '-', 'OmicronBA.1': '-'},
    21767: {'Alpha': '-', 'OmicronBA.1': '-'},
    21768: {'Alpha': '-', 'OmicronBA.1': '-'},
    21769: {'Alpha': '-', 'OmicronBA.1': '-'},
    21770: {'Alpha': '-', 'OmicronBA.1': '-'},
    21991: {'Alpha': '-', 'OmicronBA.1': '-'},
    21992: {'Alpha': '-', 'OmicronBA.1': '-'},
    21993: {'Alpha': '-', 'OmicronBA.1': '-'},
    23063: {'Alpha': 'T', 'Beta': 'T', 'Gamma': 'T', 'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    23271: {'Alpha': 'A'},
    23604: {'Alpha': 'A', 'Delta': 'G', 'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    23709: {'Alpha': 'T'},
    24506: {'Alpha': 'G'},
    24914: {'Alpha': 'C'},
    26801: {'Alpha': 'T'},
    27972: {'Alpha': 'T'},
    28048: {'Alpha': 'T'},
    28111: {'Alpha': 'G'},
    28280: {'Alpha': 'C'},
    28281: {'Alpha': 'T'},
    28282: {'Alpha': 'A'},
    28977: {'Alpha': 'T'},
    174: {'Beta': 'T'},
    1059: {'Beta': 'T'},
    5230: {'Beta': 'T'},
    8660: {'Beta': 'T'},
    8964: {'Beta': 'T'},
    10323: {'Beta': 'G'},
    13843: {'Beta': 'T'},
    17999: {'Beta': 'T'},
    21614: {'Beta': 'T', 'Gamma': 'T'},
    21801: {'Beta': 'C'},
    22206: {'Beta': 'G'},
    22281: {'Beta': '-'},
    22282: {'Beta': '-'},
    22283: {'Beta': '-'},
    22284: {'Beta': '-'},
    22285: {'Beta': '-'},
    22286: {'Beta': '-'},
    22287: {'Beta': '-'},
    22288: {'Beta': '-'},
    22289: {'Beta': '-'},
    22299: {'Beta': 'T'},
    22813: {'Beta': 'T', 'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    23012: {'Beta': 'A', 'Gamma': 'A'},
    23664: {'Beta': 'T'},
    25563: {'Beta': 'T'},
    25904: {'Beta': 'T'},
    26456: {'Beta': 'T'},
    28253: {'Beta': 'T', 'Delta': '-'},
    28887: {'Beta': 'T'},
    733: {'Gamma': 'C'},
    2749: {'Gamma': 'T'},
    3828: {'Gamma': 'T'},
    5648: {'Gamma': 'C'},
    6319: {'Gamma': 'G'},
    6613: {'Gamma': 'G'},
    12778: {'Gamma': 'T'},
    13860: {'Gamma': 'T'},
    17259: {'Gamma': 'T'},
    21621: {'Gamma': 'A'},
    21638: {'Gamma': 'T', 'OmicronBA.2': '-'},
    21974: {'Gamma': 'T'},
    22132: {'Gamma': 'T'},
    22812: {'Gamma': 'C'},
    23525: {'Gamma': 'T', 'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    24642: {'Gamma': 'T'},
    25088: {'Gamma': 'T'},
    26149: {'Gamma': 'C'},
    28167: {'Gamma': 'A'},
    28512: {'Gamma': 'G'},
    28877: {'Gamma': 'T'},
    28878: {'Gamma': 'C'},
    28881: {'Gamma': 'A', 'Delta': 'T', 'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    28882: {'Gamma': 'A', 'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    28883: {'Gamma': 'C', 'OmicronBA.1': 'C', 'OmicronBA.2': 'C'},
    210: {'Delta': 'T'},
    15451: {'Delta': 'A'},
    16466: {'Delta': 'T'},
    21618: {'Delta': 'G', 'OmicronBA.2': 'T'},
    21987: {'Delta': 'A', 'OmicronBA.1': '-', 'OmicronBA.2': 'A'},
    22029: {'Delta': '-'},
    22030: {'Delta': '-'},
    22031: {'Delta': '-'},
    22032: {'Delta': '-'},
    22033: {'Delta': '-'},
    22034: {'Delta': '-'},
    22917: {'Delta': 'G'},
    22995: {'Delta': 'A', 'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    24410: {'Delta': 'A'},
    25469: {'Delta': 'T'},
    26767: {'Delta': 'C'},
    27638: {'Delta': 'C'},
    27752: {'Delta': 'T'},
    28248: {'Delta': '-'},
    28249: {'Delta': '-'},
    28250: {'Delta': '-'},
    28251: {'Delta': '-'},
    28252: {'Delta': '-'},
    28271: {'Delta': '-', 'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    28461: {'Delta': 'G'},
    29402: {'Delta': 'T'},
    29742: {'Delta': 'T'},
    2832: {'OmicronBA.1': 'G'},
    5386: {'OmicronBA.1': 'G'},
    6513: {'OmicronBA.1': '-'},
    6514: {'OmicronBA.1': '-'},
    6515: {'OmicronBA.1': '-'},
    8393: {'OmicronBA.1': 'A'},
    10029: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    10449: {'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    11283: {'OmicronBA.1': '-'},
    11284: {'OmicronBA.1': '-'},
    11285: {'OmicronBA.1': '-'},
    11286: {'OmicronBA.1': '-'},
    11287: {'OmicronBA.1': '-'},
    11288: {'OmicronBA.1': '-'},
    11289: {'OmicronBA.1': '-'},
    11290: {'OmicronBA.1': '-'},
    11291: {'OmicronBA.1': '-'},
    11537: {'OmicronBA.1': 'G'},
    13195: {'OmicronBA.1': 'C'},
    15240: {'OmicronBA.1': 'T'},
    18163: {'OmicronBA.1': 'G', 'OmicronBA.2': 'G'},
    21762: {'OmicronBA.1': 'T'},
    21846: {'OmicronBA.1': 'T'},
    21988: {'OmicronBA.1': '-'},
    21989: {'OmicronBA.1': '-'},
    21990: {'OmicronBA.1': '-'},
    21994: {'OmicronBA.1': '-'},
    21995: {'OmicronBA.1': '-'},
    22194: {'OmicronBA.1': '-'},
    22195: {'OmicronBA.1': '-'},
    22196: {'OmicronBA.1': '-'},
    22205: {'OmicronBA.1': 'insertGAGCCAGAA'},
    22578: {'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    22673: {'OmicronBA.1': 'C'},
    22674: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    22679: {'OmicronBA.1': 'C', 'OmicronBA.2': 'C'},
    22686: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    22882: {'OmicronBA.1': 'G', 'OmicronBA.2': 'G'},
    22898: {'OmicronBA.1': 'A'},
    22992: {'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    23013: {'OmicronBA.1': 'C', 'OmicronBA.2': 'C'},
    23040: {'OmicronBA.1': 'G', 'OmicronBA.2': 'G'},
    23048: {'OmicronBA.1': 'A'},
    23055: {'OmicronBA.1': 'G', 'OmicronBA.2': 'G'},
    23075: {'OmicronBA.1': 'C', 'OmicronBA.2': 'C'},
    23202: {'OmicronBA.1': 'A'},
    23599: {'OmicronBA.1': 'G', 'OmicronBA.2': 'G'},
    23854: {'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    23948: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    24130: {'OmicronBA.1': 'A'},
    24424: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    24469: {'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    24503: {'OmicronBA.1': 'T'},
    25000: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    25584: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    26270: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    26530: {'OmicronBA.1': 'G'},
    26577: {'OmicronBA.1': 'G', 'OmicronBA.2': 'G'},
    26709: {'OmicronBA.1': 'A', 'OmicronBA.2': 'A'},
    27259: {'OmicronBA.1': 'C', 'OmicronBA.2': 'C'},
    27807: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    28311: {'OmicronBA.1': 'T', 'OmicronBA.2': 'T'},
    28362: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    28363: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    28364: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    28365: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    28366: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    28367: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    28368: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    28369: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    28370: {'OmicronBA.1': '-', 'OmicronBA.2': '-'},
    670: {'OmicronBA.2': 'G'},
    2790: {'OmicronBA.2': 'T'},
    4184: {'OmicronBA.2': 'A'},
    4321: {'OmicronBA.2': 'T'},
    9344: {'OmicronBA.2': 'T'},
    9424: {'OmicronBA.2': 'G'},
    9534: {'OmicronBA.2': 'T'},
    9866: {'OmicronBA.2': 'T'},
    10198: {'OmicronBA.2': 'T'},
    10447: {'OmicronBA.2': 'A'},
    12880: {'OmicronBA.2': 'T'},
    15714: {'OmicronBA.2': 'T'},
    17410: {'OmicronBA.2': 'T'},
    19955: {'OmicronBA.2': 'T'},
    20055: {'OmicronBA.2': 'G'},
    21633: {'OmicronBA.2': '-'},
    21634: {'OmicronBA.2': '-'},
    21635: {'OmicronBA.2': '-'},
    21636: {'OmicronBA.2': '-'},
    21637: {'OmicronBA.2': '-'},
    21639: {'OmicronBA.2': '-'},
    21640: {'OmicronBA.2': '-'},
    21641: {'OmicronBA.2': '-'},
    22200: {'OmicronBA.2': 'G'},
    22688: {'OmicronBA.2': 'G'},
    22775: {'OmicronBA.2': 'A'},
    22786: {'OmicronBA.2': 'C'},
    26060: {'OmicronBA.2': 'T'},
    26858: {'OmicronBA.2': 'T'},
    27382: {'OmicronBA.2': 'C'},
    27383: {'OmicronBA.2': 'T'},
    27384: {'OmicronBA.2': 'C'},
    29510: {'OmicronBA.2': 'C'}
    }

class TestLineageDictGet:

    def test_no_file(self):
        # bad path
        assert sra_lineage.get_lineage_dict("/not/a/real/path") == 1

    def test_dict_match(self):
        # successful retreival
        assert sra_lineage.get_lineage_dict(TestPath) == test_lin_dict


class TestLineageAssign:

    def test_bad_sra(self):
        # bad sra
        assert sra_lineage.find_lineages(test_lin_dict, TestPath, 2) == -1

    def test_no_file(self):
        # no file
        assert sra_lineage.find_lineages(test_lin_dict, TestPath, "NotAnSraAcc") == 1

    def test_finished(self):
        # already done
        assert sra_lineage.find_lineages(test_lin_dict, TestPath, "FinishedLins") == 0

    def test_empty_tsv(self):
        # empty file
        assert sra_lineage.find_lineages(test_lin_dict, TestPath, "EmptyTSV") == 2

    def test_bad_tsv(self):
        # bad nt call format
        assert sra_lineage.find_lineages(test_lin_dict, TestPath, "BadFormat") == 2

    def test_good_tsv(self):
        # good lineages
        assert sra_lineage.find_lineages(test_lin_dict, TestPath, "GoodTSV") == 0

    def test_samp_output(self):
        # samp output check
        with open(f"{TestPath}/tsvs/CheckLin.lineages.tsv", "r") as checked:
            with open(f"{TestPath}/tsvs/GoodTSV.lineages.tsv", "r") as good:
                assert checked.read() ==  good.read()

    def test_agg_output(self):
        # agg output check
        with open(f"{TestPath}/CheckLins.tsv", "r") as checked:
            with open(f"{TestPath}/Lineages.tsv", "r") as good:
                assert checked.read() ==  good.read()
