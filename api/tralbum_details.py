import requests

url = "https://bandcamp.com/api/mobile/25/tralbum_details"

payload = {
  "tralbum_type": "a",
  "band_id": 535281330,
  "tralbum_id": 71893326
}

response = requests.request("POST", url, json=payload)
track_details = response.json()

# track_details.keys() -> dict_keys(['id', 'type', 'title', 'bandcamp_url', 'art_id', 'b
# and', 'tralbum_artist', 'package_art', 'featured_track_id', 'tracks',
# 'credits', 'about', 'album_id', 'album_title', 'release_date', 'is_pur
# chasable', 'free_download', 'is_preorder', 'tags', 'currency', 'is_set
# _price', 'price', 'require_email', 'label', 'label_id', 'package_detai
# ls_lite', 'has_digital_download', 'num_downloadable_tracks', 'merch_so
# ld_out', 'streaming_limit'])
