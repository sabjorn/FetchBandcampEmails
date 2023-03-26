import sys
from time import sleep
import requests
import json
from bs4 import BeautifulSoup

def parse_bandcamp_data(text):
    soup = BeautifulSoup(text, 'html.parser')

    band_id = json.loads(soup.select_one('script[data-band]')['data-band'])['id']

    trackinfo = json.loads(soup.select_one('script[data-tralbum]')['data-tralbum'])['trackinfo']
    track_data = []
    for track in trackinfo:
        track_data.append({
            "band_id": band_id,
            "tralbum_id": track['track_id'],
            "tralbum_type": 't',
        })
    return track_data


tracks = [];
for line in sys.stdin:
    url = line.strip()
    while True:
        r = requests.get(url)

        if r.status_code == 404:
            break
        
        if r.status_code != 200:
            print(f"status code: {r.status_code}, retrying in 1 second")
            sleep(1)
            continue

        tracks += parse_bandcamp_data(r.text)
        break

json_out = json.dumps(tracks)
print(json_out)
