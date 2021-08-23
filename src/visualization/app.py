from re import S
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import geopandas as gpd
import dash_bootstrap_components as dbc
import geo.utils
import data


class VisApp:
    def __init__(self):
        """Setup Dash App"""
        # setup data
        self.df = self.data_for_map()

        self.cache = {}

        # configuration for visualization

        self.columns = {
            "crimes_pp": {
                "title": "Erfasste Straftaten",
                "color_continuous_scale": "Bluered_r"
            },
            "income_pp": {
                "title": "Verfügbares Einkommen der priv. Haushalte",
                "color_continuous_scale": "Inferno"
            }
        }

        # creating a dash app
        self.app = dash.Dash(__name__, external_stylesheets=[
                             dbc.themes.BOOTSTRAP])
        self.app.title = "IF_LICENSE_PLATS_COULD_TALK"
        self.app.layout = dbc.Container([
            html.H1(children="IF_LICENSE_PLATES_COULD_TALK",
                    style={"margin-top": "30px"}),
            dbc.Container([
                html.P("Merkmal:"),
                dcc.Dropdown(
                    id="feature_select",
                    options=[{
                        "label": "Erfasste Straftaten", "value": "crimes_pp"}, {
                        "label": "Verfügbares Einkommen der privaten Haushalte", "value": "income_pp"
                    }],
                    value="crimes_pp"
                )],  style={"margin-top": "20px"}),
            dbc.Container([
                html.P("Jahr:"),
                dcc.Slider(id="year", min=2017, max=2018, value=2018, marks={2017: "2017", 2018: "2018"})], style={"margin-top": "20px"}),
            html.Hr(),
            dbc.Container(id="output"),
            dcc.Store(id="state")
        ])
        self.setup_callbacks()

    def run(self):
        """Start Dash server in debug mode"""
        self.app.run_server(debug=True)

    def generate_output(self, feature, year):
        """Generate map and histogram"""
        return [
            dbc.Row([
                dbc.Col([
                    html.Div(id="map-container",
                             children=[self.generate_map(feature, year)])
                ])
            ])
        ]

    def setup_callbacks(self):
        """Setup the callbacks for the Dash app"""
        @self.app.callback(
            dash.dependencies.Output("output", "children"),
            [dash.dependencies.Input("feature_select", "value"), dash.dependencies.Input("year", "value")])
        def update_map(feature, year):
            return self.generate_output(feature, year)

    def data_for_map(self):
        """Load data for visualization"""
        df_geo = geo.utils.load_geodata()
        df = data.db.get_data()

        df_comb = df_geo.merge(
            df, left_on="RS", right_on="kreis_key", how="left")

        return df_comb

    def generate_map(self, feature, year):
        """Generate the map visualization for the given column"""
        col = f"{feature}_{year}"
        if True:

            fig = px.choropleth(self.df, geojson=self.df.geometry, locations=self.df.index, color=col, scope="europe",
                                color_continuous_scale=self.columns[feature]["color_continuous_scale"],
                                range_color=(self.df[col].min(
                                )*0.8, self.df[col].max()),
                                hover_name="kreis_name",
                                labels={
                                    f"crimes_pp_{year}": "Straftaten / EW",
                                    f"income_pp_{year}": "Euro / EW"
                                })
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            fig.update_layout(hoverlabel={"bgcolor": "white"})

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

            return dcc.Graph(
                id='map',
                figure=fig
            )
