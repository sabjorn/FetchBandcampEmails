from dataclasses import dataclass, asdict
import sys
import os
from time import sleep
import argparse
import logging
from typing import Optional
from io import BytesIO

import requests
import json
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TRCK, TDRC, TIT2, TALB, TPE1, TPOS, TCON, TCOM, TPOS, TCOP, COMM, TXXX, APIC

from api.tralbum_details import TralbumRequestData, get_tralbum_details

@dataclass 
class BCPurchase:
    track_id: int
    unit_price: float
    currency: str
    tralbum_type: str # = 't'
    track_url: str
    

def parse_bandcamp_data(text: str) -> list[TralbumRequestData]:
    soup = BeautifulSoup(text, 'html.parser')

    data_band = soup.select_one('script[data-band]')['data-band']
    band_id = json.loads(data_band)['id']

    data_tralbum = soup.select_one('script[data-tralbum]')['data-tralbum']
    trackinfo = json.loads(data_tralbum)['trackinfo']

    track_data = [TralbumRequestData(band_id=band_id, tralbum_id=track['track_id']) for track in trackinfo]
    return track_data

if __name__ == '__main__':
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    parser = argparse.ArgumentParser(description="Takes bandcamp album and track urls and gets metadata")
    parser.add_argument('-i','--input', nargs='+', help='Provide list of urls to process -- use "-" for stdin', required=True)
    parser.add_argument(
        "-o",
        "--outfile",
        help="directory for saving mp3s, default: './'",
        type=str,
        default="./")
    args = parser.parse_args()
    
    if args.outfile != "./":
        os.makedirs(args.outfile, exist_ok=True)

    if args.input and args.input[0] == "-" and len(args.input) == 1:
        logger.info("reading stdin") 
        urls = sys.stdin
    else:
        urls = args.input
    
    # get track data
    tracks = [];
    for line in urls:
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


    track_details = [get_tralbum_details(track) for track in tracks]
    
    @dataclass
    class BCMetadata:
        purchase_data: BCPurchase

        streaming_url: str
        art_id: int

        # used for mp3 metadata
        track_title: str
        album_title: str
        band_name: str
        label: Optional[str]

    # create metadata
    metadata = []
    for track_detail in track_details:
        tracks = track_detail.get('tracks')
        if not tracks:
            logging.error(f"no tracks in: {track_detail['bandcamp_url']}")
            continue
        
        track = tracks[0] # there should only be one
        if not track['has_digital_download']:
            logging.error(f"has no digital download for: {track_detail['bandcamp_url']}")
            continue

        if not track['is_purchasable']:
            logging.error(f"track not purchasable for: {track_detail['bandcamp_url']}")
            continue
        
        purchase_data = {
            'track_id': track['track_id'],
            'unit_price': track['price'],
            'currency': track['currency'],
            'tralbum_type': track['album_id'],
            'track_url': track_detail['bandcamp_url'],
        }
        data = {
            'purchase_data': BCPurchase(**purchase_data),

            'streaming_url': track['streaming_url']['mp3-128'],
            'art_id': track_detail['art_id'],

            'album_title': track_detail['album_title'], 
            'band_name': track['band_name'],
            'track_title': track['title'],
            'label': track['label'],
        }
        bc_metadata = BCMetadata(**data)
        metadata.append(bc_metadata)
    
    # download, annotate, and save files
    for d in metadata:
        output_filename = f"{d.band_name}-{d.track_title}.mp3".replace(" ", "_").replace("/", "-").lower()
        output_filename_full = os.path.join(args.outfile, output_filename)

        if os.path.exists(output_filename_full):
            continue
        
        logger.info(f"downloading: {output_filename}")

        # download image
        r = requests.get(f"https://f4.bcbits.com/img/a{d.art_id}_16.jpg")
        if r.status_code != 200:
            logger.error(f"request for {d.streaming_url} ALBUM_ART failed")
            continue
        album_art = BytesIO(r.content)

        r = requests.get(d.streaming_url)
        
        if r.status_code != 200:
            logger.error(f"request for {d.streaming_url} failed")
            continue

        audio_buffer = BytesIO(r.content)

        audio = MP3()

        audio.add_tags()

        if d.track_title: audio.tags.add(TIT2(encoding=3, text=d.track_title))
        if d.album_title: audio.tags.add(TALB(encoding=3, text=d.album_title))
        if d.band_name: audio.tags.add(TPE1(encoding=3, text=d.band_name))

        audio.tags.add(APIC(
                      encoding=3,
                      mime='image/jpeg',
                      type=3,
                      desc=u'Cover',
                      data=album_art.getvalue()
                    ))

        pruchase_data = asdict(d.purchase_data)
        audio.tags.add(COMM(encoding=3, desc='', lang='XXX', text=[json.dumps(purchase_data)]))

        audio.save(audio_buffer)
   
        try:
            with open(output_filename_full, "wb") as f:
                f.write(audio_buffer.getbuffer())
        except Exception as e:
            logger.exception(e)
            continue

