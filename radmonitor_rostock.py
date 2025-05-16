# %%

import pandas as pd
import requests
import io
# %%
url = "https://geo.sv.rostock.de/download/opendata/radmonitore/radmonitore_daten.csv"

#%%
response = requests.get(url, verify=True)
df = pd.read_csv(io.StringIO(response.text))

# %%
df['zeitpunkt'] = pd.to_datetime(df['zeitpunkt'], utc= True)
# %%
# pivot Tabelle erstellen
df_pivot_datum = df.pivot_table(index = 'zeitpunkt', columns="standort_id", values ="summe", aggfunc="sum")

# %%
#als Flächendiagramm anzeigen lassen (Y = jährliche Summe)
df_pivot_datum.resample('Y').sum().plot.area()
# %%
#Daten für Standorte der Radmonitore einlesen
url_1 = "https://geo.sv.rostock.de/download/opendata/radmonitore/radmonitore_standorte.csv"
response = requests.get(url_1, verify=True)
df_standorte = pd.read_csv(io.StringIO(response.text))
# %%
# die untersten sieben Zeilen der Tabelle filtern
df7tage = df_pivot_datum.resample('D').sum().iloc[-7:]
# %%
#Daten transponieren
df7tage_gedreht = df7tage.T
# %%
df7tage_gedreht = df7tage_gedreht.reset_index()
# %%
df7tage_gedreht
# %%
#Tabellen zusammenführen
df_gesamt = pd.merge(df_standorte, df7tage_gedreht,left_on="id", right_on="standort_id", how="left")
df_gesamt
# %%
df_gesamt.to_csv("radmonitor_rostock.csv")

# %%
# Spalten als Datetime parsen (angenommen alle Spalten sind Datumsstrings)
datums_spalten = df_gesamt.columns[-7:]

# Schritt 2: Datumswerte als datetime parsen und sortieren
datums_werte = pd.to_datetime(datums_spalten, format="%d.%m.%Y")
sortierte_werte, sortierte_spalten = zip(*sorted(zip(datums_werte, datums_spalten)))

# Schritt 3: DataFrame nach den sortierten Datumsspalten anordnen
df_daten = df_gesamt.loc[:, list(sortierte_spalten)].copy()

# Neuestes Datum (der letzte in der sortierten Liste)
neuestes_datum = sortierte_werte[-1].strftime("%d.%m.%Y")

# Neue Spalte 'datum' mit diesem Wert
df_daten["datum"] = neuestes_datum

# Spalten umbenennen: von -7 bis -1
neue_namen = {alt: str(neu) for alt, neu in zip(sortierte_spalten, range(-7, 0))}
df_daten.rename(columns=neue_namen, inplace=True)

# Restliche Spalten beibehalten (alle außer den letzten 7)
df_rest = df_gesamt.iloc[:, :-7]

# Alles zusammenfügen
df_gesamt_neu = pd.concat([df_rest, df_daten], axis=1)

# %%
df_gesamt_neu.to_csv("df_gesamt_neu.csv")
# %%
