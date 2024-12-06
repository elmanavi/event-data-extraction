import re
import struct

from src.crawler.CrawlerV2 import Crawler
from src.crawler.crawler_service import *
from src.crawler.maps_api import get_maps_results
from src.crawler.utils.maps_types import MAPS_TYPES
from src.persistence.db import *
import random
from urllib.parse import urlparse
import streamlit_nested_layout


# Schema
# {
#         "url_type": "city",
#         "url": "https://www.Kaiserslautern.de",
#         "meta": {
#             "website_host": "Kaiserslautern",
#             "location": "Kaiserslautern"
#         }
#     },

st.title("Event-Urls-Suche mit Crawler und Google API")

@st.cache_resource
def init_connection():
    return Database()

@st.cache_resource
def init_maps_queries():
    return db.get_collection_contents("maps_search_queries")

def crawl(item):

        results =[]
        try:
            st.info(f"Crawle {item["url"]}")

            if "overview_pages" not in item:
                crawler = Crawler(item["url"], item["url_type"], depth=2)
                results = crawler.crawl()
        except Exception as e:
            st.error(f"Fehler beim crawlen: {e}")
            db.delete_document_by_url(source,item["url"])
            return
        # Übersicht-Seiten erkennen
        overview_regex = re.compile(
            r"^https?:\/\/([a-zA-Z0-9.-]*\/)*(?!(advent))(kalender|.*veranstaltungen|veranstaltungskalender|.*events?|.*event-?kalender|([a-zA-Z]*)?programm|gottesdienste|auff(ü|ue)hrungen|termine|spielplan)(\/?|(\/?[a-zA-Z]*)\.[a-zA-Z]*)?$",
            re.IGNORECASE)
        overview_pages = set()
        # URLs sortieren

        sub_urls=[]
        for url in results:
            if overview_regex.match(url):
                overview_pages.add(url)
            else:
                sub_urls.append(url)
        if not overview_pages:
            overview_regex = re.compile(
                r"^https?:\/\/([a-zA-Z0-9.-]*\/)*(?!(advent))(kalender|.*veranstaltungen|veranstaltungskalender|.*events?|.*event-?kalender|([a-zA-Z]*)?programm|gottesdienste|auff(ü|ue)hrungen|termine|spielplan)(\/?|(\/?[a-zA-Z]*)\.[a-zA-Z]*)?",
                re.IGNORECASE)
            for url in results:
                match = overview_regex.search(url)
                if match:
                    overview_pages.add(match.group())
        overview_pages = {url.casefold() for url in overview_pages}

        with st.expander("Gefundene Suburls"):
            for url in sub_urls:
                st.write(url)
        with st.expander("Gefundene Übersichtsseiten:"):
            for url in overview_pages:
                st.write(url)


        # Update DB entry
        if overview_pages:
            item["overview_pages"] = list(overview_pages)
        if sub_urls:
            item["sub_urls"] = sub_urls
        item["crawled"] = True
        db.insert_or_update_document(source, item)



db = init_connection()
if "maps_queries" not in st.session_state:
    st.session_state.maps_queries = list(db.get_collection_contents(CollectionNames.MAPS_QUERIES))

# content
st.write("""
    Wähle aus für wie viele Urls der **Crawler** gestartert werden soll. Diese werden zufällig aus den noch nicht gecrawlten Urls aus der DB ausgewählt.
    Wenn **"Google Maps Ergebnisse finden"** aktiviert ist, werden bei den Stadtportalen zusätzlich noch neue Veranstaltungsorte gesucht.""")
with st.form("Crawler Settings"):
    source = CollectionNames.UNSORTED_URLS
    count = st.number_input("Wie viele URLs sollen gecrawled werden?", step=1)
    maps = st.checkbox("Google Maps Ergebnisse finden")
    # Every form must have a submit button.
    submitted = st.form_submit_button("Starte Crawler")
    if submitted:
        url_list = list(db.get_collection_contents(source))
        url_list = [
            item for item in url_list
            if 'crawled' not in item or not item['crawled']
        ]
        if not url_list:
            st.success("Alle Urls wurden bereits gecrawled")
        else:
            sampled_items = random.sample(url_list, k=min(count, len(url_list)))
            for item in sampled_items:
                with st.expander(f"Ergebnisse für {item["url"]} in {item["meta"]["location"]}"):

                    if item["url_type"] == "city" and maps:
                        for type_id in random.sample(MAPS_TYPES, 5):
                            print(item)
                            if "maps_searches" not in item or "maps_searches" in item and type_id not in item["maps_searches"]:
                                st.info(f"Suche Maps Ergebnisse für {type_id} in {item["meta"]["location"]}")
                                # maps_results = []
                                maps_results = get_maps_results(type_id, item["meta"]["location"])
                                if maps_results:
                                    new_elements = []
                                    with st.expander("Maps Ergebnisse"):
                                        for result in maps_results:
                                            if "facebook" not in result.website_uri and "instagram" not in result.website_uri and "tiktok" not in result.website_uri:
                                                element = {
                                                    "url_type": type_id,
                                                    "url": result.website_uri,
                                                    "meta":{
                                                        "website_host": result.display_name.text,
                                                        "location": result.formatted_address.split(", ")[1],
                                                        "address": result.formatted_address,
                                                        "maps_types": list(result.types)
                                                    }}
                                                st.write(element["url"])
                                                new_elements.append(element)
                                        if new_elements:
                                            db.insert_url_list(CollectionNames.UNSORTED_URLS, new_elements)


                                if "maps_searches" in item:
                                    maps_searches = item["maps_searches"]
                                    maps_searches.append(type_id)
                                    item["maps_searches"] = maps_searches
                                else:
                                    item["maps_searches"] =  [type_id]
                            else:
                                st.success("Maps Ergebnisse bereits in DB")

                    crawl(item)







