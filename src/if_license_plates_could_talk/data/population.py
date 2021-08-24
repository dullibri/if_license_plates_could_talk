import pandas as pd
import os

from . import utils


def prep_data():
    """Preprocess population data. Reads data in data/raw/population, outputs processed data in data/processed/population"""
    path = os.path.join(utils.path_to_data_dir(),
                        "raw", "population", "12411-05-01-4.csv")
    df_raw = pd.read_csv(path, encoding="ISO-8859-1",
                         skiprows=6, delimiter=";")

    # clean data

    df_raw.rename(columns={"Unnamed: 0": "year", "Unnamed: 1": "kreis_key",
                  "Unnamed: 2": "kreis_name", "Insgesamt": "population"}, inplace=True)
    df_raw = df_raw.dropna(subset=["kreis_key"])
    df_raw = df_raw[df_raw.kreis_key != "DG"]
    df_raw.kreis_key.replace(
        {"02": "02000", "11": "11000"}, inplace=True)  # Berlin, Hamburg

    df_raw.head()

    # Pivot Data
    df_piv = df_raw.pivot(
        index="kreis_key", columns="year", values=["population"])

    df_piv.columns = df_piv.columns.droplevel(0)
    df_piv = df_piv.reset_index()
    df_piv = df_piv.rename(
        columns={str(i): f"population_{i}" for i in df_raw.year.unique()})

    df = df_piv[[len(i) == 5 for i in df_piv.kreis_key]].copy()

    for year in range(2013, 2016):
        df = utils.fix_goettingen(df, f"population_{year}")

    return df


def load_data():
    """Load data from csv stored in data/processed"""
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                     "population", "population.csv"), index_col=0)
    for col in df.columns:
        if col != "kreis_key":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
