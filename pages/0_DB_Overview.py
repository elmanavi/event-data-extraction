from collections import defaultdict
import streamlit.components.v1 as components
import pandas as pd
from src.persistence.db import *
import streamlit_nested_layout


# Funktion zur Initialisierung der Datenbankverbindung
@st.cache_resource
def init_connection():
    return Database()

# Datenbankverbindung initialisieren
db = init_connection()

# Laden der aktuellen Inhalte aus der Datenbank
if "unsorted_urls" not in st.session_state:
    st.session_state.unsorted_urls = list(db.get_collection_contents(CollectionNames.UNSORTED_URLS))
if "event_urls" not in st.session_state:
    st.session_state.event_urls = list(db.get_collection_contents(CollectionNames.EVENT_URLS))

# Titel der App
st.title("Übersicht über die Datenbank-Inhalte")


st.subheader("Aktuelle Einträge in der DB")
st.write("""
    - **unsorted_urls**: Enthält Daten-Objekte bestehend aus Start-Urls, Url-Typ (z.b. "city", "theater") sowie vom Crawler gefundene Sub-Urls.
    - **event_urls**: Enthält Daten-Objekte bestehend aus Url, Referenz zur Basis-Url (Start-Url), Klasse (EventDetail / EventOverview) sowie HTML der Seite""")
df = pd.DataFrame({
    "DB-Collection":[
       # CollectionNames.MAPS_QUERIES,
       CollectionNames.UNSORTED_URLS,
       CollectionNames.EVENT_URLS],
    "Anzahl an Einträgen":[
       # len(list(db.get_collection_contents(CollectionNames.MAPS_QUERIES))),
       len(st.session_state.unsorted_urls),
       len(st.session_state.event_urls)],
    "Bereits gecrawled":[
        len([i for i in st.session_state.unsorted_urls if "crawled" in i]),
        len([i for i in st.session_state.event_urls if "crawled" in i])

    ]})


st.table(df)


st.subheader("Einträge in Unsorted Urls")
grouped_urls = defaultdict(list)

# Gruppiere nach url_type
for url in st.session_state.unsorted_urls:
    grouped_urls[url["url_type"]].append(url)

# Umwandeln in eine Liste von Listen
result = list(grouped_urls.values())

# Ausgabe
with st.expander("unsorted_urls sortiert nach url-types"):
    for group in result:
        with st.expander(f"{group[0]["url_type"]} ({len(group)})"):
            for element in group:
                st.write(f"Base Url: {element["url"]}")
                if "overview_pages" in element:
                    with st.expander("Übersichtsseiten"):
                        for page in element["overview_pages"]:
                            st.write(page)


overview_pages = [i for i in st.session_state.unsorted_urls if "overview_pages" in i]
st.write(f" {len(overview_pages)} URLs enthalten potentielle Even-Übersichtsseiten (vom Crawler gefunden):")

with st.expander("unsorted_urls mit Übersichtsseiten"):
    for element in overview_pages:
        with st.expander(f"Base Url: {element["url"]}, Type: {element["url_type"]}"):
            for url in element["overview_pages"]:
                st.write(url)


overview_pages = [e for e in st.session_state.event_urls if e["class"]=="EventOverview"]
detail_pages = [e for e in st.session_state.event_urls if e["class"]=="EventDetail"]

# content
st.subheader("Einträge in Event Urls")
st.write("""
    Die Übersicht zeigt die finalen Daten aus **event_urls**, sortiert nach ihrer Klasse.""")
with st.expander(f"Event-Übersichtsseiten ({len(overview_pages)})"):
    for el in overview_pages:
        with st.expander(el["url"]):
            components.html(el["cleaned_html"] + "<script>window.print = function() {console.log('Drucken ist deaktiviert.');};</script>", height=400, scrolling=True)
with st.expander(f"Event-Detailseiten ({len(detail_pages)})"):
    for el in detail_pages:
        with st.expander(el["url"]):
            components.html(el["cleaned_html"] + "<script>window.print = function() {console.log('Drucken ist deaktiviert.');};</script>", height=400, scrolling=True)




