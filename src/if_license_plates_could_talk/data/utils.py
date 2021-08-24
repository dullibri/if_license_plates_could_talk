import os
import pandas as pd


def fix_key(ser):
    """Transform int to 5-digit str, padded with zeros. Ex: 101 -> 00101"""
    return ser.astype(int).astype(str).str.zfill(5)


def path_to_data_dir():
    """Returns absolute path to data directory"""
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")


def fix_goettingen(df, col):
    df.kreis_key = pd.to_numeric(df.kreis_key)
    df = df.set_index("kreis_key")
    df.loc[3159, col] = pd.to_numeric(
        df.loc[3152, col], errors="coerce") + pd.to_numeric(df.loc[3156, col], errors="coerce")
    df = df.reset_index()
    df.kreis_key = fix_key(df.kreis_key)
    return df
