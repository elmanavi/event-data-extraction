from src.persistence.db import *
import streamlit as st
from urllib.parse import urlparse
import streamlit_nested_layout

@st.cache_resource
def init_connection():
    return Database()

def get_urls():
    result =  list(db.get_collection_contents(CollectionNames.EVENT_URLS))
    return {item['url'].lower() for item in result if 'url' in item}

db = init_connection()

# Content
st.title("Übersicht über Event URLs")
urls = get_urls()

st.write(len(urls), " URLs in der Datenbank")

# Funktion zum Überprüfen, ob eine URL ein Event, Veranstaltung oder Kalender enthält
def is_event_url(url):
    keywords = ["veranstaltung", "event", "kalender"]
    return any(keyword in url.lower() for keyword in keywords)

# Funktion zur Erzeugung der hierarchischen Baumstruktur
def build_url_tree(urls):
    tree = {}

    for url in urls:
        if is_event_url(url):
            parsed_url = urlparse(url)
            scheme_netloc = f"{parsed_url.scheme}://{parsed_url.netloc}"
            path = parsed_url.path.strip('/')
            path_segments = path.split('/') if path else []

            current_level = tree
            current_url = scheme_netloc

            # Insert the main URL node
            if current_url not in current_level:
                current_level[current_url] = {}
            current_level = current_level[current_url]

            # Insert sub-paths
            for segment in path_segments:
                current_url = f"{current_url}/{segment}"
                if current_url not in current_level:
                    current_level[current_url] = {}
                current_level = current_level[current_url]

    return tree

# Funktion zum Anzeigen der Baumstruktur mit einem Löschen-Button für jede URL
def display_tree_with_delete_buttons(url_tree):
    for url, sub_tree in sorted(url_tree.items()):
        # Zeige die Domain im Expander (nur die Domain, keine Sub-URLs)
        with st.expander(f"**{url}**"):  # Expander für jede Domain
            # Löschen-Button für die aktuelle Domain
            delete_button = st.button(f"(Löschen)", key=f"delete_{url}")
            if delete_button:
                delete_url_and_children(url)

            # Zeige alle Unter-URLs mit entsprechender Einrückung in weiteren Expandern
            if sub_tree:
                display_sub_urls(sub_tree)  # Unterknoten im Expander anzeigen

# Funktion zum Löschen einer URL und ihrer Kinder
def delete_url_and_children(url_to_delete):
    print("Deleting Subtree of ", url_to_delete )
    for url in urls:
        if url_to_delete in url:
            print("deleting ", url)
            print(db.delete_document_by_url(CollectionNames.EVENT_URLS, url))




# Funktion zum Anzeigen der Sub-URLs (Pfadsegmente) innerhalb einer Domain
def display_sub_urls(sub_tree):
    for key, subtree in sorted(sub_tree.items()):
        # Expander für jedes Sub-Element
        with st.expander(f"{key}"):  # Unter-URL als Expander anzeigen
            # Löschen-Button für jedes Unterelement
            delete_button = st.button(f"(Löschen)", key=f"delete_{key}")
            if delete_button:
                delete_url_and_children(key)
            # Rekursiv alle Sub-URLs anzeigen
            if subtree:
                display_sub_urls(subtree)  # Weitere Unterknoten anzeigen


# URLs nach Event filtern und in Baumstruktur organisieren
url_tree = build_url_tree(urls)

# Ausgabe der Baumstruktur mit Löschen-Button für jede URL
st.markdown("## URL-Baumstruktur:")
display_tree_with_delete_buttons(url_tree)
