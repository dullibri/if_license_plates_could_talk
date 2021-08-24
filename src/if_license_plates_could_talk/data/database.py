import sqlite3
import os
import pandas as pd

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

        df_plate = license_plate.load_data()
        df_plate.to_sql("license_plate", self.con, if_exists="replace")

        # Population

        df_population = population.load_data()
        df_population.to_sql("population", self.con, if_exists="replace")

        # Crime
        df_crime = crime.load_data()
        # calculate crime rates

        df_crime_rates = df_crime.merge(df_population, on="kreis_key")
        years = list(filter(lambda y: f"population_{y}" in df_crime_rates.columns and f"crimes_{y}" in df_crime_rates.columns, range(2000, datetime.today(
        ).year+2)))

        for year in years:
            df_crime_rates[f"crimes_pp_{year}"] = df_crime_rates[f"crimes_{year}"] / \
                df_crime_rates[f"population_{year}"]

        cols = ["kreis_key"]
        cols = cols + [f"crimes_{year}" for year in years]
        cols = cols + [f"crimes_pp_{year}" for year in years]

        df_crime_rates = df_crime_rates[cols]
        df_crime_rates.to_sql("crime", self.con, if_exists="replace")

        # Income
        df_income = income.load_data()
        df_income.to_sql("income", self.con, if_exists="replace")

        # regions

        df_regions = regions.load_data()
        df_regions.to_sql("regions", self.con, if_exists="replace")

        # border vic

        df_border = border_vicinity.load_data()
        df_border.to_sql("border", self.con, if_exists="replace")

        # education

        df_education = education.load_data()
        df_education.to_sql("education", self.con, if_exists="replace")

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
        df_regions = self.query("SELECT * FROM regions")
        df_income = self.query("SELECT * FROM income")
        df_crime = self.query("SELECT * FROM crime")
        df_population = self.query("SELECT * FROM population")
        df_border = self.query("SELECT * FROM border")
        df_education = self.query("SELECT * FROM education")

        df_merged = df_regions.merge(df_income, on="kreis_key", how="outer")
        df_merged = df_merged.merge(df_crime, on="kreis_key", how="outer")
        df_merged = df_merged.merge(df_population, on="kreis_key", how="outer")
        df_merged = df_merged.merge(df_border, on="kreis_key", how="outer")
        df_merged = df_merged.merge(df_education, on="kreis_key", how="outer")

        df_merged.to_csv(os.path.join(
            utils.path_to_data_dir(), "processed", "merged.csv"))

        return df_merged
