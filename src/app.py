import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import data
import os
import geopandas as gpd
import pyproj

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def data_for_map():
    df_geo = gpd.read_file(os.path.join("..", "geo", "shapefiles", "kreisgrenzen_2019-shp", "Kreisgrenzen_2019.shp"))
    df_geo.to_crs(pyproj.CRS.from_epsg(4326), inplace = True)

    df_raw = data.load_data()
    df = df_raw[df_raw.columns[1:]]
    df = df.drop_duplicates()
    df = df.sort_values("kreis_key").reset_index(drop=True)
    df = df[["kreis_key", "kreis_name",  "income_pp_2018", "income_2018", "crimes_2018", "population_2018", "crimes_pp_2018"]]
    df = df.dropna()
    df.kreis_key = df.kreis_key.astype(int).astype(str).str.zfill(5)
    df.income_pp_2018 = pd.to_numeric(df.income_pp_2018)


    df = df_raw[df_raw.columns[1:]]
    df = df.drop_duplicates()
    df = df.sort_values("kreis_key").reset_index(drop=True)
    df = df[["kreis_key", "kreis_name",  "income_pp_2018", "income_2018", "crimes_2018", "population_2018", "crimes_pp_2018"]]
    df = df.dropna()
    df.kreis_key = df.kreis_key.astype(int).astype(str).str.zfill(5)
    df.income_2018 = pd.to_numeric(df.income_2018)
    df.population_2018 = pd.to_numeric(df.population_2018)
    df.crimes_2018 = pd.to_numeric(df.crimes_2018)

    df_abs = df[["kreis_key", "income_2018", "population_2018", "crimes_2018"]]

    df_comb = df_geo.merge(df_abs, left_on = "RS", right_on = "kreis_key", how = "left", validate ="one_to_one")

    df_comb["bl_key"] = df_comb.kreis_key.str.slice(0, 2)

    df_coarse = df_comb.dissolve(by="bl_key", aggfunc = "sum")

    df_coarse["crimes_pp_2018"] = df_coarse.crimes_2018 / df_coarse.population_2018

    df_coarse["income_pp_2018"] = df_coarse.income_2018 / df_coarse.population_2018


    return df_coarse

df_coarse = data_for_map()

def generate_map(column):
    fig = px.choropleth(df_coarse, geojson=df_coarse.geometry, locations=df_coarse.index, color=column, scope = "europe", labels={
        "crimes_pp_2018" : "Erfasste Straftaten / EW",
        "income_pp_2018" : "Verfügbares Einkommen der priv. Haushalte / EW",
        "bl_key" : "Bundesland"
    })
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return dcc.Graph(
        id='map_crimes',
        figure=fig
    )

app.layout = html.Div(children=[
    html.H1(children="IF_LICENSE_PLATES_COULD_TALK"),
    dcc.Dropdown(
        id = "dropdown",
        options=[{
            "label":"Straftaten", "value": "crimes_pp_2018"},{
            "label":"Einkommen", "value": "income_pp_2018"
        }],
        value = "crimes_pp_2018"
    ),
    html.Div(id="map-container")
])

@app.callback(
    dash.dependencies.Output("map-container", "children"),
    [dash.dependencies.Input("dropdown", "value")])
def update_map(value):
    return generate_map(value)

if __name__ == '__main__':
    app.run_server(debug=True)