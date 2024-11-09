import streamlit as st
import requests
import streamlit.components.v1 as components
import json
from src.crawler.Crawler import Crawler

UNSORTED_URLS_PATH = "src/persistence/unsorted_urls.json"
URLS_PATH = "src/persistence/urls.json"

def get_unsorted_urls():
    with open(UNSORTED_URLS_PATH, 'r', encoding='utf-8') as file:
        unsorted_urls = json.load(file)
    return unsorted_urls

def next_element():
    if st.session_state.index < len(elements) - 1:
        st.session_state.index += 1

def prev_element():
    if st.session_state.index > 0:
        st.session_state.index -= 1

def submit_url_input():
    st.session_state.new_url = st.session_state.url_input
    st.session_state.url_input = ""
    replace_element(st.session_state.index, UNSORTED_URLS_PATH, st.session_state.new_url)

def add_element(index, file_path):
    element = elements[index]
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

def crawl_url(element, url_type):
    if "sitemap" in element:
        url = element["sitemap"]
        crawler = Crawler(url, None)
    else:
        url = element["url"]
        crawler = Crawler(url, url_type)
    visited_urls = crawler.crawl()
    st.write(visited_urls)
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

url = elements[st.session_state.index]['url']

# Content
st.write(f"Aktuelle Seite: {url}")

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
    if st.button("Zurück", on_click=prev_element, disabled=(st.session_state.index == 0)):
        pass
with col2:
    if st.button("Weiter", on_click=next_element, disabled=(st.session_state.index == len(elements) - 1)):
        pass
with col3:
    if st.button("URL speichern", on_click=next_element):
        add_element(st.session_state.index - 1, URLS_PATH)
        remove_element(st.session_state.index - 1, UNSORTED_URLS_PATH)
with col4:
    if st.button("URL löschen", on_click=next_element):
        remove_element(st.session_state.index - 1, UNSORTED_URLS_PATH)
with col5:
    if st.button("Crawl URL"):
        crawl_url(elements[st.session_state.index], "city_url")

st.text_input("Aktuelle URL ersetzen mit:", on_change=submit_url_input, key="url_input")




