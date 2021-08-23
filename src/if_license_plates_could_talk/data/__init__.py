import pandas as pd
import os
from . import database


def load_data():
    """loads data from /data/processed/ into a DataFrame"""
    return pd.read_csv(os.path.join("..", "data", "processed", "data.csv"), index_col=0)


db = database.DataBase()
