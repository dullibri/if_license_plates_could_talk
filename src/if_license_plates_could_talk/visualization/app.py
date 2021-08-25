
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
                             dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css"])
        self.app.title = "IF_LICENSE_PLATES_COULD_TALK"
        self.app.layout = dbc.Container([
            dcc.Location(id="url", refresh=False),
            html.H1(children="IF_LICENSE_PLATES_COULD_TALK",
                    style={"margin-top": "30px"}),
            dbc.Container(id="page-content", children=[
                self.generate_nav_page(),
                self.generate_scatter_page(),
                self.generate_map_page()
            ]),
        ])
        self.setup_scatter_callbacks()
        self.setup_map_callbacks()
        self.setup_nav_callbacks()

    def run(self):
        """Start Dash server in debug mode

        Returns:
            None
        """
        self.app.run_server(debug=True)

    def generate_map_page(self):
        return dbc.Container([
            dbc.Container([
                html.P("Feature:"),
                dcc.Dropdown(
                    id="map_feature_select",
                    options=[{"label": self.columns[feature]["title"],
                              "value": feature} for feature in self.columns],
                    value="crimes_pp"
                )],  style={"margin-top": "20px"}),
            dbc.Container([
                html.P("Year:"),
                dcc.Slider(id="map_year", min=2013, max=2018, value=2018, marks={y: f"{y}" for y in range(2013, 2019)})], style={"margin-top": "20px"}),
            html.Hr(),
            dcc.Loading(id="map_loading", type="circle",
                        children=[dbc.Container(id="map_output")])])

    def generate_scatter_page(self):

        return dbc.Container(
            [dbc.Row([dbc.Col(children=[
                html.P("Feature (x-axis):"),
                dcc.Dropdown(
                    id="scatter_feature_x",
                    options=[{"label": self.columns[feature]["title"],
                              "value": feature} for feature in self.columns],
                    value="crimes_pp"
                )]), dbc.Col(children=[html.P("Scale (x-axis):"),
                                       dcc.Dropdown(
                    id="scatter_log_x", options=[{"label":  "linear",
                                                  "value": "linear"}, {"label": "log", "value": "log"}],
                    value="linear"
                )])], style={"margin-top": "20px"}),
                dbc.Row([dbc.Col(children=[
                    html.P("Feature (y-axis):"),
                    dcc.Dropdown(
                        id="scatter_feature_y",
                        options=[{"label": self.columns[feature]["title"],
                                  "value": feature} for feature in self.columns],
                        value="income_pp"
                    )]), dbc.Col(children=[html.P("Scale (y-axis):"),
                                           dcc.Dropdown(
                        id="scatter_log_y", options=[{"label":  "linear",
                                                      "value": "linear"}, {"label": "log", "value": "log"}],
                        value="linear"
                    )])],  style={"margin-top": "20px"}),
             dbc.Container([
                 html.P("Year:"),
                 dcc.Slider(id="scatter_year", min=2013, max=2018, value=2018, marks={y: f"{y}" for y in range(2013, 2019)})], style={"margin-top": "20px"}),
             html.Hr(),
             dcc.Loading(id="scatter_loading", type="circle",
                         children=[dbc.Container(id="scatter_output")])
             ])

    def generate_scatter_plot(self, feature_x, log_x,  feature_y, log_y, year):
        featinfo_x = self.columns[feature_x]
        col_x = feature_x
        if featinfo_x["time_dep"]:
            col_x += f"_{year}"
        log_x = log_x == "log"

        featinfo_y = self.columns[feature_y]
        col_y = feature_y
        if featinfo_y["time_dep"]:
            col_y += f"_{year}"
        log_y = log_y == "log"

        fig = px.scatter(data_frame=self.df,
                         x=col_x, y=col_y, hover_data=["kreis_name"],
                         labels={col_x: featinfo_x["label"],
                                 col_y: featinfo_y["label"]},
                         log_x=log_x,
                         log_y=log_y,
                         trendline="ols",
                         trendline_options=dict(log_x=log_x, log_y=log_y),
                         trendline_color_override="red")

        return dcc.Graph(
            id='scatter',
            figure=fig
        )

    def generate_time_series_page(self):
        return dbc.Container(
            [html.H2("Time series")]
        )

    def generate_nav_page(self):
        def gen_link(title, page, icon):
            return dcc.Link(children=[html.P(html.I(className=f"bi-{icon}")), html.P(title)], href=f"/{page}")

        return html.Div(id="nav", children=[dbc.Row([dbc.Col(gen_link("Maps", "map", "map")),
                                                     dbc.Col(
            gen_link("Scatter Plots", "scatter", "table")),
            dbc.Col(gen_link("Time Series", "timeseries", "bar-chart-line"))])])

    def generate_map_output(self, feature, year):
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
                    html.Div(id="map_container",
                             children=[self.generate_map(feature, year)])
                ])
            ])
        ]

    def setup_nav_callbacks(self):
        @ self.app.callback(dash.dependencies.Output('page-content', 'children'),
                            [dash.dependencies.Input('url', 'pathname')])
        def display_page(pathname):
            if pathname == "/":
                return self.generate_nav_page()
            elif pathname == "/map":
                return self.generate_map_page()
            elif pathname == "/scatter":
                return self.generate_scatter_page()
            elif pathname == "/timeseries":
                return self.generate_time_series_page()
            else:
                return "404"

    def setup_map_callbacks(self):
        """Setup the callbacks for the map page

        Returns:
            None
        """
        @ self.app.callback(
            dash.dependencies.Output("map_output", "children"),
            [dash.dependencies.Input("map_feature_select", "value"), dash.dependencies.Input("map_year", "value")])
        def update_map(feature, year):
            return self.generate_map_output(feature, year)

    def setup_scatter_callbacks(self):
        """Setup the callbacks for the scatter page
        """
        @ self.app.callback(
            dash.dependencies.Output("scatter_output", "children"),
            [dash.dependencies.Input("scatter_feature_x", "value"), dash.dependencies.Input("scatter_log_x", "value"), dash.dependencies.Input(
                "scatter_feature_y", "value"), dash.dependencies.Input("scatter_log_y", "value"), dash.dependencies.Input("scatter_year", "value")])
        def update_map(feature_x, log_x, feature_y, log_y, year):
            return self.generate_scatter_plot(feature_x, log_x,  feature_y, log_y,  year)

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
