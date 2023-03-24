import pandas as pd
from faker import Faker
from datetime import datetime
import folium
import streamlit as st
import pydeck as pdk

# Créer une instance du module Faker
fake = Faker('fr_FR')

# Charger votre fichier CSV dans un DataFrame
def parser(x):
    return datetime.strptime(x, '%m%Y')

df = pd.read_csv('ts_brutt.csv', sep=";",index_col=0,parse_dates=[1], date_parser=parser).squeeze(axis=1)
df['valeur'] = df['valeur'].fillna(0)

clients_df = pd.DataFrame({'client': df['client'].unique()})

# Ajouter une colonne "adresse" au hasard pour chaque client
df['adresse'] = [fake.address() for _ in range(len(df))]

# Créer un dictionnaire qui fait correspondre chaque adresse à une commune de la wilaya de Bejaia
communes = {
    'Avenue de la Liberté': 'Bejaia',
    'Rue du 20 Août': 'Tichy',
    'Boulevard Colonel Amirouche': 'Akbou',
    'Cité 240 logements': 'Oued Ghir',
    'Route de Sidi Ayad': 'Aokas',
    # Ajouter des adresses au hasard et les communes correspondantes
}

# Ajouter une colonne "commune" avec le nom de la commune correspondante pour chaque adresse
df['commune'] = df['adresse'].map(communes)


merged_df = pd.merge(df, clients_df, on=['client'])


# Enregistrer le DataFrame modifié dans un nouveau fichier CSV
merged_df.to_csv('nouveau_fichier.csv', index=False, columns=['client', 'concat', 'valeur', 'adresse', 'commune'])

# Convertir le DataFrame en JSON avec un index unique
df_json = df.reset_index().to_json(orient='columns')

# Créer une carte centrée sur Bejaia
bejaia_map = pdk.Deck(
    map_style='mapbox://styles/mapbox/streets-v11',
    initial_view_state=pdk.ViewState(
        latitude=36.7512,
        longitude=5.0568,
        zoom=12,
        pitch=50
    )
)

# Récupérer l'ID client entré par l'utilisateur
client_id = st.text_input('Saisir l\'ID client à localiser')

# Filtrer le DataFrame sur l'ID client entré
filtered_df = df.loc[df['client'] == client_id]

# Afficher un message d'erreur si l'ID client n'existe pas
if len(filtered_df) == 0:
    st.warning("Le client sélectionné n'existe pas dans la base de données.")
else:
    # Créer un marqueur sur la carte pour l'emplacement du client
    marker = pdk.Layer('ScatterplotLayer', data=filtered_df, get_position='[longitude, latitude]',
                      get_radius=200, get_color=[255, 0, 0], pickable=True, auto_highlight=True,
                      radius_scale=5, radius_min_pixels=10, radius_max_pixels=30,
                      tooltip=['adresse', 'valeur', 'client'])
    # Ajouter le marqueur à la carte
    bejaia_map.add_layer(marker)
    # Afficher la carte
    st.pydeck_chart(bejaia_map.to_json())