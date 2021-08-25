import sqlite3
import os
import pandas as pd

from . import household
from . import border_vicinity
from . import license_plate
from . import population
from . import income
from . import crime
from . import regions
from . import utils
from . import education

from datetime import datetime


class DataBase:
    """Interface to sqlite database stored in data/sqlite"""

    def __init__(self):
        """Initializing database, connecting to db, ..."""
        path = os.path.join(os.path.dirname(__file__),
                            "..", "..", "..",  "data", "sqlite", "database.db")
        self.con = sqlite3.connect(path)

    def populate_db(self):
        """Populate database with processed data"""
        # License Plates / Regions

        def load_data(feature):
            df = globals()[feature].load_data()
            df.to_sql(feature, self.con, if_exists="replace")
            return df

        features_without_crime_pop = [
            "license_plate", "income", "regions", "border_vicinity", "education", "household"]

        for feature in features_without_crime_pop:
            load_data(feature)

        # Population

        df_population = load_data("population")
        # Crime

        df_crime = crime.load_data()
        # calculate crime rates

        df_crime_rates = df_crime.merge(df_population, on="kreis_key")
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
        df_crime_rates.to_sql("crime", self.con, if_exists="replace")

    def query(self, sql_query):
        """Execute a query.

        Args:
            sql_query (str): sql  query

        Returns:
            DataFrame: Result of query
        """
        df = pd.read_sql(sql_query, self.con, index_col="index")
        return df

    def get_data(self):
        """Load data from db. For details on columns, see data/processed/data_desc.csv

        Returns:
            DataFrame: Data on regions, income, crime and population
        """
        features = ["income", "crime", "population",
                    "border_vicinity", "education",  "household"]

        df_merged = self.query(f"SELECT * FROM regions")

        for feature in features:
            df_feat = self.query(f"SELECT * FROM {feature}")
            df_merged = df_merged.merge(df_feat, on="kreis_key", how="outer")

        df_merged.to_csv(os.path.join(
            utils.path_to_data_dir(), "processed", "merged.csv"))

        return df_merged
