import requests
import streamlit.components.v1 as components
from src.crawler.CrawlerV2 import Crawler
from src.persistence.db import *

@st.cache_resource
def init_connection():
    return Database()

def get_all_urls():
    return list(db.get_collection_contents(CollectionNames.UNSORTED_URLS))

def next_element():
    if st.session_state.index < len(elements) - 1:
        st.session_state.index += 1
    st.session_state.visited_urls = None

def prev_element():
    if st.session_state.index > 0:
        st.session_state.index -= 1
    st.session_state.visited_urls = None

def submit_url_input():
    st.session_state.new_url = st.session_state.url_input
    st.session_state.url_input = ""
    new_element = {"url": st.session_state.new_url, "url_type": current_element["url_type"]}
    db.replace_document_by_url(CollectionNames.UNSORTED_URLS, current_element["url"], new_element)

def crawl_url(element, url_type):
    crawler = Crawler(element['url'], url_type)
    return crawler.crawl()

def save_html_content(html_content):
    current_element['content']=html_content
    db.insert_document(CollectionNames.UNSORTED_URLS, current_element)

def render_url_content(element):
    try:
        if "content" in element:
            html_content = element["content"]
        else:
            response = requests.get(element["url"])
            if response.status_code == 200:
                html_content = response.text
                save_html_content(html_content)
            else:
                html_content = "<p>Fehler: Die Seite konnte nicht geladen werden.</p>"
        components.html(html_content, height=400, scrolling=True)
    except Exception as e:
        st.write("Es ist ein Fehler aufgetreten: ", e)

def save_sub_urls_to_element():
    new_element = elements[st.session_state.index]
    new_element["sub_urls"] = list(save_sub_urls)
    db.insert_document(CollectionNames.UNSORTED_URLS, new_element)

def save_event_url():
    result=db.insert_document(CollectionNames.EVENT_URLS, elements[st.session_state.index - 1]),
    result=db.delete_document_by_url(CollectionNames.UNSORTED_URLS, elements[st.session_state.index - 1]['url'])
    st.session_state.all_urls = get_all_urls()

def remove_url():
    result = db.delete_document_by_url(CollectionNames.UNSORTED_URLS, current_element['url']),
    st.session_state.all_urls = get_all_urls()

# Variables
db = init_connection()
if 'index' not in st.session_state:
    st.session_state.index = 0
if "new_url" not in st.session_state:
    st.session_state.new_url = ""
if "all_urls" not in st.session_state:
    st.session_state.all_urls = get_all_urls()

elements = st.session_state.all_urls
current_element = elements[st.session_state.index]
current_url = current_element['url']


# Page Content
st.write(f"{len(elements)} URLs in der Liste")
st.write(f"Nr. {st.session_state.index} - Aktuelle Seite: {current_url}")

render_url_content(current_element)

# Buttons
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

with col1:
    st.button("Zurück", on_click=prev_element, disabled=(st.session_state.index == 0))
with col2:
    st.button("Weiter", on_click=next_element, disabled=(st.session_state.index == len(elements) - 1))
with col3:
    st.button("Als Event-URL speichern", on_click=save_event_url)

with col4:
    st.button("URL löschen", on_click= remove_url)
with col5:
    if st.button("Crawl URL"):
        visited_urls = set(crawl_url(current_element, current_element["url_type"])) - {
            item['url'] for item in elements if 'url' in item
        }

        event_elements = {url for url in visited_urls if "veranstaltung" in url.lower() or "event" in url.lower()}
        st.session_state.visited_urls = visited_urls - event_elements

        # gefundene Event URLs direkt in DB speichern
        save_event_urls = [{"url": url, "url_type": current_element["url_type"]} for url in event_elements]
        db.insert_document_list(CollectionNames.EVENT_URLS, save_event_urls)

        st.write("Saved", len(save_event_urls), "Event Urls")


# Display and mark crawled URLs
sub_urls = set()
if 'visited_urls' in st.session_state and st.session_state.visited_urls:
    sub_urls.update(st.session_state.visited_urls)
if 'sub_urls' in current_element:
    sub_urls.update(set(current_element['sub_urls']))
if sub_urls:
    sub_urls = sub_urls - {item['url'] for item in elements if 'url' in item}
    st.write(len(sub_urls), " Sub URLs:")
    with st.form(key="sort_crawler_urls"):
        # Store checkboxes for each URL
        event_urls = []
        unsorted_urls = []
        delete_urls = []
        for i, crawled_url in enumerate(sub_urls):
            st.write(crawled_url)

            col1, col2, col3 = st.columns(3)
            with col1:
                is_event = st.checkbox("Mark as Event URL", key=f"event_{i}")
            with col2:
                is_unsorted = st.checkbox("Mark as Unsorted URL", key=f"unsorted_{i}")
            with col3:
                delete = st.checkbox ("URL löschen", key=f"delete_{i}")
            # Collect URLs based on checkbox selection
            if is_event:
                event_urls.append(crawled_url)
            if is_unsorted:
                unsorted_urls.append(crawled_url)
            if delete:
                delete_urls.append(crawled_url)

        # Submit button to save changes
        if st.form_submit_button("Submit"):
            # Add URLs to appropriate JSON files based on checkbox selections
            event_elements = []
            unsorted_elements = []
            save_sub_urls = sub_urls
            for url in event_urls:
                new_element = {"url_type": elements[st.session_state.index]["url_type"], "url": url}
                event_elements.append(new_element)
                save_sub_urls.remove(url)
            for url in unsorted_urls:
                new_element = {"url_type": elements[st.session_state.index]["url_type"], "url": url}
                unsorted_elements.append(new_element)
                save_sub_urls.remove(url)
            for url in delete_urls:
                save_sub_urls.remove(url)
            db.insert_document_list(CollectionNames.EVENT_URLS, event_elements)
            db.insert_document_list(CollectionNames.UNSORTED_URLS, unsorted_elements)

            if save_sub_urls:
                save_sub_urls_to_element()
            else:
                remove_url()
                st.write("Seite vollständig verarbeitet. URL wurde gelöscht.")

            st.write("URLs have been processed and saved.")

# Text input to replace URL
st.text_input("Aktuelle URL ersetzen mit:", on_change=submit_url_input, key="url_input")

