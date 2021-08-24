import data
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px
import os
import geo.utils
from visualization.config import feature_info

df_geo = geo.utils.load_geodata()
df = data.db.get_data()

df_comb = df_geo.merge(df, left_on="RS", right_on="kreis_key", how="left")


def generate_static_map(feature, year=""):
    """Generate static maps

    Args:
        feature (str): feature column
        year (int): [year
    """
    if year != "":
        col = f"{feature}_{year}"
        title_ = feature_info[feature]["title"]
        title = f"{title_} ({year})"
    else:
        col = feature
        title = feature_info[feature]["title"]

    fig = px.choropleth(df_comb, geojson=df_comb.geometry, locations=df_comb.index, color=col, scope="europe",
                        color_continuous_scale="gray_r",
                        title=title,
                        range_color=(df_comb[col].min(
                        )*0.8, df[col].max()),
                        labels={
                            col: feature_info[feature]["label"]
                        })
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(hoverlabel={"bgcolor": "white"},
                      title_font_color="black", font_color="black")

    fig.add_annotation(dict(font=dict(color='black', size=11),
                            x=-0.1,
                            y=-0.12,
                            showarrow=False,
                            text="Quelle: BKA, Regionaldatenbank Deutschland",
                            textangle=0,
                            xanchor='left',
                            xref="paper",
                            yref="paper"))

    fig.write_image(os.path.join(os.path.dirname(__file__),
                    "..", "..", "output", f"{col}.png"), scale=1)


if __name__ == "__main__":
    years = range(2018, 2019)

    for feature in feature_info:
        if feature_info[feature]["time_dep"]:
            for year in years:
                generate_static_map(feature, year)
        else:
            generate_static_map(feature)
