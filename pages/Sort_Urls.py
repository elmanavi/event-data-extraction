import streamlit as st
import requests
import streamlit.components.v1 as components
import json


def get_unsorted_urls():
    with open('src/persistence/unsorted_urls.json', 'r') as file:
        unsorted_urls = json.load(file)
    return unsorted_urls


def next_element():
    if st.session_state.index < len(elements) - 1:
        st.session_state.index += 1


def prev_element():
    if st.session_state.index > 0:
        st.session_state.index -= 1


def add_element(index, file_path):
    element = elements[index]
    with open(file_path, 'r') as file:
        urls = json.load(file)

    if element not in urls:
        urls.append(element)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=4)


def remove_element(index, file_path):
    with open(file_path, 'r') as file:
        urls = json.load(file)
    urls.pop(index)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(urls, f, ensure_ascii=False, indent=4)


elements = get_unsorted_urls()
if 'index' not in st.session_state:
    st.session_state.index = 0
url = elements[st.session_state.index]['url']

# Content
st.write(f"Aktuelle Seite: {url}")
response = requests.get(url)

if response.status_code == 200:
    html_content = response.text
else:
    html_content = "<p>Fehler: Die Seite konnte nicht geladen werden.</p>"

components.html(html_content, height=600, scrolling=True)


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
        add_element(st.session_state.index - 1, "src/persistence/urls.json")
        remove_element(st.session_state.index - 1, "src/persistence/unsorted_urls.json")
with col4:
    if st.button("URL löschen", on_click=next_element):
        remove_element(st.session_state.index - 1, "src/persistence/unsorted_urls.json")
with col5:
    if st.button("Crawl URL"):
        pass

