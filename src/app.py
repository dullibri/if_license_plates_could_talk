import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import data
import os
import geopandas as gpd
import pyproj
import dash_bootstrap_components as dbc

class VisApp:
    def __init__(self):
        """Setup Dash App"""
        # setup data
        self.df_coarse = self.data_for_map()

        # configuration for visualization

        self.columns = {
            "crimes_pp_2018" : {
                "title": "Erfasste Straftaten",
                "color_continuous_scale" : px.colors.diverging.RdBu,
                "nbins": 20,
            },
            "income_pp_2018": {
                "title": "Verfügbares Einkommen der priv. Haushalte",
                "color_continuous_scale" : "Inferno",
                "nbins" : 20,
            }
        }

        # creating a dash app
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.app.title = "IF_LICENSE_PLATS_COULD_TALK"
        self.app.layout = dbc.Container([
            html.H1(children="IF_LICENSE_PLATES_COULD_TALK", style={"margin-top": "30px"}),
            dbc.Container([
            html.P("Merkmal:"),
            dcc.Dropdown(
                id = "dropdown",
                options=[{
                    "label":"Erfasste Straftaten", "value": "crimes_pp_2018"},{
                    "label":"Verfügbares Einkommen der privaten Haushalte", "value": "income_pp_2018"
                }],
                value = "crimes_pp_2018"
            )],  style={"margin-top": "20px"}),
            dbc.Container([
            html.P("Jahr:"),
            dcc.Slider(id="year", min = 2018, max = 2018, value = 2018, marks = {2018: "2018"})], style={"margin-top": "20px"}),
            html.Hr(),
            dbc.Container(id = "output")
        ])
        self.setup_callbacks()

    def run(self):
        """Start Dash server in debug mode"""
        self.app.run_server(debug=True)
    
    def generate_output(self, column):
        """Generate map and histogram"""
        return [
            dbc.Row([
                dbc.Col([
                    html.Div(id="map-container", children = [self.generate_map(column)])
                ]),
                dbc.Col([
                    html.Div(id="hist-container", children = [self.generate_hist(column)])
                ])
            ])
        ]

    def setup_callbacks(self):
        """Setup the callbacks for the Dash app"""
        @self.app.callback(
        dash.dependencies.Output("output", "children"),
        [dash.dependencies.Input("dropdown", "value")])
        def update_map(value):
            return self.generate_output(value)

    def data_for_map(self):
        # TODO: Refactor this into data/...
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

        df_coarse.reset_index()

        df_coarse["crimes_pp_2018"] = df_coarse.crimes_2018 / df_coarse.population_2018

        df_coarse["income_pp_2018"] = df_coarse.income_2018 / df_coarse.population_2018

        return df_coarse

    def generate_map(self, column):
        """Generate the map visualization for the given column"""
        fig = px.choropleth(self.df_coarse, geojson=self.df_coarse.geometry, locations=self.df_coarse.index, color=column, scope = "europe", 
        color_continuous_scale=self.columns[column]["color_continuous_scale"],
        range_color = (self.df_coarse[column].min()*0.8, self.df_coarse[column].max()),
        color_continuous_midpoint=self.df_coarse[column].median(),
        labels={
            "crimes_pp_2018" : "Straftaten / EW",
            "income_pp_2018" : "T€ / EW",
            "bl_key" : "Bundesland"
        })
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        return dcc.Graph(
            id='map',
            figure=fig
        )
    
    def generate_hist(self, column):
        """Generate a histogramm for the values of the given column"""
        fig = px.histogram(self.df_coarse, x = column, nbins = self.columns[column]["nbins"], labels={
            "crimes_pp_2018" : "Straftaten / EW",
            "income_pp_2018" : "T€ / EW",
            "bl_key" : "Bundesland"
        })
        return dcc.Graph(
            id = "histo",
            figure = fig
        )

if __name__ == '__main__':
    app = VisApp()
    server = app.app.server
    app.run()