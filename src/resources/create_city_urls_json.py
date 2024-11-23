import json
from pathlib import Path

p = Path(__file__).with_name('city_urls.txt')

urls = []
with p.open('r') as f:
    for line in f:
        l = line.strip()
        a = l.split()
        j = {"url_type": "city_url", "url":a[2]}
        urls.append(j)

urls.pop(0)
with open('unsorted_urls.json', 'w', encoding='utf-8') as f:
    json.dump(urls, f, ensure_ascii=False, indent=4)

