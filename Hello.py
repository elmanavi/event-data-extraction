import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Willkommen zum Event-Daten-Extraktions-Tool! 👋")
st.write("""
    ## Übersicht über die Seiten:
    - **DB Overview**: Übersicht über die Inhalte in den Tabellen "unsorted_urls" und "event_urls" in der Datenbank.
    - **Get Urls**: Generieren von Start-Urls für die Suche nach Event Daten. Stadtportale und Veranstaltungsorte werden mithilfe der Google Maps Places API gefunden und in unsorted_urls abgelegt.
    - **Get Event Data**: Generieren von fertigen Event Daten für die Analyse. Unsortierte Urls werden mithilfe der GPT API in "EventDetail" und "EventOverview" Seiten klassifiziert und in event_urls abgelegt
    - **Sort Event Data**: Daten aus event_urls können hier nochmal überprüft und aussortiert werden.""")
st.sidebar.success("Wähle eine Seite aus für weitere Aktionen")


