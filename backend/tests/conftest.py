"""
Fixture for decompressing testing support files
and removing them after the test
"""
import subprocess as sp
import pytest


@pytest.fixture(scope="session", autouse=True)
def necessary_files():
    """
    decompresses at start and yields so that the removal is
    done after the tests
    """
    # setup
    sp.run("tar xzf tests/testfiles.tar.gz -C tests", shell=True, check=True)

    yield
    # tear down
    sp.run("rm -rf tests/aggregate", shell=True, check=True)
    sp.run("rm -rf tests/consensus", shell=True, check=True)
    sp.run("rm -rf tests/download_sra", shell=True, check=True)
    sp.run("rm -rf tests/full", shell=True, check=True)
    sp.run("rm -rf tests/get_fastqs", shell=True, check=True)
    sp.run("rm -rf tests/lineages", shell=True, check=True)
    sp.run("rm -rf tests/mapping", shell=True, check=True)
    sp.run("rm -rf tests/primer_trim", shell=True, check=True)
    sp.run("rm -rf tests/quality_check", shell=True, check=True)
    sp.run("rm -rf tests/sam2bam", shell=True, check=True)
    sp.run("rm -rf tests/vc", shell=True, check=True)
