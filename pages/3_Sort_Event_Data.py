import streamlit.components.v1 as components
from src.persistence.db import *


@st.cache_resource
def init_connection():
    return init_db()

def render_url_content(element):
    with st.container(border=True):
        components.html(element["cleaned_html"] + "<script>window.print = function() {console.log('Drucken ist deaktiviert.');};</script>", height=400, scrolling=True)

def save_event_url():
    result = db.event_urls.update_one({"_id": current_element["_id"]}, { "$set": { "final": True } })

def remove_url():
    result = db.event_urls.delete_one({"_id": current_element["_id"]}),

# Variables
db = init_connection()
current_element = db.event_urls.find_one(filter={"final": None})

if current_element:
    current_url = current_element['url']

    # Page Content
    st.header("Event Daten Sortieren")
    st.subheader(f"{db.event_urls.count_documents({"final":None})} URLs sind noch unsortiert")
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
        st.write(f"""### Aktuelle Seite: \n{current_url} ({db.unsorted_urls.find_one(filter={"_id": current_element["base_url_id"]}, projection={"url_type":1})["url_type"]})""")
        st.write(f"""#### Predicted Class: {current_element["class"]}""")
        render_url_content(current_element)
    except Exception as e:
        st.write(f"Fehler: {e}")
        st.write(current_url)
    # Buttons
    col1, col2= st.columns([1, 1])


    with col1:
        st.button("Als Event-URL speichern", on_click=save_event_url)
    with col2:
        st.button("URL löschen", on_click=remove_url)

else:
    st.write("Es sind aktuell keine Daten in der DB zur Berarbeitung vorhanden.")



