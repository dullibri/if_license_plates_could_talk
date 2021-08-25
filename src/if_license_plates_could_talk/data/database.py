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

        def load_data(feature):
            df = globals()[feature].load_data()
            df.to_sql(feature, self.con, if_exists="replace")
            return df

        features = [
            "license_plate", "income", "regions", "border_vicinity", "education", "household", "population", "crime"]

        for feature in features:
            load_data(feature)

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
