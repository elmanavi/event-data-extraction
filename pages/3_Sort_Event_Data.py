import base64

import streamlit.components.v1 as components
from src.persistence.db import *

@st.cache_resource
def init_connection():
    return Database()

def get_all_urls():
    return [e for e in list(db.get_collection_contents(CollectionNames.EVENT_URLS))  if "final" not in e]

def next_element():
    if st.session_state.index < len(elements) - 1:
        st.session_state.index += 1
    st.session_state.visited_urls = None

def prev_element():
    if st.session_state.index > 0:
        st.session_state.index -= 1
    st.session_state.visited_urls = None

def render_url_content(element):
    with st.container(border=True):
        components.html(element["cleaned_html"] + "<script>window.print = function() {console.log('Drucken ist deaktiviert.');};</script>", height=400, scrolling=True)

def save_event_url():
    new_element = current_element
    st.session_state.last_element = current_element
    new_element["final"]=True
    result=db.insert_or_update_document(CollectionNames.EVENT_URLS, new_element),
    st.session_state.all_urls = get_all_urls()

def remove_url():
    st.session_state.last_element = current_element
    result = db.delete_document_by_url(CollectionNames.EVENT_URLS, current_element['url']),
    st.session_state.all_urls = get_all_urls()

# Variables
db = init_connection()
if 'index' not in st.session_state:
    st.session_state.index = 0

if "all_urls" not in st.session_state:
    st.session_state.all_urls = get_all_urls()

if "unsorted_urls" not in st.session_state:
    st.session_state.unsorted_urls = list(db.get_collection_contents(CollectionNames.UNSORTED_URLS))

elements = st.session_state.all_urls
if elements:
    current_element = elements[st.session_state.index]
    current_url = current_element['url']


    # Page Content
    st.header("Event Daten Sortieren")
    st.subheader(f"{len(elements)} URLs sind noch unsortiert")
    st.write("""
        Hier wird das Datenset endgültig bereinigt. Wenn die von der GPT API zugeordnete Klasse (EventDetail / EventOverview) 
        falsch ist, muss die URL gelöscht werden. Wenn es korrekt zugeordnet ist können die Daten gespeichert werden. \n 
        **ACHTUNG** Teilweise sind die Daten unvollständig. Das liegt daran, dass das HTML gekürzt wurde, 
        für die Sortierung ist das irrelvant, also auch abgeschnittene Events gehören in die Event-DB.\n
        **Übersichtsseiten müssen Listen von Events enthalten. Eine Seite mit Kategorien oder anderen Links ist keine Übersichtsseite.** 
        """)
    st.info("Es sollen nur deutsche Texte verarbeitet werden. Alle anderen Texte müssen gelöscht werden. (Teilweise englisch ist okay)")
    st.write("")
    try:
        st.write(f"""### Nr. {st.session_state.index} - Aktuelle Seite: \n{current_url} ({[e for e in st.session_state.unsorted_urls if current_element["base_url_id"] == e["_id"]][0]["url_type"]})""")
        st.write(f"""#### Predicted Class: {current_element["class"]}""")
        render_url_content(current_element)
    except Exception as e:
        st.write(f"Fehler: {e}")
        st.write(current_url)
    # Buttons
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

    with col1:
        st.button("Zurück", on_click=prev_element, disabled=(st.session_state.index == 0))
    with col2:
        st.button("Weiter", on_click=next_element, disabled=(st.session_state.index == len(elements) - 1))
    with col3:
        st.button("Als Event-URL speichern", on_click=save_event_url)
    with col4:
        st.button("URL löschen", on_click=remove_url)

else:
    st.write("Es sind aktuell keine Daten in der DB zur Berarbeitung vorhanden.")



