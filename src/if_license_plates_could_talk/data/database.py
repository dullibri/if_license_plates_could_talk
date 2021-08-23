import sqlite3
import os
import pandas as pd
import data.license_plate
import data.population
import data.income
import data.crime
from datetime import datetime
import sys


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

        df_plate = data.license_plate.load_data()
        df_plate.to_sql("license_plate", self.con, if_exists="replace")

        # Population

        df_population = data.population.load_data()
        df_population.to_sql("population", self.con, if_exists="replace")

        # Crime
        df_crime = data.crime.load_data()
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
        df_income = data.income.load_data()
        df_income.to_sql("income", self.con, if_exists="replace")

    def query(self, sql_query):
        """Execute a query. Returns result as pandas Dataframe"""
        df = pd.read_sql(sql_query, self.con, index_col="index")
        return df

    def get_data(self):
        df_plate = self.query("SELECT * FROM license_plate")
        df_income = self.query("SELECT * FROM income")
        df_crime = self.query("SELECT * FROM crime")
        df_population = self.query("SELECT * FROM population")

        df_merged = df_plate.merge(df_income, on="kreis_key", how="outer")
        df_merged = df_merged.merge(df_crime, on="kreis_key", how="outer")
        df_merged = df_merged.merge(df_population, on="kreis_key", how="outer")

        return df_merged
