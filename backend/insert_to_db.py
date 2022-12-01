import os
import re
import datetime
import itertools
from multiprocessing import Pool, cpu_count
import pandas as pd
import duckdb
from subprocess import check_output
from yaml import safe_load


def get_git_revision_hash() -> str:
    return check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()


def get_run_config_file() -> pd.DataFrame:

    with open("config.yaml", "r") as stream:

        d = safe_load(stream)

    df = pd.DataFrame(d, index=[0])

    return df


def get_pipeline_run_metadata(timestamp: str) -> pd.DataFrame:

    latest_git_hash = get_git_revision_hash()

    df = get_run_config_file()

    df["run_at"] = timestamp

    df["git_hash"] = latest_git_hash

    return df


def parse_full_lineages(SRA_ID: str, work_path: str) -> pd.DataFrame:

    df = pd.read_csv(
        f"{work_path}/endpoints/{SRA_ID}.lineages.tsv",
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


def load_full_df(SRA_ID: str, work_path: str) -> pd.DataFrame:

    try:
        df = parse_full_lineages(SRA_ID, work_path)

    except FileNotFoundError:
        df = pd.DataFrame(columns=["SRA_ID", "lineages", "abundances"])

    return df


def compile_regex() -> re.Pattern:
    return re.compile(r"[A-Za-z]+[A-Za-z0-9\.]*|0\.[0-9]+")


def parse_pattern(name: str, regex_pattern: re.Pattern) -> str:
    return re.findall(regex_pattern, name)[0]


def parse_summarized_lineages(SRA_ID: str, work_path: str) -> pd.DataFrame:

    regex = compile_regex()

    df = pd.read_table(
        f"{work_path}/endpoints/{SRA_ID}.lineages.tsv",
        skiprows=1,
        header=None,
        engine="python",
        sep="\t|, ",
        nrows=1,
    )

    # File is not column oriented. All data is on one row.
    # Elements are in order: string | lineage | % | lineage | % ....
    # Pull out the lineage names which should be elements 1, 3, ..., n-1
    # and lin % which should be 2, 4, ..., n
    summarized_lineages = [
        parse_pattern(df[i][0], regex) for i in range(1, len(df.columns) - 1, 2)
    ]
    lineage_percentages = [
        parse_pattern(df[i][0], regex) for i in range(2, len(df.columns), 2)
    ]

    return pd.DataFrame(
        {"SRA_ID": SRA_ID, "name": summarized_lineages, "p": lineage_percentages}
    )


def load_summarized_df(SRA_ID: str, work_path: str) -> pd.DataFrame:

    try:
        df = parse_summarized_lineages(SRA_ID, work_path)

    except FileNotFoundError:
        df = pd.DataFrame(columns=["SRA_ID", "name", "p"])

    return df


def get_sample_metadata(work_path: str) -> pd.DataFrame:
    con = duckdb.connect(":memory:")
    meta = con.execute(
        f"""
        SELECT DISTINCT * FROM read_csv_auto('{work_path}/sra_meta_collect_*.tsv',
        header=True)
        """
    ).df()
    con.close
    return meta


if __name__ == "__main__":
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d_%H.%M.%S"
    )
    with open("Pipeline.times", "r", encoding="utf-8") as times_fh:
        start_time = times_fh.readline().split(" ")[-1].strip()
        end_time = times_fh.readline().split(" ")[-1].strip()
    # Duckdb is automatically executed on all cores

    run_metadata = get_pipeline_run_metadata(timestamp)
    work_path = run_metadata["work_path"][0]
    if work_path:
        work_path = os.path.realpath(work_path)
    else:
        work_path = os.getcwd()

    sample_metadata = get_sample_metadata(work_path)
    sample_metadata["run_at"] = timestamp
    sample_metadata["start_at"] = start_time
    sample_metadata["end_at"] = end_time

    run_metadata.to_csv(f"{timestamp}_run_meta.csv", index=False)
    regex = compile_regex()
    SRA_IDs = sample_metadata["Accession"].tolist()

    sample_metadata.to_csv(f"{timestamp}_samp_meta.csv", index=False)
    with Pool(processes=cpu_count()) as pool:

        # Get the full lineage outputs
        res = pool.starmap(load_full_df, zip(SRA_IDs, itertools.repeat(work_path)))
        full_lineage_output = pd.concat(res, ignore_index=True)
        full_lineage_output["run_at"] = timestamp
        full_lineage_output["start_at"] = start_time
        full_lineage_output["end_at"] = end_time

        # Get the summarized lineage outputs
        res = pool.starmap(
            load_summarized_df, zip(SRA_IDs, itertools.repeat(work_path))
        )
        summarized_lineage_output = pd.concat(res, ignore_index=True)
        summarized_lineage_output["run_at"] = timestamp
        summarized_lineage_output["start_at"] = start_time
        summarized_lineage_output["end_at"] = end_time

    summarized_lineage_output.to_csv(
        f"{timestamp}_summarized_lineage_meta.csv", index=False
    )
    full_lineage_output.to_csv(f"{timestamp}_full_lineage_meta.csv", index=False)

    try:
        s3_access_key_id = os.environ["s3_access_key_id"]
        s3_secret_access_key = os.environ["s3_secret_access_key"]
    except KeyError:
        print("s3 keys not found, skipping upload")
    else:
        con = duckdb.connect(":memory:")  # in-memory db

        con.execute(
            f"""

        INSTALL httpfs;
        LOAD httpfs;
        SET s3_region='us-east-1';
        SET s3_access_key_id='{s3_access_key_id}';
        SET s3_secret_access_key='{s3_secret_access_key}';

                   """
        )

        for dataset in [
            "sample_metadata",
            "run_metadata",
            "full_lineage_output",
            "summarized_lineage_output",
        ]:

            con.execute(
                f"""

            COPY (

            SELECT *
            FROM {dataset}

                 )

            TO 's3://ppi-dev/shed/{dataset}/{timestamp}.parquet';

            """
            )
