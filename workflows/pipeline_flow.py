import os
import duckdb
import pandas as pd
from prefect import flow, task


DATA_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
TABLE_NAME = "tips"


@task
def fetch_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    print(f"Fetched {len(df)} rows from {url}")
    return df


@task
def load_to_motherduck(df: pd.DataFrame, table: str) -> int:
    token = os.environ["MOTHERDUCK_TOKEN"]
    con = duckdb.connect(f"md:?motherduck_token={token}")
    con.execute("CREATE DATABASE IF NOT EXISTS hackathon")
    con.execute("USE hackathon")
    con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM df")
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    con.close()
    print(f"Loaded {count} rows into MotherDuck table '{table}'")
    return count


@flow(name="pipeline-flow")
def pipeline_flow():
    df = fetch_data(DATA_URL)
    load_to_motherduck(df, TABLE_NAME)


if __name__ == "__main__":
    pipeline_flow()
