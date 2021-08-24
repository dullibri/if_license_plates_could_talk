import pandas as pd
import os
from . import utils


def load_data():
    """Load data on regions

    Returns:
        DataFrame: data on regions
    """
    df = pd.read_csv(os.path.join(utils.path_to_data_dir(), "processed",
                                  "regions", "regions.csv"), index_col=0)
    df.kreis_key = utils.fix_key(df.kreis_key)
    return df
