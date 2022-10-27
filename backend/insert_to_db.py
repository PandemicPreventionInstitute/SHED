import re
import datetime
from multiprocessing import Pool, cpu_count
import pandas as pd
import duckdb


def parse_full_lineages(SRA_ID: str) -> pd.DataFrame:

    df = pd.read_csv(
        f"endpoints/{SRA_ID}.lineages.tsv",
        sep="\t| ",
        header=None,
        engine="python",  # regex parsing requires python engine
        skiprows=2,
        nrows=2,
    )

    df = pd.DataFrame(df.transpose())

    # Use the first row as the header
    df.columns = df.iloc[0]
    df = df[1:]

    df.insert(0, "SRA_ID", SRA_ID)

    return df


def compile_regex() -> re.Pattern:
    return re.compile(r"[A-Za-z]+|\.[0-9]+")


def parse_pattern(name: str, regex_pattern: re.Pattern) -> str:
    return re.findall(regex_pattern, name)[0]


def parse_summarized_lineages(SRA_ID: str, regex: re.Pattern) -> pd.DataFrame:

    df = pd.read_table(
        f"endpoints/{SRA_ID}.lineages.tsv",
        skiprows=1,
        header=None,
        engine="python",
        sep="\t| ",
        nrows=1,
    )

    # File is not column oriented. All data is on one row.
    # Elements are in order: string | lineage | % | lineage | % ....
    # Pull out the lineage names which should be elements 1, 3, ..., n-1
    # and lin % which should be 2, 4, ..., n
    summarized_lineages = [
        parse_pattern(df[i][0], regex)
        for i in range(1, len(df.columns) - 1, 2)
    ]
    lineage_percentages = [
        parse_pattern(df[i][0], regex) for i in range(2, len(df.columns), 2)
    ]

    return pd.DataFrame(
        {"name": summarized_lineages, "p": lineage_percentages}
    )


def get_metadata() -> pd.DataFrame:
    con = duckdb.connect(":memory:")
    meta = con.execute(
        """
        SELECT DISTINCT * FROM read_csv_auto('sra_meta_collect_*.tsv',
        header=True)
        """
    ).df()
    con.close
    return meta


if __name__ == "__main__":
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    # Duckdb is automatically executed on all cores
    metadata = get_metadata()
    metadata["run_at"] = timestamp

    regex = compile_regex()
    SRA_IDs = metadata["Accession"].tolist()

    with Pool(processes=cpu_count()) as pool:

        # Get the full lineage outputs
        res = pool.map(parse_full_lineages, SRA_IDs)
        full_lineage_outputs = pd.concat(res, ignore_index=True)
        full_lineage_outputs["run_at"] = timestamp

        # Get the summarized lineage outputs
        res = pool.map(parse_summarized_lineages, SRA_IDs)
        summarized_lineage_outputs = pd.concat(res, ignore_index=True)
        summarized_lineage_outputs["run_at"] = timestamp
