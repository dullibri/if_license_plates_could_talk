import sqlite3
import os
import pandas as pd
import data.license_plate
import data.population
import data.income
import data.crime


class DataBase:
    """Interface to sqlite database stored in data/sqlite"""

    def __init__(self):
        """Initializing database, connecting to db, ..."""
        self.con = sqlite3.connect(os.path.join(
            "..", "data", "sqlite", "database.db"))

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
        df_crime.to_sql("crime", self.con, if_exists="replace")

        # Income

        df_income = data.income.load_data()
        df_income.to_sql("income", self.con, if_exists="replace")

    def query(self, sql_query):
        """Execute a query. Returns result as pandas Dataframe"""
        df = pd.read_sql_query(sql_query)
        return df


db = DataBase()
