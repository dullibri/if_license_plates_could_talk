import pandas as pd
import os


class PreprocessorCrime:
    def __init__(self):
        self.years = set()
        self.df = pandas.DataFrame()

    def year_to_path(self, year):
        """Convert year to relative path in filesystem"""
        path = str(year)
        files = os.listdir(os.path.join("bka", path))
        if len(files) > 0:
            return os.path.join("bka", path, files[0])

    def prep_crime_data_2013(self):
        """returns data on crimes in 2013"""
        df_2013 = pd.read_excel(year_to_path(2013), skiprows=6)[["Unnamed: 1", "Unnamed: 2", "Fälle"]].dropna(subset = ["Unnamed: 2"])

        df_2013.rename(columns = {"Unnamed: 1" : "Art", "Unnamed: 2" : "kreis_key", "Fälle" : "crimes_2013"}, inplace = True)

        df_2013 = df_2013[df_2013.Art == "Straftaten insgesamt"][["kreis_key", "crimes_2013"]]

        df_2013.kreis_key = df_2013.kreis_key.astype(int)
        df_2013.crimes_2013 = df_2013.crimes_2013.astype(int)

        return df_2013

    def prep_crime_data_14_20(self, year):
        """return data on crimes in given year (2014-2020)"""
        df = pd.read_csv(self.year_to_path(year), encoding = "ISO-8859-1", delimiter = ";", skiprows = 1, thousands = ",")

        df = df[df.Straftat == "Straftaten insgesamt"]

        crime_clm = f"crimes_{year}"

        df.rename(columns = {"Gemeindeschlüssel" : "kreis_key", "Anzahl erfasste Faelle" : crime_clm,  "erfasste Fälle" : crime_clm, "Gemeindeschluessel" : "kreis_key", "erfasste Faelle" :crime_clm}, inplace = True)

        df.kreis_key = df.kreis_key.astype(int)

        df = df[["kreis_key", crime_clm]]

        return df

    def prep_crime_data(self):
        """returns data"""
        df = self.prep_crime_data_2013()
        for i in range(2014, 2021):
            df2 = self.read_crime_data_14_20(i)
            df = df.merge(df2, on = "kreis_key", how = "outer")
        return df