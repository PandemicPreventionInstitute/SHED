"""
    module for testing quality_check rule
    generated by snakemake
    last edited 7-12-22
"""
import common


def test_quality_check():
    """
    function to test quality_check rule
    """

    additional_variable = [
        "--snakefile",
        "snakefile2",
    ]

    common.run_unit_test(
        "quality_check", "fastqs/ERR9813149.qc.done", additional_variable
    )
