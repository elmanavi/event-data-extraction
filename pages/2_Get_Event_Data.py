from src.data_analysis.preprocess_html import get_clean_html, get_clean_text
import streamlit as st
import streamlit.components.v1 as components
from src.crawler.CrawlerV2 import *
import streamlit_nested_layout
from bs4 import BeautifulSoup
from src.data_analysis.gpt_api import classify_text
import random

from src.persistence.db import init_db


@st.cache_resource
def init_connection():
    return init_db()

def get_html(url:str):
    response = requests.get(url)
    if response.status_code >= 400:
        print(f"Skipping {overview_url} with status code {response.status_code}")
        return None
    else:
        return response.content

def process_url(url:str, el):
    try:
        page_content = get_html(url)
        if page_content:
            cleaned_html = get_clean_html(page_content)
            cleaned_text = get_clean_text(cleaned_html)
            gpt_class = classify_text(cleaned_html)
            with st.expander(url):
                st.write("Bereinigtes HTML:")
                with st.container(border=True):
                    components.html(cleaned_html, height=400, scrolling=True)
                st.write(f"GPT Klasse: {gpt_class["class"]}")

            if gpt_class["class"] != "None":
                new_element = {
                    "base_url_id": el["_id"],
                    "base_url": el["url"],
                    "url": url,
                    "html": page_content,
                    "cleaned_html": cleaned_html,
                    "cleaned_text": cleaned_text,
                    "class": gpt_class["class"]
                }
                db.event_urls.insert_one(new_element)
                return new_element
    except Exception as e:
        st.error(f"Es is ein Fehler aufgetreten, die url {url} wird übersprungen\n Fehlermeldung: {e}")


db = init_connection()

suburls_count = 10

# content
st.title("Generieren von Event Daten")
st.write("""
    Hier werden die potentiellen Übersichtsseiten aus unsorted_urls sowie alle Links auf dieser Seite mithilfe der GPT API überprüft und den beiden Klassen **"EventDetail"** und **"EventOverview"** zugeordnet. Die Event Daten werden dann als neues Objekt in event_urls gespeichert.""")
st.info(
    f"Es werden immer nur max. {suburls_count} Suburls der Übersichtsseiten angeschaut, damit die Daten ausgeglichen bleiben")
counter = st.number_input("Wie viele der Urls sollen insgesamt überprüft werden?", step=1)
get_event_data = st.button("Event Daten sammeln")

if get_event_data:
    for i in range(counter):
        el = db.unsorted_urls.find_one({"overview_pages": { "$exists": True, "$ne": [] } , "checked": None})
        print(el)
        if el:
            with st.container(border=True):
                if counter <= 0:
                    break
                st.subheader(f"Daten sammeln für {el["url"]} mit {len(el["overview_pages"])} Übersichtsseiten")
                update_element = el

                for overview_url in el["overview_pages"]:

                    st.info(f"Überprüfe Übersichtsseite: {overview_url}")

                    new_element=process_url(overview_url,el)
                    if new_element:
                            soup = BeautifulSoup(new_element["cleaned_html"],"lxml")
                            links = soup.find_all(["a"])
                            urls = set()
                            with st.expander("Suburls"):
                                try:
                                    for link in links:
                                        href = link["href"]
                                        url = urljoin(overview_url, href)
                                        url = urlparse(url)._replace(query="", fragment="").geturl()
                                        if overview_url != url and check_regex(url, PATTERNS) and str(urlparse(overview_url).scheme)+str(urlparse(overview_url).netloc) != url:
                                            urls.add(url)
                                except:
                                    print("Exception while processing links")
                                if len(urls) > suburls_count:
                                    urls= set(random.sample(list(urls), 10))
                                for url in urls:
                                    new_element = process_url(url, el)
                                if not urls:
                                    st.info("Es wurden keine Eventseiten unter der Übersichtsseite gefunden")
                                    update_element["overview_pages"].remove(overview_url)

                    else:
                        update_element["overview_pages"].remove(overview_url)
                    counter = counter - 1
                    if counter <= 0:
                            break
                new_values = {"$set": {"overview_pages": update_element["overview_pages"], "checked": True }}
                db.unsorted_urls.update_one({"_id": update_element["_id"]}, new_values )





