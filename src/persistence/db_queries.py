
import json
from src.persistence.db import *
from pathlib import Path

p = Path(__file__).with_name('city_urls.json"')
db = Database()

def insert_json_file_to_db(file_name, collection_name):
    with open(f"{file_name}.json", 'r', encoding='utf-8') as file:
        elements = json.load(file)
    print(elements)
    db.insert_url_list(collection_name, elements)


insert_json_file_to_db("large_city_urls", CollectionNames.UNSORTED_URLS)






