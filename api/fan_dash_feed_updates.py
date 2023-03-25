from pprint import pprint as print
import requests

""" notes: 
    * may not be possible to get "new releases from artists I follow" -- there doesn't seem to be an endpoint
"""
""" fan_dash_feed_updates - from https://bandcamp.com/dataist/feed?from=menubar
contains data for 'fan feed' -- aka the collection of stuff bought by people we follow

desktop app can just pull from this to create playlist of new releases
and then users can add to cart/wishlist?"""
url = 'https://bandcamp.com/fan_dash_feed_updates'
headers = {
    'Cookie': 'identity=7%09nLqA2egVjg7Jz%2BFUeJVefYSVlZVnUJTmVcOkrrgJkc0%3D%09%7B%22id%22%3A4131472792%2C%22ex%22%3A0%7D',
}
data = {'fan_id':'896389','older_than':'1668869312'}
r = requests.post(url, headers=headers, data=data)
fan_dash_feed_updates = r.json()
fan_dash_feed_updates.keys() #dict_keys(['ok', 'stories', 'fan_info', 'band_info', 'story_collectors', 'item_lookup'])

ok = fan_dash_feed_updates['ok'] # success/fail -- not necessary?

stories = fan_dash_feed_updates['stories']
stories.keys() # dict_keys(['entries', 'oldest_story_date', 'newest_story_date', 'track_list', 'query_times', 'feed_timestamp'])

oldest_story_date = stories['oldest_story_date']
newest_story_date = stories['newest_story_date']
track_list = stories['track_list'] # list of story tracks with context
entry_info = stories['entries'] # actual track meta with mp3 urls
# 'query_times' -- how long each db query took -- not necessary
# 'feed_timestamp' -- seems empty...

# list of fans that fed this info
fan_info = fan_dash_feed_updates['fan_info']
fan_ids = list(fan_info.keys()) # keys are each fan id -- also contained in fan_info.values()
for info in fan_info.values():
    print(info) 

# not sure what this is for...
band_info = fan_dash_feed_updates['band_info']
band_ids = list(band_info.keys()) # note: band_id also contained in band_info values
for info in band_info.values():
    print(info)

story_collectors = fan_dash_feed_updates['story_collectors'] # dictionary of people who collect each track -- not likely necessary
for track_id, info in story_collectors.items():
    print(track_id)
    for user in info:
        print(user) # note: track_id is available in the user dict


item_lookup = fan_dash_feed_updates['item_lookup'] # single item, not sure what it is for...
