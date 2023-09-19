import requests


def get_tralbum_details(band_id: int):
    url = "https://bandcamp.com/api/mobile/25/band_details"

    response = requests.get(url, params={'band_id': 535281330})

    return response.json()

# track_details.keys() -> dict_keys(['id', 'type', 'title', 'bandcamp_url', 'art_id', 'b
# and', 'tralbum_artist', 'package_art', 'featured_track_id', 'tracks',
# 'credits', 'about', 'album_id', 'album_title', 'release_date', 'is_pur
# chasable', 'free_download', 'is_preorder', 'tags', 'currency', 'is_set
# _price', 'price', 'require_email', 'label', 'label_id', 'package_detai
# ls_lite', 'has_digital_download', 'num_downloadable_tracks', 'merch_so
# ld_out', 'streaming_limit'])
if __name__ == "__main__":
    band_details = get_tralbum_details(band_id=535281330)

    print(band_details)
    
