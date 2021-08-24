import geopy.distance
from shapely.geometry import LinearRing, shape
from . import utils
import data
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px


class DistanceCalculator():
    def __init__(self):
        self.df_geo = utils.load_geodata()
        self.crs = "epsg:32662"
        germany = self.df_geo.dissolve()
        buffered = germany.to_crs(self.crs).buffer(10000).to_crs(germany.crs)
        self.border = buffered.boundary.to_crs(self.crs).explode().iloc[0]

        self.border_shape = shape(self.border)

        self.counter = 0

    def distance(self, kreis_key):
        self.counter += 1
        print(self.counter)
        kreis_geom = self.df_geo[self.df_geo["RS"] == kreis_key]
        center_point = kreis_geom.to_crs(self.crs).centroid
        center_point.reset_index(drop=True, inplace=True)

        pol_ext = LinearRing(self.border_shape.coords)
        d = pol_ext.project(center_point.geometry.loc[0])
        p = pol_ext.interpolate(d)
        cp_x, cp_y = center_point.geometry.loc[0].coords[0]

        closest = list(p.coords)[0]

        point_geometry = gpd.points_from_xy(
            x=[cp_x, closest[0]], y=[cp_y, closest[1]])
        point_df = gpd.GeoDataFrame(
            {}, geometry=point_geometry, crs=self.crs).to_crs(self.df_geo.crs)

        return geopy.distance.geodesic(point_df.loc[0, "geometry"].coords[0], point_df.loc[1, "geometry"].coords[0]).kilometers
