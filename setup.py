import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IF_LICENSE_PLATES_COULD_TALK",
    version="0.0.1",
    author="Moritz Hartlieb",
    author_email="moritz-hartlieb@web.de",
    description="German license plates' geographical information is used to link them to income and crime.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dullibri/if_license_plates_could_talk",
    project_urls={
        "Bug Tracker": "https://github.com/dullibri/if_license_plates_could_talk/issues",
    },
    classifiers=[],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    package_data={
        "": ["data", "geo"]
    }
)
