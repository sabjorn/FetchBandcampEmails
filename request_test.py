import sys
from time import sleep
import requests
import json
from bs4 import BeautifulSoup

def parse_bandcamp_data(text):
    soup = BeautifulSoup(text, 'html.parser')
    results = soup.findAll("script")
    data = None
    for res in results:
        try:
            data = res["data-tralbum"]
            break
        except:
            pass

    data = json.loads(data)
    track_data = {}
    for track in data["trackinfo"]:
        track_base_url = f"{data['url'].split('.com')[0]}.com"
        track_data = {
            "url": f"{track_base_url}{track['title_link']}",
            "meta": f"{track['track_num']} : {data['artist']} - {track['title']}",
            "img_id": data["art_id"],
            "mp3-128": track["file"]["mp3-128"]
        }
    return track_data


tracks = [];
for line in sys.stdin:
    url = line.strip()
    while True:
        r = requests.get(url)

        if r.status_code == 200:
            try:
                tracks.append(parse_bandcamp_data(r.text))
            except:
                pass
            break

        if r.status_code == 404:
            break
        print(f"status code: {r.status_code}, retrying in 1 second")
        sleep(1)

json_out = json.dumps(tracks)
print(json_out)
