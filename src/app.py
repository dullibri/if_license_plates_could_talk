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

print(df.info())

df_comb = df_geo.merge(df, left_on = "RS", right_on = "kreis_key", how = "left", validate ="one_to_one")





fig = px.choropleth(df_comb, geojson=df_comb.geometry, locations=df_comb.index, color="crimes_pp_2018", scope = "europe")
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


app.layout = html.Div(children=[
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)