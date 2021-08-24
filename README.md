# if_license_plates_could_talk

German license plates' geographical information is used to link them to income and crime. This will be done by:

1. Associating German license plates with official region codes [AGS](https://de.wikipedia.org/wiki/Amtlicher_Gemeindeschl%C3%BCssel)
2. Collecting data on crime rates in different regions of Germany
3. Collecting data on income in different regions of Germany
4. Merging the above data sets
5. ...

## Visualization

Deployed to [Heroku](https://license-plates-talk.herokuapp.com/).

## Data sources:

- License plates:
    - https://de.wikipedia.org/wiki/Liste_der_kreisfreien_St%C3%A4dte_in_Deutschland
    - https://de.wikipedia.org/wiki/Liste_der_Landkreise_in_Deutschland
- PLZ
    - [Destatis Gemeindeverzeichnis](https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/Archiv/GVAuszugQ/AuszugGV2QAktuell.html;jsessionid=8274FBC848E650875A15A3184CC48E06.live732)
- Crime:
    - [BKA](https://www.bka.de/DE/AktuelleInformationen/StatistikenLagebilder/PolizeilicheKriminalstatistik/PKS2017/BKATabellen/bkaTabellenLaenderKreiseStaedteFaelle.html) (2013-2020)

- Income:
    - https://www.regionalstatistik.de/ (2000-2018)
    - https://www.statistikportal.de/de/vgrdl/ergebnisse-kreisebene/einkommen-kreise
