import pandas as pd
import os
from . import utils


def prep_data():
    """Preprocess data on the Europawahl 2019 / 2014
    """
    election_path = os.path.join(
        utils.path_to_data_dir(), "raw", "election", "ew19_kerg.csv")
    election = pd.read_csv(election_path, skiprows=[0, 1, 3, 4], delimiter=";")
    election.dropna(axis=1, inplace=True, how="all")
    election.columns = ["kreis_key",  "kreis_name", "bl_key", "ew_eli_2019", "ew_eli_2014", "ew_vot_2019", "ew_vot_2014",
                        "ew_invalid_2019", "ew_invalid_2014", "ew_valid_2019", "ew_valid_2014"] + list(election.columns[11:])
    election.drop("kreis_name", axis=1, inplace=True)
    election.dropna(subset=["kreis_key"], inplace=True)

    df_partei = pd.DataFrame()

    new_columns = list(election.columns[:10])
    partei_key = ""
    for i in range(10, len(election.columns)):
        clm = election.columns[i]
        if "Unnamed: " not in clm:
            partei_key = clm.lower()
            replacements = {
                " ": "_",
                "/": "_",
                ".": "_",
                "-": "_",
                "ä": "ae",
                "ö": "oe",
                "ü": "ue",
                "ß": "ss"
            }
            for rep in replacements:
                partei_key = partei_key.replace(rep, replacements[rep])

            df_partei = df_partei.append(
                {"partei_key": partei_key, "partei_name": clm}, ignore_index=True)

            new_columns.append(f"ew_vot_abs_{partei_key}_2019")
        else:
            new_columns.append(f"ew_vot_abs_{partei_key}_2014")

    df_partei.to_csv(os.path.join(utils.path_to_data_dir(),
                     "processed", "election", "parties.csv"))

    election.columns = new_columns

    election = election[election.kreis_key > 99]

    election.kreis_key = utils.fix_key(election.kreis_key)

    election = election.fillna(0)

    return election
