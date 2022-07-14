"""
    module for testing primer_trim rule
    generated by snakemake
    last edited 7-12-22
"""
import common


def test_primer_trim():
    """
    function to test primer_trim rule
    """

    additional_variable = [
        "--snakefile",
        "snakefile3",
    ]

    common.run_unit_test(
        "primer_trim", "sams/SRR17866146.trim.done", additional_variable
    )