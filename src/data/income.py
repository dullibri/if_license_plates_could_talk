import pandas as pd
import os 

def prep_data():
    path = os.path.join("..", "data", "raw", "income", "82411-01-03-4.csv")
    df_raw = pd.read_csv(path, encoding="ISO-8859-1", skiprows = 6, delimiter = ";")

    df_raw = df_raw.rename(columns = {"Unnamed: 0" : "year", "Unnamed: 1" : "kreis_key", "Unnamed: 2" : "kreis_name", "Tsd. EUR" : "income", "EUR" : "income_pp"})
    df_raw = df_raw.dropna(subset = ["kreis_key"])
    df_raw = df_raw[df_raw.kreis_key != "DG"]
    df_raw.kreis_key.replace({"02": "02000", "11" : "11000"}, inplace=True) # Berlin, Hamburg

    df_piv = df_raw.pivot(index = "kreis_key", columns = "year", values = ["income_pp", "income"])

    df_piv.columns  =[f"{s1}_{s2}" for (s1,s2) in df_piv.columns.tolist()]

    df_piv.reset_index(inplace= True)

    df = df_piv[[len(i) == 5 for i in df_piv.kreis_key]] # drop rows that are not on "Kreis"-level

    return df

def load_data():
    return pd.read_csv(os.path.join("..", "data", "processed", "income", "income.csv"))
