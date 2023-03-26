import requests
from enum import Enum
from dataclasses import dataclass, asdict

@dataclass
class TralbumRequestData:
    band_id: int
    tralbum_id: int
    tralbum_type: str = 't'


def get_tralbum_details(tralbum_details: TralbumRequestData):

    url = "https://bandcamp.com/api/mobile/25/tralbum_details"

    response = requests.request("POST", url, json=asdict(tralbum_details))

    return response.json()

# track_details.keys() -> dict_keys(['id', 'type', 'title', 'bandcamp_url', 'art_id', 'b
# and', 'tralbum_artist', 'package_art', 'featured_track_id', 'tracks',
# 'credits', 'about', 'album_id', 'album_title', 'release_date', 'is_pur
# chasable', 'free_download', 'is_preorder', 'tags', 'currency', 'is_set
# _price', 'price', 'require_email', 'label', 'label_id', 'package_detai
# ls_lite', 'has_digital_download', 'num_downloadable_tracks', 'merch_so
# ld_out', 'streaming_limit'])
if __name__ == "__main__":
    tralbum_request_data = TralbumRequestData(band_id=310533014, tralbum_id=310533014)
    tralbum_details = get_tralbum_details(tralbum_request_data)

    print(tralbum_details)
    
