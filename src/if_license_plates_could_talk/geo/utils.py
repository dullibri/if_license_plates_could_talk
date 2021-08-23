import geopandas as gpd
import os
import pyproj


def load_geodata():
    df_geo = gpd.read_file(os.path.join(
        "..", "geo", "shapefiles", "kreisgrenzen_2019-shp", "Kreisgrenzen_2019.shp"))
    df_geo.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    return df_geo
