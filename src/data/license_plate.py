import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

def prep_data():
    wiki_kreise = requests.get("https://de.wikipedia.org/wiki/Liste_der_Landkreise_in_Deutschland")

    soup = BeautifulSoup(wiki_kreise.text, features="html.parser")

    df_kreise = pd.DataFrame()

    for tr in soup.find_all('tr'):
        """Format: <tr>
                    <td>REGIONAL_SCHLÜSSEL</td>
                    <td>LANDKREIS</td>
                    <td>KFZ-KENNZ</td>
                    <td>BUNDESLAND</td>
                    <td>KREISSITZ</td>
                    <td>EINWOHNER</td>
                    <td>FLÄCHE</td>
                    <td>BeVÖLKERUNGSDICHTE</td>
                    <td>KARTE</td></tr>
                    <tr>"""
        tds = tr.find_all('td')
        if(len(tds)>5):
            kreis_key = tds[0].text.strip()
            kreis = tds[1].text.split(",")[0].strip()
            license_plates = tds[2].text.replace(",", " ").replace("(", " ").replace(")", " ").split()

            for license_plate in license_plates:
                df_kreise = df_kreise.append({"license_plate": license_plate.strip(), "kreis_key": kreis_key}, ignore_index = True)

    wiki_städte = requests.get("https://de.wikipedia.org/wiki/Liste_der_kreisfreien_St%C3%A4dte_in_Deutschland")

    soup = BeautifulSoup(wiki_städte.text, features="html.parser")

    df_städte = pd.DataFrame()

    for tr in soup.find_all('tr'):
        """ Format:
        <tr>
            <td>WAPPEN</td>
            <td>STADT</td>
            <td>REGIONALSCHLÜSSEL
            </td>
            <td>BUNDESLAND</td>
            <td>RGIERUNGSBEZIRK</td>
            <td>KFZ-KENNZEICHEN
            </td>
            <td>FLÄCHE
            </td>
            <td>TEINWOHNER 1939
            </td>
            <td>TEINWOHNER 1950
            </td>
            <td>TEINWOHNER 1970
            </td>
            <td>TEINWOHNER 1990
            </td>
            <td>TEINWOHNER 2011
            </td>
            <td>EINWOHNER 2020</small>
            </td>
            <td>BEVDICHTE
            </td>
            <td>KARTE</td></tr>
        """
        tds = tr.find_all('td')
        if(len(tds) > 12):
            kreis_key = tds[2].text.strip()
            kreis = re.split("\(|\[", tds[1].text)[0].strip()
            license_plates = tds[5].text.replace(",", " ").replace("(", " ").replace(")", " ").split()

            if(all(df_kreise["kreis_key"] != kreis_key)): # Avoid duplicates
                for license_plate in license_plates:
                    df_städte = df_städte.append({"license_plate": license_plate.strip(), "kreis_key": kreis_key}, ignore_index = True)

    df = pd.concat([df_städte, df_kreise])

    df["kreis_key"].replace({"11001": "11000"}, inplace = True) # Fix regional code of Berlin ("11000")

    return df