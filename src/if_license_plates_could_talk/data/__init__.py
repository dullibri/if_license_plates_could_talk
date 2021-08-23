import pandas as pd
import os
from . import database
from . import utils


def load_data():
    """loads data from /data/processed/ into a DataFrame"""
    return pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed", "data.csv"), index_col=0)


db = database.DataBase()
