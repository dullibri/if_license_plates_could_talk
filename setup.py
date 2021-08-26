import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IF_LICENSE_PLATES_COULD_TALK",
    version="0.0.5",
    author="Moritz Hartlieb",
    description="German license plates' geographical information is used to link them to income and crime.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dullibri/if_license_plates_could_talk",
    project_urls={
        "Bug Tracker": "https://github.com/dullibri/if_license_plates_could_talk/issues",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "bs4",
        "dash",
        "dash-bootstrap-components",
        "dash-core-components",
        "dash-html-components",
        "geopandas",
        "matplotlib",
        "numpy",
        "openpyxl",
        "pandas",
        "plotly",
        "pyproj",
        "requests",
        "scikit-learn",
        "scipy",
        "statsmodels",
        "xlrd",
        "geopy",
        "gunicorn"
    ],
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.xlsx", "*.db", "*.dbf", "*.prj", "*.shp", "*.shx"]
    }
)
