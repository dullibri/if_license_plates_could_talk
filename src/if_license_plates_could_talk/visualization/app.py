
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
from . import config


class VisApp:
    """Dash application to visualize collected data"""

    def __init__(self):
        """Setup Dash aplication
        """
        # setup data
        self.df = self.data_for_map()

        # configuration for visualization

        self.columns = config.feature_info

        # creating a dash app
        self.app = dash.Dash(__name__, external_stylesheets=[
                             dbc.themes.BOOTSTRAP])
        self.app.title = "IF_LICENSE_PLATS_COULD_TALK"
        self.app.layout = dbc.Container([
            html.H1(children="IF_LICENSE_PLATES_COULD_TALK",
                    style={"margin-top": "30px"}),
            dbc.Container([
                html.P("Feature:"),
                dcc.Dropdown(
                    id="feature_select",
                    options=[{"label": self.columns[feature]["title"],
                              "value": feature} for feature in self.columns],
                    value="crimes_pp"
                )],  style={"margin-top": "20px"}),
            dbc.Container([
                html.P("Year:"),
                dcc.Slider(id="year", min=2013, max=2018, value=2018, marks={y: f"{y}" for y in range(2013, 2019)})], style={"margin-top": "20px"}),
            html.Hr(),
            dcc.Loading(id="loading", type="circle",
                        children=[dbc.Container(id="output")]),
            dcc.Store(id="state")
        ])
        self.setup_callbacks()

    def run(self):
        """Start Dash server in debug mode

        Returns:
            None
        """
        self.app.run_server(debug=True)

    def generate_output(self, feature, year):
        """Generate output structure

        Args:
            feature (str): feature column to display
            year (int): -

        Returns:
            [Component]: dash components to display map of germany with selected regional data.
        """
        return [
            dbc.Row([
                dbc.Col([
                    html.Div(id="map-container",
                             children=[self.generate_map(feature, year)])
                ])
            ])
        ]

    def setup_callbacks(self):
        """Setup the callbacks for the Dash app

        Returns:
            None
        """
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
        """Generate map for visualization

        Args:
            feature (str): feature column
            year (int): year

        Returns:
            dcc.Graph: Map component
        """

        feature_info = self.columns[feature]

        if feature_info["time_dep"]:
            col = f"{feature}_{year}"
        else:
            col = feature

        fig = px.choropleth(self.df, geojson=self.df.geometry, locations=self.df.index, color=col, scope="europe",
                            color_continuous_scale="gray_r",
                            range_color=(self.df[col].min(
                            )*0.8, self.df[col].max()),
                            hover_name="kreis_name",
                            hover_data=[col],
                            labels={
                                col: feature_info["label"]
                            })
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update_layout(hoverlabel={"bgcolor": "white"})

        return dcc.Graph(
            id='map',
            figure=fig
        )
