import sys
import requests
from urllib.parse import urljoin
from src.crawler.utils.regEx import patterns
from src.crawler.utils.keywords import KEYWORDS
from src.crawler.crawler_service import *
from urllib.robotparser import RobotFileParser


URL_KEYWORDS = [
    "veranstaltung", "event", "kalendar", "kunst", "kultur",
    "freizeit", "termine", "highlights",
    "happenings", "ausgehen", "aktivitäten", "aktivitaeten", "programm", "agenda",
    "wochenendtipps", "party", "festivals", "konzerte", "bühne", "buehne", "musik",
    "shows", "kino", "theater", "veranstaltungskalender", "ausstellungen",
    "sehenswürdigkeiten", "sehenswuerdigkeiten", "tipps", "feste", "erleben",
    "entdecken"
]

class Crawler:

    sys.path.append("..")
    # filter variables
    keywords = KEYWORDS
    url_patterns = patterns

    def __init__(self, url, url_type):

        self.visited_urls = set()
        self.url_type = url_type
        start_url = url
        # set tupel of url and max depth to crawl
        self.queue = [(start_url, 2)]
        self.domain = urlparse(start_url).netloc
        self.robots = {}

    def crawl(self):
        # Loop through the URLs in the queue until it is empty
        print("Crawler startet...")
        while self.queue:
            try:
                # get the next URL to crawl
                url_tupels = self.queue.pop(0)
                current_url = url_tupels[0]
                depth = url_tupels[1]
                access = ask_robots(current_url, "*")

                # make request
                if access and depth > 0:
                    response = requests.get(current_url)
                    if response.status_code >= 400:
                        print(f"Skipping {current_url} with status code {response.status_code}")
                        continue
                    page_content = response.content

                    # Parse the HTML content and extract links to other pages
                    soup = BeautifulSoup(page_content, "html.parser")
                    urls_to_crawl = self.find_urls(soup, current_url)
                    urls_to_crawl_tupels = []
                    for url in urls_to_crawl:
                        urls_to_crawl_tupels.append((url, depth - 1))

                    # Add the new URLs to the queue and mark the current URL as visited
                    self.queue.extend(urls_to_crawl_tupels)

                    # extract events and store in db
                    content = get_page_content(soup)

                    print(f"Crawled {current_url} and found {len(urls_to_crawl)} new URLs to crawl")
            except Exception as e:
                print("Exception:", e)

            self.visited_urls.add(current_url)
            if current_url in self.queue:
                self.queue.remove(current_url)
        print("Done")
        return self.visited_urls

    def find_urls(self, soup: BeautifulSoup, current_url: str):
        # get all links from page content
        links = soup.find_all("a", href=True)
        content = get_page_content(soup)
        urls_to_crawl = set()
        for link in links:
            href = link["href"]
            url = urljoin(current_url, href)
            url = urlparse(url)._replace(query="", fragment="").geturl()

            # Check if url should be crawled
            if urlparse(url).netloc == self.domain \
                    and url not in self.visited_urls \
                    and check_regex(url, self.url_patterns) \
                    and check_keywords(content, self.keywords) \
                    and url not in self.queue:
                if self.url_type == "city_url":
                    if  any(keyword in url for keyword in URL_KEYWORDS):
                        urls_to_crawl.add(url)
                else:
                    urls_to_crawl.add(url)
        return urls_to_crawl
