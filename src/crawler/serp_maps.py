from src.configuration.config import SERP_API_KEY
from serpapi import GoogleSearch

# maps type ids
relevant_locations = [
    "art_gallery",
    "auditorium",
    "museum",
    "performing_arts_theater",
    "amphitheatre",
    "amphitheatre",
    "amusement_center",
    "amusement_park",
    "banquet_hall",
    "childrens_camp",
    "comedy_club",
    "community_center",
    "concert_hall",
    "convention_center",
    "cultural_center",
    "dance_hall",
    "event_venue",
    "karaoke",
    "night_club",
    "opera_house",
    "philharmonic_hall",
    "planetarium",
    "library",
    "church",
    "hindu_temple",
    "mosque",
    "synagogue"
]


params = {
    "engine": "google_maps",
    "q": "",
    "type": "search",
    "api_key": SERP_API_KEY ,
    # "ll": "@49.4540304,11.101698,14z"  # coordinates for Nuremberg with 15 zoom in
}


def get_maps_results(search_query ):
    results = []

    params["q"] = search_query
    search = GoogleSearch(params)
    search_dict = search.get_dict()
    if "local_results" not in search_dict:
        return results
    local_results = search_dict["local_results"]

    for location in local_results:
        if "website" in location and location["website"] not in results:

            results.append(location["website"])
    return results


# print(get_maps_results("Konzerte Nuernberg"))