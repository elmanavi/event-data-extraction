import streamlit.components.v1 as components
import pandas as pd
import streamlit as st
import streamlit_nested_layout
from src.persistence.db import *


# Funktion zur Initialisierung der Datenbankverbindung
@st.cache_resource
def init_connection():
    return init_db()

# Datenbankverbindung initialisieren
db = init_connection()

# Titel der App
st.title("Übersicht über die Datenbank-Inhalte")
st.subheader("Aktuelle Einträge in der DB")
st.write("""
    - **unsorted_urls**: Enthält Daten-Objekte bestehend aus Start-Urls, Url-Typ (z.b. "city", "theater") sowie vom Crawler gefundene Sub-Urls.
    - **event_urls**: Enthält Daten-Objekte bestehend aus Url, Referenz zur Basis-Url (Start-Url), Klasse (EventDetail / EventOverview) sowie HTML der Seite""")
df = pd.DataFrame({
    "DB-Collection":[
       CollectionNames.UNSORTED_URLS,
       CollectionNames.EVENT_URLS],
    "Anzahl an Einträgen":[
        db.unsorted_urls.count_documents({}),
        db.event_urls.count_documents({})],
    "Bereits verarbeitet":[
        db.unsorted_urls.count_documents({"crawled": True}),
        db.event_urls.count_documents({"final":True})
    ]})
st.table(df)

overview_pages = list(db.event_urls.find(filter={"class":"EventOverview", "final":True}, projection={"url":1,"base_url_id":1,"cleaned_html":1}))
detail_pages = list(db.event_urls.find(filter={"class":"EventDetail", "final":True}, projection={"url":1,"base_url_id":1,"cleaned_html":1}) )

st.subheader("Einträge in Event Urls")
st.write("""
    Die Übersicht zeigt die finalen Daten aus **event_urls**, sortiert nach ihrer Klasse.""")
with st.expander(f"Event-Übersichtsseiten ({len(overview_pages)})"):
    try:
        for el in overview_pages:
            with st.expander(f"{el["url"]} - ({db.unsorted_urls.find_one(filter={"_id":el["base_url_id"]}, projection={"url_type":1})["url_type"]})"):
                components.html(el["cleaned_html"] + "<script>window.print = function() {console.log('Drucken ist deaktiviert.');};</script>", height=400, scrolling=True)
    except Exception as e:
        st.write(f"Fehler: {e}")


with st.expander(f"Event-Detailseiten ({len(detail_pages)})"):
    try:
        for el in detail_pages:
            with st.expander(f"{el["url"]} - ({db.event_urls.find_one(filter={"_id":el["base_url_id"]}, projection={"url_type":1})["url_type"]})"):
                components.html(el["cleaned_html"] + "<script>window.print = function() {console.log('Drucken ist deaktiviert.');};</script>", height=400, scrolling=True)
    except Exception as e:
        st.write(f"Fehler bei {el["url"]}: {e} ")




