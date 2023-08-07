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



def get_pipeline_run_metadata(timestamp: str) -> pd.DataFrame:

    df = pd.DataFrame()

    df["db_collection_time"] = [timestamp]
    df["git_hash"] = get_git_revision_hash()

    return df


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


def load_full_df(SRA_ID: str) -> pd.DataFrame:

    try:
        df = parse_full_lineages(SRA_ID)

    except FileNotFoundError:
        df = pd.DataFrame(columns=["SRA_ID", "lineages", "abundances"])

    return df


def compile_regex() -> re.Pattern:
    return re.compile(r"[A-Za-z]+[A-Za-z0-9\.]*|0\.[0-9]+")


def parse_pattern(name: str, regex_pattern: re.Pattern) -> str:
    return re.findall(regex_pattern, name)[0]


def parse_summarized_lineages(SRA_ID: str) -> pd.DataFrame:

    regex = compile_regex()

    df = pd.read_table(
        f"endpoints/{SRA_ID}.lineages.tsv",
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


def load_summarized_df(SRA_ID: str) -> pd.DataFrame:

    try:
        df = parse_summarized_lineages(SRA_ID)

    except FileNotFoundError:
        print(f"parse sum lin: no file for {SRA_ID}")
        df = pd.DataFrame(columns=["SRA_ID", "name", "p"])
    except Exception as Err:
        print(f"parse sum lin err: {Err} for {SRA_ID}")
        df = pd.DataFrame(columns=["SRA_ID", "name", "p"])

    return df


def get_sample_metadata() -> pd.DataFrame:
    con = duckdb.connect(":memory:")
    meta = con.execute(
        f"""
        SELECT DISTINCT * FROM read_csv_auto('sra_meta_collect_*.tsv',
        header=True)
        """
    ).df()
    con.close
    return meta


if __name__ == "__main__":
    try:
        timestamp = os.environ["timestamp"]
    except:
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d_%H.%M.%S"
        )
    try:
        timestamp += "_" + os.environ["count"]
    except:
        pass

    with open("Pipeline.times", "r", encoding="utf-8") as times_fh:
        start_time = times_fh.readline().split(" ")[-1].strip()
        end_time = times_fh.readline().split(" ")[-1].strip()
    # Duckdb is automatically executed on all cores

    run_metadata = get_pipeline_run_metadata(timestamp)

    run_metadata["db_collection_time"] = timestamp
    run_metadata["run_start_time"] = start_time
    run_metadata["run_end_time"] = end_time
    if os.path.isfile("freyja.update.times"):
        with open(
            "freyja.update.times", "r", encoding="utf-8"
        ) as freyja_fh:
            if freyja_fh.read():
                freyja_fh.seek(0)
                run_metadata["Freyja updated"] = freyja_fh.readlines()[-1].strip()

    run_metadata["snakemake"] = check_output(["snakemake", "-v"]).decode().strip()


    for file in os.listdir("envs/"):
        if file.endswith(".yaml"):
            with open(os.path.join("envs/", file), "r", encoding="utf-8") as yaml_fh:
                depend_vers = yaml_fh.read().split("dependencies:\n")[-1]
                for line in depend_vers.split("\n"):
                    if line:
                        line_split = line.split("=")
                        run_metadata[line_split[0].split(" ")[-1]] = line_split[-1]

    print(run_metadata)
    run_metadata.to_csv(f"{timestamp}_run_meta.csv", index=False)

    sample_metadata = get_sample_metadata()
    regex = compile_regex()
    SRA_IDs = sample_metadata["Accession"].tolist()

    sample_metadata.to_csv(f"{timestamp}_samp_meta.csv", index=False)
    with Pool(processes=cpu_count()) as pool:

        # Get the full lineage outputs
        res = pool.starmap(load_full_df, zip(SRA_IDs))
        full_lineage_output = pd.concat(res, ignore_index=True)
        full_lineage_output["db_collection_time"] = timestamp
        full_lineage_output["run_start_time"] = start_time
        full_lineage_output["run_end_time"] = end_time

        # Get the summarized lineage outputs
        res = pool.starmap(
            load_summarized_df, zip(SRA_IDs)
        )
        summarized_lineage_output = pd.concat(res, ignore_index=True)
        summarized_lineage_output["db_collection_time"] = timestamp
        summarized_lineage_output["run_start_time"] = start_time
        summarized_lineage_output["run_end_time"] = end_time

        summarized_lineage_output.to_csv(
            f"{timestamp}_summarized_lineage_meta.csv", index=False
        )
        full_lineage_output.to_csv(f"{timestamp}_full_lineage_meta.csv", index=False)

    try:
        s3_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        s3_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    except KeyError:
        print("s3 keys not found, skipping write")
    else:
        print("writing to s3")
        print(f"timestamp {timestamp}")
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
