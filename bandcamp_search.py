#!/usr/bin/env bash
import sys
import argparse
import logging
import requests
from bs4 import BeautifulSoup


def search(url, max_number=None):
    r = requests.get(url)
    if r.status_code != 200:
        logging.error('status code not 200')
        return []

    soup = BeautifulSoup(r.text, 'html.parser')

    try:
        page_numbers = max([int(num.text) for num in soup.find_all('a', {'class':'pagenum'})])
    except ValueError:
        logging.info('no search matches your selected term')
        return []

    if max_number:
        page_numbers = min(max_number, page_numbers)
    logging.info(f'found {page_numbers} pages')

    releases = []
    for page in range(1, page_numbers + 1):
        logging.info(f'searching page: {page}')
        for search_result in soup.find_all('li', {'class':'searchresult'}):
            page_url = f'{url}&page={page}'
            r = requests.get(page_url)
            soup = BeautifulSoup(r.text, 'html.parser')

            release_url = search_result.find_next('a')['href'].split('?')[0]
            releases.append(release_url)

    return releases


def main(argv):
    parser = argparse.ArgumentParser(description='Searches bandcamp based on search query and retreives all URLs')
    parser.add_argument(
        'search_term',
        help='what you are searching for')
    parser.add_argument(
        '-t',
        '--type',
        choices=['album', 'a', 'track', 't'],
        default='track',
        help='choose type of search')
    parser.add_argument(
        '-p',
        '--pages',
        type=int,
        help='maximum number of pages')
    args = parser.parse_args(argv)

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    search_term = args.search_term.replace(' ', '%20')
    
    search_type = args.type.lower()[0]
    url = f'https://bandcamp.com/search?q={search_term}&item_type={search_type}'
  
    releases = search(url, args.pages)
    for r in releases:
        sys.stdout.write(f"{r}\n")

 
if __name__ == '__main__':
    main(sys.argv[1:])
