from src.configuration.config import SERP_API_KEY
from serpapi import GoogleSearch

params = {
    "engine": "google_maps",
    "q": "",
    "type": "search",
    "api_key": SERP_API_KEY ,
    "ll": "@49.4540304,11.101698,14z"  # coordinates for Nuremberg with 15 zoom in
}


def get_maps_results(search_keywords ):
    results = []
    for keyword in search_keywords:
        params["q"] = keyword
        search = GoogleSearch(params)
        local_results = search.get_dict()["local_results"]
        for location in local_results:
            if "website" in location and location["website"] not in results:
                results.append(location["website"])
                # print(location["website"])
    return results

