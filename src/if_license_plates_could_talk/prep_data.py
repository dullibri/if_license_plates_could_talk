import pandas as pd
import data.crime
import data.income
import data.population
import data.license_plate
import data.utils
import data.border_vicinity
import data.education
import data.household
import os


def prep_data():
    """Preprocess the raw data in data/raw.

    Returns:
        DataFrame: data indexed by license plate codes
    """

    df_crime = data.crime.prep_data()
    df_crime.to_csv(os.path.join(data.utils.path_to_data_dir(),
                    "processed", "crime", "crime.csv"))

    df_income = data.income.prep_data()
    df_income.to_csv(os.path.join(
        data.utils.path_to_data_dir(),  "processed", "income", "income.csv"))

    df_population = data.population.prep_data()
    df_population.to_csv(os.path.join(
        data.utils.path_to_data_dir(), "processed", "population", "population.csv"))

    df_plate = data.license_plate.prep_data()

    # regions

    df_regions = df_plate.drop(columns=["license_plate"])
    df_regions = df_regions[["kreis_key", "kreis_name"]].drop_duplicates()
    df_regions.to_csv(os.path.join(
        data.utils.path_to_data_dir(), "processed", "regions", "regions.csv"))

    df_plate = df_plate[["kreis_key", "license_plate"]].drop_duplicates()
    df_plate.to_csv(os.path.join(data.utils.path_to_data_dir(), "processed",
                    "license_plate", "license_plate.csv"))

    # border vicinity

    df_border = data.border_vicinity.load_data()
    df_border.to_csv(os.path.join(data.utils.path_to_data_dir(),
                     "processed", "border", "border.csv"))

    # education

    df_education = data.education.prep_data()
    df_education.to_csv(os.path.join(
        data.utils.path_to_data_dir(), "processed", "education", "education.csv"))

    # household

    df_household = data.household.prep_data()
    df_household.to_csv(os.path.join(
        data.utils.path_to_data_dir(), "processed", "household", "household.csv"))

    #  merge

    df = df_regions.merge(df_income, on="kreis_key", how="outer")
    df = df.merge(df_crime, on="kreis_key", how="outer")
    df = df.merge(df_population, on="kreis_key", how="outer")
    df = df.merge(df_border, on="kreis_key", how="outer")
    df = df.merge(df_education, on="kreis_key", how="outer")
    df = df.merge(df_household, on="kreis_key", how="outer")

    # Calculate Crime Rates

    crime_years = range(2013, 2020)

    for year in crime_years:
        df[f"crimes_pp_{year}"] = pd.to_numeric(
            df[f"crimes_{year}"], errors="coerce") / pd.to_numeric(df[f"population_{year}"], errors="coerce")

    df.to_csv(os.path.join(data.utils.path_to_data_dir(), "processed", "data.csv"))

    return df


if __name__ == "__main__":
    df = prep_data()
