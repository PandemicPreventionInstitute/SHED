"""
Common code for unit testing of rules generated with Snakemake 7.8.0.
Last edited on 11-21-22
"""

import os
import sys
from tempfile import TemporaryDirectory
import shutil
from pathlib import Path, PurePosixPath
import subprocess as sp


def run_snakemake(workdir, target, add_args):
    """
    run the snakemake command with provided target and additional variables
    """

    command_list = []
    if target:
        command_list = [
            "python",
            "-m",
            "snakemake",
            target,
            "-j1",
            "--directory",
            workdir,
            "--use-conda",
        ]
    else:
        command_list = [
            "python",
            "-m",
            "snakemake",
            "-j1",
            "--directory",
            workdir,
            "--use-conda",
        ]

    # Run the test job.
    sp.check_output(command_list + add_args)


def run_unit_test(name, target, additional_variable):
    """
    Runs the tests used by pytest
    """
    with TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir) / "workdir"
        data_path = PurePosixPath(f"tests/{name}/data")
        expected_path = PurePosixPath(f"tests/{name}/expected")

        # Copy data to the temporary workdir.
        shutil.copytree(data_path, workdir)

        # dbg
        print(name, file=sys.stderr)

        run_snakemake(workdir, target, additional_variable)

        # Check the output byte by byte using cmp.
        # To modify this behavior, you can inherit from common.OutputChecker in here
        # and overwrite the method `compare_files(generated_file, expected_file),
        # also see common.py.
        OutputChecker(data_path, expected_path, workdir).check()


class OutputChecker:
    """
    Snakemake's auto generated class for comparing expected and generated outputs.
    The check function was altered so that files that are expected or may be different
    from run to run are passed on the cmp run.
    """

    def __init__(self, data_path, expected_path, workdir):
        """
        Class self definition
        """
        self.data_path = data_path
        self.expected_path = expected_path
        self.workdir = workdir

    def check(self):
        """
        Checks to see if the generated files are the same as the expected.
        Skips binary comparision for files that may be different run to run.
        """
        input_files = set(
            (Path(path) / file).relative_to(self.data_path)
            for path, subdirs, files in os.walk(self.data_path)
            for file in files
        )
        expected_files = set(
            (Path(path) / file).relative_to(self.expected_path)
            for path, subdirs, files in os.walk(self.expected_path)
            for file in files
        )
        unexpected_files = set()
        for path, subdirs, files in os.walk(self.workdir):
            for file in files:
                file = (Path(path) / file).relative_to(self.workdir)
                if str(file).startswith(".snakemake"):
                    continue
                if file in expected_files:
                    if not (
                        str(file).endswith(".html")
                        or str(file).endswith(".sam")
                        or str(file).endswith(".bam")
                        or str(file).endswith(".bai")
                        or str(file).endswith(".done")
                        or str(file).endswith(".log")
                        or str(file).startswith("sra_")
                        or "lineage" in str(file).lower()
                        or str(file).endswith(".json")
                    ):
                        self.compare_files(
                            self.workdir / file, self.expected_path / file
                        )
                elif file in input_files:
                    # ignore input files
                    pass
                else:
                    unexpected_files.add(file)
        if unexpected_files:
            raise ValueError(
                "Unexpected files:\n{}".format(
                    "\n".join(sorted(map(str, unexpected_files)))
                )
            )

    def compare_files(self, generated_file, expected_file):
        """
        binary file comparision
        """
        sp.check_output(["cmp", generated_file, expected_file])
