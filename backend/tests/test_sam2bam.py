"""
    module for testing sam2bam rule
    generated by snakemake
    last edited 11-21-22
"""
import common


def test_sam2bam():
    """
    function to test sam2bam rule
    """

    additional_variable = [
        "--snakefile",
        "snakefile2",
    ]

    common.run_unit_test("sam2bam", "sams/SRR17866146.bam", additional_variable)
