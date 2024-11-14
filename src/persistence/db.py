
from pymongo.mongo_client import MongoClient
import streamlit as st
from enum import Enum

# URI = "mongodb+srv://event_data_extraction_application:J1TRVDBbl4kSaxTD@cluster0.rtcz4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "event_data"

class CollectionNames:
   EVENT_URLS = "event_urls"
   UNSORTED_URLS = "unsorted_urls"

class Database:
   def __init__(self):
      """
      Initialisiert die Verbindung zur MongoDB.
      """
      mongo_secrets = st.secrets["mongo"]
      uri = f"mongodb+srv://{mongo_secrets['username']}:{mongo_secrets['password']}@{mongo_secrets['host']}/?retryWrites=true&w=majority&appName=Cluster0"
      self.client = MongoClient(uri)
      self.db = self.client[DB_NAME]


   def get_collection(self, collection_name):
      """
      Ruft eine Collection aus der Datenbank ab.
      """
      return self.db[collection_name]

   def insert_document(self, collection_name, document):
      """
      Fügt ein Dokument in die angegebene Collection ein.
      """
      collection = self.get_collection(collection_name)
      filter_query = {"url": document["url"]}  # Bedingung für vorhandenes Dokument
      return collection.update_one(filter_query, {"$set": document}, upsert=True)


   def find_documents(self, collection_name, query):
      """
      Findet Dokumente basierend auf einer Abfrage.
      """
      collection = self.get_collection(collection_name)
      return list(collection.find(query))


   def insert_document_list(self, collection_name, document_list):
      """
      Insert Elements to collection or update existing element if url already exists
      """
      collection = self.get_collection(collection_name)
      for dokument in document_list:
         filter_query = {"url": dokument["url"]}  # Bedingung für vorhandenes Dokument

         # Update oder Insert (Upsert-Operation)
         collection.update_one(filter_query, {"$set": dokument}, upsert=True)

   def delete_document_by_url(self, collection_name, url):
      """
      Löscht ein Dokument aus der Collection basierend auf der URL.
      """
      collection = self.get_collection(collection_name)
      result = collection.delete_one({"url": url})
      return result.deleted_count  # Gibt die Anzahl der gelöschten Dokumente zurück (1 oder 0)

   def get_collection_contents(self, collection_name):
      collection = self.get_collection(collection_name)
      return collection.find()

   def replace_document_by_url(self,collection_name, url, replacement):
      collection = self.get_collection(collection_name)
      collection.replace_one({"url": url},replacement)
