import pandas as pd
import os


def load_data():
    """loads data from /data/processed/ into a DataFrame"""
    return pd.read_csv(os.path.join("..", "data", "processed", "data.csv"), index_col=0)
