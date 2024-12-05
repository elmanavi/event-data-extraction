import streamlit.components.v1 as components
from src.persistence.db import *
import streamlit as st
import streamlit_nested_layout

@st.cache_resource
def init_connection():
    return Database()

db = init_connection()

event_data = list(db.get_collection_contents(CollectionNames.EVENT_URLS))

for el in event_data:
    with st.expander(el["url"]):
        components.html(el["cleaned_html"], height=400, scrolling=True)
