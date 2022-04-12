#!/bin/env python3

'''
Writen by Devon Gregory
This script tests the workings of the sra_fetch module using pytest
Last edited on 4-11-22
'''

import os
import sys
import pytest
sys.path.insert(0, os.getcwd().split('SHED')[0]+'SHED/backend' )
import modules.sra_file_parse as file_parse

base_path = os.getcwd().split('SHED')[0]+'SHED/backend/tests/'

class TestGetAccessions:
    '''Tests of get_accessions function in sra_file_parse'''

    def test_non_existing_file_get(self):
    # bad filename
        assert file_parse.get_accessions('probably.a.non-existing.file') == 1

    def test_empty_file_get(self):
    # empty file
        assert file_parse.get_accessions('./tests/TestEmptySraList.txt') == 2

    def test_bad_sra_acc_get(self):
    # no valid accessions
        assert file_parse.get_accessions('./tests/TestBadSraList.txt') == 2

    def test_fake_sra_acc_get(self):
    # no real accessions
        assert file_parse.get_accessions('./tests/TestBadSraList2.txt') == ['SRR00000001']

    def test_good_sra_acc_get(self):
    # good file, mix of good and bad SRAs
        assert file_parse.get_accessions('./tests/TestMixedSraList.txt') == ['ERR5019844', 'SRR15294802', 'SRR17888010', 'SRR15240439', 'SRR17887900']


class TestFindFastqs:
    ''' testing find_fastqs function in sra_file_parse'''


    def test_no_fastqs(self):
    # no fastqs
        assert file_parse.find_fastqs(base_path, 'not.an.sra') == []

    def test_single_fastqs(self):
    # single fastqs
        assert file_parse.find_fastqs(base_path, 'single.test') == ['/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/single.test_1.fastq']

    def test_paired_fastqs(self):
    # paired fastqs
        assert file_parse.find_fastqs(base_path, 'paired.test') \
            == ['/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/paired.test_1.fastq', '/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/paired.test_2.fastq']

    def test_mismatched_fastqs(self):
    # single and paired
        assert file_parse.find_fastqs(base_path, '3fastqtest') == 1


class TestFindProgress:
    ''' testing find_progress function in sra_file_parse'''

    def test_no_prog(self):
        # no progress
        assert file_parse.find_progess(base_path, 'not.an.sra') == ('fetch', [])

    def test_fetch_started(self):
        # fetch started, not finished
        assert file_parse.find_progess(base_path, 'SRR00000001') == ('fetch', [])

    def test_fetch_finished(self):
        # fetch finished, no further progress
        assert file_parse.find_progess(base_path, 'fetch.finished') == ('preproc', ['/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/fetch.finished_1.fastq', \
        '/mnt/e/Rockefeller/Git/SHED/backend/tests/fastqs/fetch.finished_2.fastq'])

    def test_rep_started(self):
        # repair started, not finished
        assert file_parse.find_progess(base_path, 'rep.not.finished') == ('repair', [])

    def test_ref_finished(self):
        # repair finished, no further progress
        assert file_parse.find_progess(base_path, 'rep.finished') == ('merge', ['/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/rep.finished_1.rep.fq', \
            '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/rep.finished_2.rep.fq', '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/rep.finished_sing.rep.fq'])

    def test_merge_started(self):
        # merge started, not finished
        assert file_parse.find_progess(base_path, 'merge.not.finished') == ('merge', [])

    def test_merge_finished(self):
        # merge finished, no further progress
        assert file_parse.find_progess(base_path, 'merge.finished') == ('cat', ['/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/merge.finished.merged.fq', \
            '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/merge.finished.un1.fq', '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/merge.finished.un2.fq'])

    def test_merge_rep_finished(self):
        # merge finished from repaired, no further progress
        assert file_parse.find_progess(base_path, 'mergerep.finished') == ('cat', ['/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/mergerep.finished.merged.fq', \
            '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/mergerep.finished.un1.fq', '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/mergerep.finished.un2.fq', \
                '/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/mergerep.finished_sing.rep.fq'])

    def test_cat_finsihed(self):
        # cat finished, no further progress
        assert file_parse.find_progess(base_path, 'cat.finished') == ('derep', ['/mnt/e/Rockefeller/Git/SHED/backend/tests/processing/cat.finished.all.fq'])

    def test_derep_finished(self):
        # derep finished, no further progress
        assert file_parse.find_progess(base_path, 'derep.finished') == ('map', ['/mnt/e/Rockefeller/Git/SHED/backend/tests/fastas/derep.finished.collapsed.fa'])


# # map finished, no further progress
# print(file_parse.find_progess(base_path, 'map.finished'))


# # vc started, not finished
# print(file_parse.find_progess(base_path, 'vc.not.finished'))


# # vc finished, no further progress
# print(file_parse.find_progess(base_path, 'vc.finished'))


