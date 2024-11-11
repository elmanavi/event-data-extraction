import streamlit as st
import requests
import streamlit.components.v1 as components
import json
from src.crawler.CrawlerV2 import Crawler

UNSORTED_URLS_PATH = "src/persistence/unsorted_urls.json"
URLS_PATH = "src/persistence/urls.json"


def get_unsorted_urls():
    with open(UNSORTED_URLS_PATH, 'r', encoding='utf-8') as file:
        unsorted_urls = json.load(file)
    return unsorted_urls


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
    replace_element(st.session_state.index, UNSORTED_URLS_PATH, st.session_state.new_url)


def add_element(element, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = json.load(file)

    if element not in urls:
        urls.append(element)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=4)


def remove_element(index, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = json.load(file)
    urls.pop(index)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)


def replace_element(index, file_path, url):
    if url:
        with open(file_path, 'r', encoding="utf-8") as file:
            urls = json.load(file)
        urls[index]['url'] = url
        if 'content' in urls[index]:
            urls[index].pop('content')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=4)

def save_element_list(new_urls, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = json.load(file)
    urls.extend(new_urls)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)


def crawl_url(element, url_type):
    element['crawled'] = True
    with open(UNSORTED_URLS_PATH, 'w', encoding='utf-8') as f:
        json.dump(elements, f, ensure_ascii=False, indent=4)
    crawler = Crawler(element['url'], url_type)
    visited_urls = crawler.crawl()
    return visited_urls


def save_html_content(html_content):
    with open(UNSORTED_URLS_PATH, 'r', encoding='utf-8') as file:
        urls = json.load(file)
        urls[st.session_state.index]["content"] = html_content
    with open(UNSORTED_URLS_PATH, 'w', encoding='utf-8') as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)


elements = get_unsorted_urls()
if 'index' not in st.session_state:
    st.session_state.index = 0
if "new_url" not in st.session_state:
    st.session_state.new_url = ""

current_element = elements[st.session_state.index]
url = elements[st.session_state.index]['url']

# Content
st.write(f"Aktuelle Seite: {url}")
if "crawled" in current_element:
    st.markdown("*Crawled*")

try:
    current_element = elements[st.session_state.index]
    if "content" in current_element:
        html_content = current_element["content"]
    else:
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.text
            save_html_content(html_content)
        else:
            html_content = "<p>Fehler: Die Seite konnte nicht geladen werden.</p>"
    components.html(html_content, height=600, scrolling=True)
except Exception as e:
    st.write("Es ist ein Fehler aufgetreten:")
    st.write(e)

# Buttons
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

with col1:
    st.button("Zurück", on_click=prev_element, disabled=(st.session_state.index == 0))
with col2:
    st.button("Weiter", on_click=next_element, disabled=(st.session_state.index == len(elements) - 1))
with col3:
    st.button("URL speichern", on_click=lambda: [
        add_element(elements[st.session_state.index - 1], URLS_PATH),
        remove_element(st.session_state.index - 1, UNSORTED_URLS_PATH),
    ])
with col4:
    st.button("URL löschen", on_click=lambda: remove_element(st.session_state.index - 1, UNSORTED_URLS_PATH))
with col5:
    if st.button("Crawl URL"):
        visited_urls = crawl_url(elements[st.session_state.index], "city_url")
        st.session_state.visited_urls = visited_urls  # Store crawled URLs in session state

# Display and mark crawled URLs
if 'visited_urls' in st.session_state and st.session_state.visited_urls:
    st.write("Crawled URLs:")
    with st.form(key="sort_crawler_urls"):
        # Store checkboxes for each URL
        event_urls = []
        unsorted_urls = []

        for i, crawled_url in enumerate(st.session_state.visited_urls):
            st.write(crawled_url)

            col1, col2 = st.columns(2)
            with col1:
                is_event = st.checkbox("Mark as Event URL", key=f"event_{i}")
            with col2:
                is_unsorted = st.checkbox("Mark as Unsorted URL", key=f"unsorted_{i}")

            # Collect URLs based on checkbox selection
            if is_event:
                event_urls.append(crawled_url)
            if is_unsorted:
                unsorted_urls.append(crawled_url)

        # Submit button to save changes
        if st.form_submit_button("Submit"):
            # Add URLs to appropriate JSON files based on checkbox selections
            event_elements = []
            unsorted_elements = []
            for url in event_urls:
                new_element = {"city": elements[st.session_state.index]["city"], "url": url}
                event_elements.append(new_element)
            for url in unsorted_urls:
                new_element = {"city": elements[st.session_state.index]["city"], "url": url}
                unsorted_elements.append(new_element)
            save_element_list(event_elements, URLS_PATH)
            save_element_list(unsorted_elements, UNSORTED_URLS_PATH)
            st.write("URLs have been processed and saved.")

# Text input to replace URL
st.text_input("Aktuelle URL ersetzen mit:", on_change=submit_url_input, key="url_input")
