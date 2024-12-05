import urllib
import re
import json
import copy
import datetime
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from pathlib import Path
import spacy
import requests


root_path = Path.cwd()
html_filter = ['header', 'footer', 'svg', 'img', 'nav', 'script']

# check if crawler is allowed to crawl url
def ask_robots(url: str, useragent="*") -> bool:
    try:
        url_parsed = urlparse(url)
        url_robots_txt = url_parsed.scheme + '://' + url_parsed.netloc + '/robots.txt'
        print("robots.txt: ", url_robots_txt)
        robotParse = urllib.robotparser.RobotFileParser()
        robotParse.set_url(url_robots_txt)
        robotParse.read()

        print("Ask access to ", url)
        return robotParse.can_fetch('*', url)
    except Exception as e:
        print("Ask Robots :", e)


def get_disallowed_urls(url, user_agent="*"):
    """
    Gibt alle disallowed URLs für den angegebenen User-Agent aus der robots.txt zurück.

    :param robots_url: Die URL zur robots.txt-Datei (z. B. "https://example.com/robots.txt").
    :param user_agent: Der User-Agent, für den die Regeln geprüft werden (Standard: "*").
    :return: Eine Liste der disallowed URLs.
    """
    # robots.txt Parser initialisieren
    url_parsed = urlparse(url)
    url_robots_txt = url_parsed.scheme + '://' + url_parsed.netloc + '/robots.txt'
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url_robots_txt)
    rp.read()

    # Liste der disallowed Pfade initialisieren
    disallowed_paths = []

    # robots.txt-Datei als Text herunterladen
    response = requests.get(url_robots_txt)
    if response.status_code == 200:
        # Parsen der robots.txt
        lines = response.text.splitlines()
        current_user_agent = None
        for line in lines:
            # Leerzeichen und Kommentare ignorieren
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # User-Agent-Zeilen erkennen
            if line.lower().startswith("user-agent"):
                current_user_agent = line.split(":")[1].strip()

            # Disallow-Regeln erkennen
            elif line.lower().startswith("disallow") and current_user_agent == user_agent:
                disallow_path = line.split(":")[1].strip()
                if disallow_path:
                    disallowed_paths.append(disallow_path)

    # Basis-URL extrahieren
    base_url = url_robots_txt.rsplit("/", 1)[0]

    # Vollständige URLs zurückgeben
    disallowed_urls = [base_url + path for path in disallowed_paths]
    return disallowed_urls


# check if the url matches the regEx pattern, exclude it from crawler if it does
def check_regex(url: str, url_patterns: dict) -> bool:
    for pattern in url_patterns:
        if pattern.match(url):
            return False
    return True


# exclude url if website contains no keyword
def check_keywords(content: str, keywords: dict) -> bool:
    for word in keywords:
        if re.search(word, content, flags=re.IGNORECASE):
            return True
    return False

# get only the content of the page without html tags
def get_page_content(soup: BeautifulSoup):
    soup_temp = copy.copy(soup)
    body = soup_temp.find('body')
    if body is None:
        return
    for tag in html_filter:
        for el in body.find_all(tag):
            el.decompose()
    return prettify_content(body.text)


def prettify_content(content: str):
    return re.sub(r'\n\s*\n', '\n', content)
