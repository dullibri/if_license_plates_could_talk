import pandas as pd
import os
from . import utils
from . import population
from datetime import datetime


def fraud_filter(df, column="Straftat"):
    """Construct filter for fraud crimes

    Args:
        df ([type]): [description]
        column (str, optional): [description]. Defaults to "Straftat".

    Returns:
        [type]: [description]
    """
    fraud_cats = [
        "Betrug §§ 263, 263a, 264, 264a, 265, 265a, 265b StGB davon:", "Betrug §§ 263, 263a, 264, 264a, 265, 265a, 265b StGB",
        "Urkundenfälschung §§ 267-271, 273-279, 281 StGB", "Betrug §§ 263, 263a, 264, 264a, 265, 265a-e StGB"]
    filt = df[column] == fraud_cats[0]
    for cat in fraud_cats:
        filt = filt | (df[column] == cat)
    return filt


def year_to_path(year):
    """Compute path of data on crimes for the given year

    Args:
        year (int): year

    Returns:
        str: path to data file
    """
    data_path = os.path.join(utils.path_to_data_dir(), "raw", "crime")
    path = str(year)
    files = os.listdir(os.path.join(data_path, "bka", path))
    if len(files) > 0:
        return os.path.join(data_path, "bka", path, files[0])


def prep_data_2013():
    """Preprocess data on crimes in 2013

    Returns:
        DataFrame: data on crimes in 2013
    """
    df = pd.read_excel(year_to_path(2013), skiprows=6)[
        ["Unnamed: 1", "Unnamed: 2", "Fälle"]].dropna(subset=["Unnamed: 2"])
    df.rename(columns={
        "Unnamed: 1": "Straftat", "Unnamed: 2": "kreis_key", "Fälle": "crimes_2013"}, inplace=True)
    cats = df.Straftat.unique()

    df.kreis_key = utils.fix_key(df.kreis_key)

    df_ges = df[df.Straftat ==
                "Straftaten insgesamt"][["kreis_key", "crimes_2013"]]

    df_ges.crimes_2013 = pd.to_numeric(df_ges.crimes_2013, errors="coerce")

    df_fraud = df[fraud_filter(df)]
    df_fraud = df_fraud.groupby("kreis_key").sum().reset_index()
    df_fraud = df_fraud.rename(columns={"crimes_2013": "fraud_2013"})

    df_ges = df_ges.merge(df_fraud, on="kreis_key")

    df_ges = utils.fix_goettingen(df_ges, "crimes_2013")
    df_ges = utils.fix_goettingen(df_ges, "fraud_2013")

    return df_ges, list(cats)


def prep_data_14_20(year):
    """Preprocess data on crimes in the specified year

    Args:
        year (int): year in the range 2014-2020

    Returns:
        DataFrame: data on crimes in the given year
    """
    crime_clm = f"crimes_{year}"
    fraud_clm = f"fraud_{year}"

    df = pd.read_csv(year_to_path(year), encoding="ISO-8859-1",
                     delimiter=";", skiprows=1, thousands=",")
    cats = df.Straftat.unique()
    df.rename(columns={"Gemeindeschlüssel": "kreis_key", "Anzahl erfasste Faelle": crime_clm,
              "erfasste Fälle": crime_clm, "Gemeindeschluessel": "kreis_key", "erfasste Faelle": crime_clm}, inplace=True)
    df.kreis_key = utils.fix_key(df.kreis_key)

    df_ges = df[df.Straftat == "Straftaten insgesamt"]
    df_ges = df_ges[["kreis_key", crime_clm]]

    df_fraud = df[["kreis_key", "Straftat", crime_clm]][fraud_filter(df)]
    df_fraud = df_fraud.groupby("kreis_key").sum().reset_index()
    df_fraud = df_fraud.rename(columns={crime_clm: fraud_clm})

    df_ges = df_ges.merge(df_fraud, on="kreis_key")

    if year <= 2016:
        df_ges = utils.fix_goettingen(df_ges, crime_clm)
        df_ges = utils.fix_goettingen(df_ges, fraud_clm)

    return df_ges, list(cats)


def prep_data():
    """Preprocess crime data

    Returns:
        DataFrame: crime data in the years 2013-2020
    """
    df, cats = prep_data_2013()

    for i in range(2014, 2021):
        df2, cats2 = prep_data_14_20(i)
        df = df.merge(df2, on="kreis_key", how="outer")
        cats = cats + cats2
    cats_df = pd.DataFrame(pd.Series(cats).unique())
    cats_df.to_csv(os.path.join(utils.path_to_data_dir(),
                   "processed", "crime", "categories.csv"))

    # calculate crime rates

    df_population = population.load_data()

    df_crime_rates = df.merge(df_population, on="kreis_key")
    years = list(filter(lambda y: f"population_{y}" in df_crime_rates.columns and f"crimes_{y}" in df_crime_rates.columns, range(2000, datetime.today(
    ).year+2)))

    for year in years:
        df_crime_rates[f"crimes_pp_{year}"] = df_crime_rates[f"crimes_{year}"] / \
            df_crime_rates[f"population_{year}"]
        df_crime_rates[f"fraud_pp_{year}"] = df_crime_rates[f"fraud_{year}"] / \
            df_crime_rates[f"population_{year}"]

    cols = ["kreis_key"]
    cols = cols + [f"crimes_{year}" for year in years]
    cols = cols + [f"crimes_pp_{year}" for year in years]
    cols = cols + [f"fraud_pp_{year}" for year in years]

    df_crime_rates = df_crime_rates[cols]

    return df_crime_rates


def load_data():
    """Load crime data from csv

    Returns:
       DataFrame : data on crimes
    """
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                                  "crime", "crime.csv"), index_col=0)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
