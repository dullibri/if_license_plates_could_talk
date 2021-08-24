import geo.border_vicinity
from . import regions
from . import utils
import os
import pandas as pd


def prep_data():
    """[summary]
    """
    df = regions.load_data()
    df = df[["kreis_key"]]
    df.drop_duplicates()
    distance_calculator = geo.border_vicinity.DistanceCalculator()
    df["border_vic"] = df.kreis_key.apply(distance_calculator.distance)
    return df[["kreis_key", "border_vic"]]


def load_data():
    """[summary]
    """
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                     "border", "border.csv"), index_col=0)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
