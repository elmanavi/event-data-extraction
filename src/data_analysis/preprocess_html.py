import json
import os
from bs4 import BeautifulSoup, Comment


def get_clean_html(page_content:str):

    soup = BeautifulSoup(page_content, "lxml")
    body_content = soup.body

    if not body_content:
        print("Kein <body>-Tag im HTML gefunden!")
        return None
    else:
        for tag in body_content.find_all(["footer", "script", "header", "nav", "menu", "img"]):
            tag.decompose()
        for tag in body_content.find_all(True):
            try:
                if any(keyword in str(tag.get('class', [])).lower() for keyword in
                       ['navigation', 'menu', 'nav', 'language']) or \
                        any(keyword in tag.get('id', '').lower() for keyword in
                            ['navigation', 'menu', 'nav', 'language']):
                    tag.decompose()  # Entfernt das Tag und seinen Inhalt
            except Exception as e:
                print(f"{tag.name} {e}")

        # Entfernen von Kommentaren
        for comment in body_content.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Bereinigtes HTML speichern oder verwenden
        cleaned_html = body_content.prettify()
        clean_html_lines = [line for line in cleaned_html.splitlines() if line.strip()]
        cleaned_html = "\n".join(clean_html_lines)
        return cleaned_html

def get_clean_text(cleaned_html:str):
    soup = BeautifulSoup(cleaned_html,"lxml")
    return soup.get_text(separator=' ', strip=True)