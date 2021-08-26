import os
import pandas as pd
from . import regions
from . import population
from . import license_plate
from . import income
from . import household
from . import database
from . import utils
from . import border_vicinity
from . import crime
from . import education


def load_data():
    """loads data from /data/processed/ into a DataFrame"""
    return pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed", "data.csv"), index_col=0)


db = database.DataBase()
