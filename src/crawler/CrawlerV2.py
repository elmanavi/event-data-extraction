import gzip
import sys

import requests
import httpx
from urllib.parse import urljoin

from src.crawler.utils.regEx import patterns
from src.crawler.utils.keywords import KEYWORDS
from src.crawler.crawler_service import *
from urllib.robotparser import RobotFileParser

URL_KEYWORDS = [
    "veranstaltung", "event", "kalendar", "kunst", "kultur",
    "freizeit", "termine", "highlights",
    "happenings", "ausgehen", "aktivitäten", "aktivitaeten", "programm",
    "wochenendtipps", "party", "festivals", "konzerte", "bühne", "buehne", "musik",
    "shows", "kino", "theater", "veranstaltungskalender", "ausstellungen", "tipps", "feste", "erleben",
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
        # set tupel of url and max depth to crawl
        self.queue = [(url, 2)]
        self.domain = urlparse(url).netloc
        self.sitemaps_urls = crawl_sitemaps(url)
        print(self.url_type)

    def crawl(self):
        # Loop through the URLs in the queue until it is empty
        if self.sitemaps_urls:
            print("Sitemaps Crawler startet...")
            for url in self.sitemaps_urls:

                if self.include_url(url):
                    print("include URL: ", url)
                    self.visited_urls.add(url)

        else:
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
                            if self.include_url(url):
                                urls_to_crawl_tupels.append((url, depth - 1))

                        # Add the new URLs to the queue and mark the current URL as visited
                        self.queue.extend(urls_to_crawl_tupels)

                        # # extract events and store in db
                        # content = get_page_content(soup)

                        print(f"Crawled {current_url} and found {len(urls_to_crawl)} new URLs to crawl")
                    else:
                        print("access denied for ",current_url )
                except Exception as e:
                    print("Exception:", e)

                self.visited_urls.add(current_url)
                if current_url in self.queue:
                    self.queue.remove(current_url)
        print("Done. Found ", len(self.visited_urls), " Urls")
        return self.visited_urls

    def find_urls(self, soup: BeautifulSoup, current_url: str):
        # get all links from page content
        links = soup.find_all("a", href=True)
        urls_to_crawl = set()
        for link in links:
            href = link["href"]
            url = urljoin(current_url, href)
            url = urlparse(url)._replace(query="", fragment="").geturl()
            urls_to_crawl.add(url)
        return urls_to_crawl


    def include_url(self,url):
        if not urlparse(url).netloc.lower() == self.domain.lower():
            print("Other Domain, excluded ", url)
        if url in self.visited_urls:
            print("Already visited ", url)
        if not check_regex(url, self.url_patterns):
            print("RegEx Match, exlcluded ", url)
        if url in self.queue:
            print("Url already in queue")

        if urlparse(url).netloc.lower() == self.domain.lower() \
                and url not in self.visited_urls \
                and check_regex(url, self.url_patterns)\
                and url not in self.queue:
            print("Checking ", url)
            if self.url_type == "city_url":
                if any(keyword in url for keyword in URL_KEYWORDS):
                    print("Found Event URL:", url)
                    return True
            else:
                if ask_robots(url,"*"):
                    response = requests.get(url)
                    if response.status_code >= 400:
                        print(f"Skipping {url} with status code {response.status_code}")
                        return False
                    else:
                        page_content = response.content
                        # Parse the HTML content and extract links to other pages
                        soup = BeautifulSoup(page_content, "html.parser")
                        # remove navigation elements
                        for nav in soup.find_all('nav'):
                            nav.decompose()

                        # Step 2: Remove elements with "navigation" or "menu" in the id or class attributes

                        nav_elements= []
                        nav_elements.extend(soup.find_all(id=re.compile(r'.*navigation.*')))
                        nav_elements.extend(soup.find_all(id=re.compile(r'.*menu.*')))
                        nav_elements.extend(soup.find_all(class_=re.compile(r'.*navigation.*')))
                        nav_elements.extend(soup.find_all(class_=re.compile(r'.*menu.*')))

                        print(len(nav_elements))
                        for elem in nav_elements:
                            if elem:
                                elem.decompose()

                        content = get_page_content(soup)
                        print("searching content for keywords...")
                        if check_keywords(content, self.keywords):
                            print("Found Keyword in ", url)
                            return True
                else:
                    print("access denied")
                    return False
            # if ask_robots(url, "*"):
            #     response = requests.get(url)
            #     if response.status_code >= 400:
            #         print(f"Skipping {url} with status code {response.status_code}")
            #         return False
            #     else:
            #         page_content = response.content
            #         # Parse the HTML content and extract links to other pages
            #         soup = BeautifulSoup(page_content, "html.parser")
            #         content = get_page_content(soup)
            #         print("searching content for keywords...")
            #         if check_keywords(content, self.keywords):
            #             print("Found Keyword in ", url)
            #             return True
            # else:
            #     print("access denied")
            #     return False
        else:
            return False


def crawl_sitemaps(url):
    url_parsed = urlparse(url)
    url_robots_txt = url_parsed.scheme + '://' + url_parsed.netloc + '/robots.txt'
    sitemaps = set()
    urls = set()

    robotParse = urllib.robotparser.RobotFileParser()
    robotParse.set_url(url_robots_txt)
    try:
        robotParse.read()
        robot_sitempaps = robotParse.site_maps()
        if robot_sitempaps:
            sitemaps.update(robot_sitempaps)
        # sitemaps.add(url_parsed.scheme + '://' + url_parsed.netloc + '/sitemap.xml')

        for sitemap in sitemaps:
            print(sitemap)
            urls = get_urls_from_sitemap(sitemap, set())
        print("result", len(urls))
    except Exception as e:
        print("Exception while parsing ", url_robots_txt, ": ", e)
    return urls


def get_urls_from_sitemap(sitemap, urls):
    print("Getting URLs from sitemap:", sitemap)
    try:
        response = httpx.get(sitemap)
        if response.status_code == httpx.codes.OK:
            # Prüfen, ob die Sitemap eine gezippte Datei ist (anhand des Headers oder der Dateiendung)
            content_type = response.headers.get('Content-Type', '')
            if 'gzip' in content_type or sitemap.endswith('.gz'):
                # Falls gezippt, entpacken und lesen
                decompressed_content = gzip.decompress(response.content)
                soup = BeautifulSoup(decompressed_content, 'lxml')
            else:
                # Falls nicht gezippt, direkt parsen
                soup = BeautifulSoup(response.content, 'lxml')

            # URLs aus der Sitemap extrahieren
            locs = soup.find_all("loc")
            for loc in locs:
                url = loc.get_text()
                if "sitemap" in url:
                    # Rekursiv aufrufen, falls es eine Unter-Sitemap ist
                    urls.update(get_urls_from_sitemap(url, urls))
                else:
                    urls.add(url)

    except Exception as e:
        print("Exception while resolving sitemap:", sitemap, "-", e)

    return urls


