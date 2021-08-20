import pandas as pd
import os

def year_to_path(year):
    data_path = os.path.join("..", "data", "raw", "crime")

    path = str(year)
    files = os.listdir(os.path.join(data_path, "bka", path))
    if len(files) > 0:
        return os.path.join(data_path, "bka", path, files[0])

def prep_data_2013():
    df_2013 = pd.read_excel(year_to_path(2013), skiprows=6)[["Unnamed: 1", "Unnamed: 2", "Fälle"]].dropna(subset = ["Unnamed: 2"])

    df_2013.rename(columns = {"Unnamed: 1" : "Art", "Unnamed: 2" : "kreis_key", "Fälle" : "crimes_2013"}, inplace = True)

    df_2013 = df_2013[df_2013.Art == "Straftaten insgesamt"][["kreis_key", "crimes_2013"]]

    df_2013.kreis_key = df_2013.kreis_key.astype(str).str.zfill(5)

    df_2013.crimes_2013 = df_2013.crimes_2013.astype(int)

    return df_2013

def prep_data_14_20(year):
    df = pd.read_csv(year_to_path(year), encoding = "ISO-8859-1", delimiter = ";", skiprows = 1, thousands = ",")

    df = df[df.Straftat == "Straftaten insgesamt"]

    crime_clm = f"crimes_{year}"

    df.rename(columns = {"Gemeindeschlüssel" : "kreis_key", "Anzahl erfasste Faelle" : crime_clm,  "erfasste Fälle" : crime_clm, "Gemeindeschluessel" : "kreis_key", "erfasste Faelle" :crime_clm}, inplace = True)

    df.kreis_key = df.kreis_key.astype(str).str.zfill(5)

    df = df[["kreis_key", crime_clm]]

    return df

def prep_data():
    df = prep_data_2013()

    for i in range(2014, 2021):
        df2 = prep_data_14_20(i)
        df = df.merge(df2, on = "kreis_key", how = "outer")

    return df