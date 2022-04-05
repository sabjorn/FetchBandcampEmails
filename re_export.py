import sys
import json

filename = sys.argv[1]
with open(filename) as playlist:
  playlist_json = json.load(playlist)

for track in playlist_json:
  print(track["url"])

