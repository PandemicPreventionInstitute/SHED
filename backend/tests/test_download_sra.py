import os
import sys

import subprocess as sp
from tempfile import TemporaryDirectory
import shutil
from pathlib import Path, PurePosixPath

sys.path.insert(0, os.path.dirname(__file__))

import common


def test_download_sra():

    with TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir) / "workdir"
        data_path = PurePosixPath("tests/download_sra/data")
        expected_path = PurePosixPath("tests/download_sra/expected")

        # Copy data to the temporary workdir.
        shutil.copytree(data_path, workdir)

        # dbg
        print("download_sra", file=sys.stderr)

        # Run the test job.
        sp.check_output(
            [
                "python",
                "-m",
                "snakemake",
                "download_sra",
                "-j1",
                "--directory",
                workdir,
                "--config",
                "query=ERR9812480+or+SRR14010117",
                "run_ID=test",
                "--snakefile",
                "snakefile1",
                "--use-conda",
            ]
        )

        # Check the output byte by byte using cmp.
        # To modify this behavior, you can inherit from common.OutputChecker in here
        # and overwrite the method `compare_files(generated_file, expected_file),
        # also see common.py.
        common.OutputChecker(data_path, expected_path, workdir).check()
