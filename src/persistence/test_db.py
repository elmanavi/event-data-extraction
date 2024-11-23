
import json
from src.persistence.db import *
from pathlib import Path

p = Path(__file__).with_name('unsorted_urls.json"')
db = Database()

with open("unsorted_urls.json", 'r', encoding='utf-8') as file:
    unsorted_urls = json.load(file)

# db.insert_document_list("unsorted_urls",unsorted_urls)


# db.insert_document(
#     CollectionNames.UNSORTED_URLS,
#     {
#         "city": "Moenchengladbach",
#         "url": "https://www.Moenchengladbach.de/"
#     })
# # db.insert_document(
#     CollectionNames.UNSORTED_URLS,
#     {
#         "city": "Moenchengladbach",
#         "url": "https://www.Moenchengladbach.de/",
#         "sub_urls": "https://www.moenchengladbach.de/de/aktuell-aktiv/veranstaltungskalender#page=1&mode=range&start=1731452400&end=*&sort=priority_intS%20desc,%20startTime_doubleS%20asc,%20sortTitle%20asc"
#     })
# db.delete_document_by_url(CollectionNames.UNSORTED_URLS, "https://www.Moenchengladbach.de/")


print(CollectionNames.UNSORTED_URLS)
