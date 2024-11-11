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


root_path = Path.cwd()
html_filter = ['header', 'footer', 'svg', 'img', 'nav', 'script']

# load text categorizer model
path_textcat = Path.joinpath(root_path, "blueprints/utils/text_cat_model")
# textcat_nlp = spacy.load(path_textcat)

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

# extract events from content
# def scrape_events(content: str):
#     # only store content from event pages
#     if textcat_nlp(content)._.cats['event'] == 0:
#         return
#     try:
#         events = ask_chatgpt(":".join(("Gib mir alle Events aus dem Text in einem json objekt mit key 'events' mit einem array aus json objekten aus mit den keys name, location, date(yyyy-mm-dd), address, category. Wenn kein Jahr angegeben ist, benutze das Jahr {}. Gebe nur die keys an die im Text Eindeutig identifizierbar sind. Veranstalter und location stimmen nicht immer überein".format(datetime.now().year), content)))
#         events = json.loads(events)
#         result_events = []
#         for event in events['events']:
#             new_event = Event(event_json=event)
#             if new_event.name and new_event.date:
#                 result_events.append(new_event)
#         return result_events
#     except Exception as e:
#         print("scrape Events: ", e)