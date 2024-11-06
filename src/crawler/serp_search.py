from serpapi import GoogleSearch
from urllib.parse import urlparse
from src.configuration.config import SERP_API_KEY

params = {
    "q": "",
    "location": "Nuremberg, Bavaria, Germany",
    "hl": "en",
    "gl": "us",
    "google_domain": "google.com",
    "api_key": SERP_API_KEY
}

def get_search_results(keywords):
    results = []
    for keyword in keywords:
        params["q"] = keyword + " Veranstaltungen"
        search = GoogleSearch(params)
        organic_results = search.get_dict().get("organic_results")
        if organic_results is not None:
            for result in organic_results:
                append_url = True
                base_url = urlparse(result["link"]).netloc
                for r in results:
                    if  base_url in r.url:
                        append_url = False
                if append_url:
                    results.append( result["link"])
    return results
