import requests

# login probably wont work because can have capcha....
# will need to see how ios app does it eventually

""" fan_feed_poll - from https://bandcamp.com/dataist/feed?from=menubar
returns: 
'new_count': int 
'newness': int (timestamp?)
'ok': bool

likely used to check if new stuff is available since the date -- save on a full lookup from a date?
"""
url = 'https://bandcamp.com/fan_feed_poll'
headers = {
    'Cookie': 'identity=7%09nLqA2egVjg7Jz%2BFUeJVefYSVlZVnUJTmVcOkrrgJkc0%3D%09%7B%22id%22%3A4131472792%2C%22ex%22%3A0%7D',
}
data = {'since':'1668873134', 'crumb':'|fan_feed_poll|1668892140|R3dlA3qJO3/hv2Oxb3T+eCEgsiQ='}

r = requests.post(url, headers=headers, data=data)
fan_feed_poll = r.json()

""" collection summary - from https://bandcamp.com/dataist/feed?from=menubar
appears to return all releases owned by user -- 'collection' 
runs on many pags BUT also when you go to your own page after logging in"""
url = 'https://bandcamp.com/api/fan/2/collection_summary'
headers = {
    'Cookie': 'identity=7%09nLqA2egVjg7Jz%2BFUeJVefYSVlZVnUJTmVcOkrrgJkc0%3D%09%7B%22id%22%3A4131472792%2C%22ex%22%3A0%7D',
}
r = requests.post(url, headers=headers)
collection_summary = r.json()
purchased_albums = collection_summary['collection_summary']['tralbum_lookup']

""" wishlist_items - from https://bandcamp.com/dataist"""
url = 'https://bandcamp.com/api/fancollection/1/wishlist_items'
headers = {
    'Cookie': 'identity=7%09nLqA2egVjg7Jz%2BFUeJVefYSVlZVnUJTmVcOkrrgJkc0%3D%09%7B%22id%22%3A4131472792%2C%22ex%22%3A0%7D',
}

data = {'fan_id':'896389', 'older_than_token': '1646418061:357124979:a::', 'count':'20'}

r = requests.post(url, headers=headers, json=data)
wishlist_items = r.json()
# wishlist_items.keys() -> dict_keys(['items', 'more_available', 'item_lookup', 'last_token', 'tracklists', 'purchase_infos', 'co llectors'])

items = wishlist_items['items']
tracklist =  wishlist_items['tracklists'] # contains keys() with each release and URL, durration, and track metadata

# pagnation
if wishlist_items['more_available']:
    older_than_token = wishlist_items['last_token']

item_lookup = wishlist_items['item_lookup'] # contains keys for each track with value of 'item_type':str and 'purchased': bool


""" collection - from https://bandcamp.com/dataist

not sure how this is different from '/collection_summary'"""
url = 'https://bandcamp.com/api/fancollection/1/collection_items'
headers = {
    'Cookie': 'identity=7%09nLqA2egVjg7Jz%2BFUeJVefYSVlZVnUJTmVcOkrrgJkc0%3D%09%7B%22id%22%3A4131472792%2C%22ex%22%3A0%7D',
}

data = {'fan_id':'896389', 'older_than_token': '1646418061:357124979:a::', 'count':'20'}
r = requests.post(url, headers=headers, json=data)
collection_items = r.json()
# collection_items.keys() ->  dict_keys(['items', 'more_available', 'tracklists', 'redownload_urls', 'item_lookup', 'last_token', 'p urchase_infos', 'collectors'])

items = collection_items['items']
tracklists = collection_tracklists['tracklists']

# pagnation
if collection_items['more_available']:
    older_than_token = collection_items['last_token']

item_lookup = collection_items['item_lookup'] # contains keys for each track with value of 'item_type':str and 'purchased': bool

