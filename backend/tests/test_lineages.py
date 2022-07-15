"""
    module for testing lineages rule
    generated by snakemake
    last edited 7-12-22
"""
import common


def test_lineages():
    """
    function to test lineages rule
    """

    additional_variable = [
        "--snakefile",
        "snakefile3",
    ]

    common.run_unit_test(
        "lineages", "endpoints/SRR17866146.lineages.tsv", additional_variable
    )
