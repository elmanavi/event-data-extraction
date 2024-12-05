from collections import defaultdict

import streamlit as st
import pandas as pd
import numpy as np

from src.persistence.db import *
import streamlit_nested_layout


# Funktion zur Initialisierung der Datenbankverbindung
@st.cache_resource
def init_connection():
    return Database()


def submit_text_input():
    st.session_state.label = st.session_state.label_widget
    st.session_state.label_widget = ""
    st.session_state.query = st.session_state.query_widget
    st.session_state.query_widget = ""

    if "query" in st.session_state and "label" in st.session_state:
        db.insert_document(
            CollectionNames.MAPS_QUERIES,
            {"label": st.session_state.label,"query": st.session_state.query}
        )
        st.session_state.maps_queries = db.get_collection_contents(CollectionNames.MAPS_QUERIES)
        st.success("Eintrag erfolgreich gespeichert!")

    else:
        st.error("Beide Felder müssen ausgefüllt sein!")


# Datenbankverbindung initialisieren
db = init_connection()

# Laden der aktuellen Inhalte aus der Datenbank
if "maps_queries" not in st.session_state:
    st.session_state.maps_queries = db.get_collection_contents(CollectionNames.MAPS_QUERIES)
if "unsorted_urls" not in st.session_state:
    st.session_state.unsorted_urls = list(db.get_collection_contents(CollectionNames.UNSORTED_URLS))

maps_queries = st.session_state.maps_queries

# Titel der App
st.title("Übersicht über die Datenbank-Inhalte")


st.subheader("Aktuelle Einträge in der DB")
df = pd.DataFrame({
    "DB-Collection":[
       # CollectionNames.MAPS_QUERIES,
       CollectionNames.UNSORTED_URLS,
       CollectionNames.EVENT_URLS],
    "Anzahl an Einträgen":[
       # len(list(db.get_collection_contents(CollectionNames.MAPS_QUERIES))),
       len(st.session_state.unsorted_urls),
       len(list(db.get_collection_contents(CollectionNames.EVENT_URLS))) ],
    "Bereits gecrawled":[
        len([i for i in st.session_state.unsorted_urls if "crawled" in i]),
        len([i for i in list(db.get_collection_contents(CollectionNames.EVENT_URLS)) if "crawled" in i])

    ]})


st.table(df)


st.subheader("Einträge in Unsorted URLs sortiert nach url_types")
grouped_urls = defaultdict(list)

# Gruppiere nach url_type
for url in st.session_state.unsorted_urls:
    grouped_urls[url["url_type"]].append(url)

# Umwandeln in eine Liste von Listen
result = list(grouped_urls.values())

# Ausgabe
for group in result:
    with st.expander(f"{group[0]["url_type"]} ({len(group)})"):
        for element in group:
            st.write(f"Base Url: {element["url"]}")
            if "overview_pages" in element:
                with st.expander("Übersichtsseiten"):
                    for page in element["overview_pages"]:
                        st.write(page)


# st.subheader("Google Maps Queries")
# # Formular für Label und Query
# with st.form("input_form"):
#     st.write("""
#     **Queries** werden für Anfragen an die Google Maps API verwendet im Format: `[query] [location]`.
#     **Beispiel**: `Livemusik Nuernberg`.
#     Das **Label** wird später bei den gefundenen Urls als `url_type` gespeichert
#     Queries sollten sich also auf **Veranstaltungsorte** oder **-arten** beziehen. Es ist sinnvoll die Anfragen kurz in Google Maps zu testen.
#     """)
#     st.text_input("Query eingeben:", key="query_widget", placeholder="Nachtclub")
#     st.text_input("Label eingeben:", key="label_widget", placeholder="night_club")
#
#
#     # Submit-Button innerhalb des Formulars
#     submitted = st.form_submit_button("Speichern", on_click=submit_text_input)
#
#
# # Anzeigen der gespeicherten Inhalte
# st.write("""###### Google Maps Queries aus der Datenbank:""")
# df = pd.DataFrame([{"Label": q['label'], "Query": q['query']} for q in maps_queries])
#
# st.table(df)


overview_pages = [i for i in st.session_state.unsorted_urls if "overview_pages" in i]
st.subheader(f" {len(overview_pages)} URLs enthalten Übersichtsseiten:")

for element in overview_pages:
    with st.expander(f"Base Url: {element["url"]}, Type: {element["url_type"]}"):
        for url in element["overview_pages"]:
            st.write(url)




