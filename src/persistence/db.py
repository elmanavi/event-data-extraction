import streamlit as st
from pymongo import MongoClient


def init_db():
    mongo_secrets = st.secrets["mongo"]
    uri = f"mongodb+srv://{mongo_secrets['username']}:{mongo_secrets['password']}@{mongo_secrets['host']}/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri)
    return client.event_data

class CollectionNames:
   EVENT_URLS = "event_urls"
   UNSORTED_URLS = "unsorted_urls"