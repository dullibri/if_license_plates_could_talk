import pandas as pd
import data.crime
import data.income
import data.population
import data.license_plate
import os

def prep_data():

    df_crime = data.crime.prep_data()
    df_crime.to_csv(os.path.join("..", "data", "processed", "crime", "crime.csv"))

    df_income = data.income.prep_data()
    df_income.to_csv(os.path.join("..", "data", "processed", "income", "income.csv"))

    
    df_population = data.population.prep_data()
    df_population.to_csv(os.path.join("..", "data", "processed", "population", "population.csv"))

    df_plate = data.license_plate.prep_data()
    df_plate.to_csv(os.path.join("..", "data", "processed", "license_plate", "license_plate.csv"))

    #merge
    
    df = df_plate.merge(df_income, on = "kreis_key", how = "outer")
    df = df.merge(df_crime, on = "kreis_key", how = "outer")
    df = df.merge(df_population, on = "kreis_key", how = "outer")

    
    # Calculate Crime Rates

    crime_years = range(2013, 2020)

    for year in crime_years:
        df[f"crimes_pp_{year}"] = pd.to_numeric(df[f"crimes_{year}"], errors = "coerce") / pd.to_numeric(df[f"population_{year}"], errors = "coerce")

    df.to_csv(os.path.join("..", "data", "processed", "data.csv"))

    return df

if __name__ == "__main__":
    df = prep_data()
    print(df.info())
    print(df.head())